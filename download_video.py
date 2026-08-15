import os
import time
import subprocess
import sys

try:
    import yt_dlp
except ImportError:
    print("❌ Biblioteca 'yt-dlp' não encontrada.")
    print("   Instale com: pip install yt-dlp")
    sys.exit(1)


# Atalhos de resolução aceitos na opção de qualidade
RESOLUCOES = {
    "8k": 4320,
    "4k": 2160,
    "2160p": 2160,
    "1440p": 1440,
    "2k": 1440,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
    "240p": 240,
}


def _montar_opcoes_ydl(pasta_saida, qualidade):
    """Monta o dicionário de opções do yt-dlp de acordo com a qualidade escolhida.

    qualidade:
        "melhor"       -> maior resolução de vídeo disponível (inclui 4K/8K)
        "audio"        -> apenas áudio, extraído em MP3
        "1080p", "720p", "480p", "4k", etc. -> limita à altura correspondente
    """
    caminho_saida = os.path.join(pasta_saida, "%(title)s.%(ext)s")

    ydl_opts = {
        'outtmpl': caminho_saida,
        'retries': 10,                  # Tentativas internas de rede do yt-dlp
        'fragment_retries': 10,         # Tentativas em caso de fragmento corrompido
        'socket_timeout': 30,           # Timeout de conexão
        'continuedl': True,             # Retoma downloads parciais
        'noprogress': False,
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web', 'mweb'],
                'skip': ['hls', 'dash'],
            }
        },
    }

    if qualidade == "audio":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        if qualidade == "melhor":
            # Sem restrição de altura/extensão: pega a maior resolução disponível
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            altura = RESOLUCOES.get(qualidade.lower())
            if altura is None:
                # Aceita algo como "1440" sem o "p"
                altura = int(qualidade.replace("p", "").strip())
            ydl_opts['format'] = f'bestvideo[height<={altura}]+bestaudio/best[height<={altura}]'

        # Faz o remux/merge final para mp4 (ffmpeg lida com vp9/av1 em container mp4)
        ydl_opts['merge_output_format'] = 'mp4'

    return ydl_opts


def baixar_video(url, pasta_saida=".", qualidade="melhor", max_tentativas=3):
    """Baixa um vídeo (ou apenas o áudio) do YouTube com resistência a falhas.

    Args:
        url: URL do vídeo do YouTube
        pasta_saida: Pasta onde o vídeo será salvo
        qualidade: "melhor" (maior resolução disponível), "audio" (apenas áudio em MP3),
                   ou uma resolução como "1080p", "720p", "4k", "8k", etc.
        max_tentativas: Número máximo de tentativas em caso de falha

    Returns:
        Caminho do arquivo baixado, ou None em caso de falha
    """
    os.makedirs(pasta_saida, exist_ok=True)

    ydl_opts = _montar_opcoes_ydl(pasta_saida, qualidade)

    tentativa = 1
    tempo_inicio = time.time()

    while tentativa <= max_tentativas:
        try:
            print(f"\n📥 Tentativa {tentativa}/{max_tentativas} — Baixando: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                caminho_final = ydl.prepare_filename(info)

                # Ajusta extensão caso o postprocessor tenha convertido o arquivo
                # (merge para mp4, ou extração de áudio para mp3)
                if not os.path.exists(caminho_final):
                    base, _ = os.path.splitext(caminho_final)
                    extensao_alvo = "mp3" if qualidade == "audio" else "mp4"
                    possivel_arquivo = base + "." + extensao_alvo
                    if os.path.exists(possivel_arquivo):
                        caminho_final = possivel_arquivo

            tempo_decorrido = time.time() - tempo_inicio
            minutos, segundos = divmod(tempo_decorrido, 60)

            print(f"✅ Download concluído: {caminho_final}")
            print(f"⏱️  Tempo total: {int(minutos)}m {segundos:.2f}s")
            return caminho_final

        except yt_dlp.utils.DownloadError as e:
            print(f"❌ Erro de download (tentativa {tentativa}/{max_tentativas}): {e}")
        except yt_dlp.utils.ExtractorError as e:
            print(f"❌ Erro ao extrair informações do vídeo: {e}")
            print("   O vídeo pode ter sido removido, ser privado ou a URL está incorreta.")
            return None
        except KeyboardInterrupt:
            print("\n⚠️  Download interrompido pelo usuário.")
            return None
        except Exception as e:
            print(f"❌ Erro inesperado (tentativa {tentativa}/{max_tentativas}): {e}")

        if tentativa < max_tentativas:
            espera = 2 ** tentativa  # Backoff exponencial: 2s, 4s, 8s...
            print(f"   Aguardando {espera}s antes de tentar novamente...")
            time.sleep(espera)

        tentativa += 1

    print(f"❌ Falha ao baixar o vídeo após {max_tentativas} tentativas: {url}")
    return None


def baixar_multiplos_videos(urls, pasta_saida=".", qualidade="melhor", max_tentativas=3):
    """Baixa múltiplos vídeos, continuando mesmo se algum falhar.

    Args:
        urls: Lista de URLs do YouTube
        pasta_saida: Pasta onde os vídeos serão salvos
        qualidade: Qualidade desejada
        max_tentativas: Tentativas por vídeo

    Returns:
        Tupla (sucesso: list, falhas: list)
    """
    sucesso = []
    falhas = []

    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"Vídeo {i}/{len(urls)}")
        print(f"{'='*60}")

        caminho = baixar_video(url, pasta_saida, qualidade, max_tentativas)

        if caminho:
            sucesso.append((url, caminho))
        else:
            falhas.append(url)

    print(f"\n{'='*60}")
    print(f"Resumo: {len(sucesso)} sucesso(s), {len(falhas)} falha(s)")
    print(f"{'='*60}")

    if falhas:
        print("\n❌ Vídeos que falharam:")
        for url in falhas:
            print(f"   - {url}")

    return sucesso, falhas


def verificar_ffmpeg():
    """Verifica se o ffmpeg está instalado (necessário para merge de áudio/vídeo)."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


if __name__ == "__main__":
    if not verificar_ffmpeg():
        print("⚠️  Aviso: ffmpeg não encontrado. É necessário para juntar áudio/vídeo e extrair áudio em MP3.")
        print("   Instale com: sudo apt install ffmpeg")

    print("Informe os links do YouTube (um por linha).")
    print("Pressione Enter em branco para finalizar a lista.\n")

    urls = []
    while True:
        url = input(f"Link {len(urls) + 1} (ou Enter para finalizar): ").strip()
        if not url:
            break
        urls.append(url)

    if not urls:
        print("❌ Nenhum link informado. Encerrando.")
        sys.exit(1)

    pasta_saida = input("\nPasta de saída (padrão 'downloads'): ").strip() or "downloads"

    print("\nQualidade:")
    print("  melhor -> maior resolução disponível (inclui 4K/8K)")
    print("  8k, 4k, 1440p, 1080p, 720p, 480p, 360p, 240p -> limita à resolução escolhida")
    print("  audio  -> apenas o áudio, extraído em MP3")
    qualidade = input("Escolha (padrão 'melhor'): ").strip().lower() or "melhor"

    if len(urls) == 1:
        baixar_video(urls[0], pasta_saida=pasta_saida, qualidade=qualidade)
    else:
        baixar_multiplos_videos(urls, pasta_saida=pasta_saida, qualidade=qualidade)

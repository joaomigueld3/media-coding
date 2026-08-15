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


def verificar_ffmpeg():
    """Verifica se ffmpeg está instalado (necessário para converter para MP3)."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _montar_opcoes_ydl(pasta_saida, qualidade):
    """Monta o dicionário de opções do yt-dlp para extração de áudio."""
    caminho_saida = os.path.join(pasta_saida, "%(title)s.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': caminho_saida,
        'retries': 10,
        'fragment_retries': 10,
        'socket_timeout': 30,
        'continuedl': True,
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
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': qualidade.replace('k', ''),
        }],
    }

    return ydl_opts


def baixar_audio(url, pasta_saida=".", qualidade="192k", max_tentativas=3):
    """Baixa apenas o áudio de um vídeo do YouTube em MP3 com resistência a falhas.

    Args:
        url: URL do vídeo do YouTube
        pasta_saida: Pasta onde o áudio será salvo
        qualidade: Bitrate do MP3 ("128k", "192k", "256k", "320k", etc.)
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
            print(f"\n🎵 Tentativa {tentativa}/{max_tentativas} — Baixando áudio: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                caminho_final = ydl.prepare_filename(info)

                # Ajusta extensão caso o postprocessor tenha convertido para mp3
                if not os.path.exists(caminho_final):
                    base, _ = os.path.splitext(caminho_final)
                    possivel_mp3 = base + ".mp3"
                    if os.path.exists(possivel_mp3):
                        caminho_final = possivel_mp3

            tempo_decorrido = time.time() - tempo_inicio
            minutos, segundos = divmod(tempo_decorrido, 60)

            # Verifica se o arquivo foi criado e tem tamanho > 0
            if os.path.exists(caminho_final):
                tamanho = os.path.getsize(caminho_final)
                if tamanho > 0:
                    print(f"✅ Áudio baixado com sucesso: {caminho_final}")
                    print(f"   Tamanho: {tamanho / (1024**2):.1f} MB")
                    print(f"⏱️  Tempo total: {int(minutos)}m {segundos:.2f}s")
                    return caminho_final
                else:
                    print(f"⚠️  Aviso: arquivo criado mas está vazio.")
                    os.remove(caminho_final)

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

    print(f"❌ Falha ao baixar o áudio após {max_tentativas} tentativas: {url}")
    return None


def baixar_multiplos_audios(urls, pasta_saida=".", qualidade="192k", max_tentativas=3):
    """Baixa múltiplos áudios, continuando mesmo se algum falhar.

    Args:
        urls: Lista de URLs do YouTube
        pasta_saida: Pasta onde os áudios serão salvos
        qualidade: Qualidade desejada (ex: "192k")
        max_tentativas: Tentativas por áudio

    Returns:
        Tupla (sucesso: list, falhas: list)
    """
    sucesso = []
    falhas = []

    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"Áudio {i}/{len(urls)}")
        print(f"{'='*60}")

        caminho = baixar_audio(url, pasta_saida, qualidade, max_tentativas)

        if caminho:
            sucesso.append((url, caminho))
        else:
            falhas.append(url)

    print(f"\n{'='*60}")
    print(f"Resumo: {len(sucesso)} sucesso(s), {len(falhas)} falha(s)")
    print(f"{'='*60}")

    if falhas:
        print("\n❌ Áudios que falharam:")
        for url in falhas:
            print(f"   - {url}")

    return sucesso, falhas


if __name__ == "__main__":
    if not verificar_ffmpeg():
        print("❌ ffmpeg não encontrado ou não está funcionando.")
        print("   É necessário para converter para MP3.")
        print("   Instale com: sudo apt install ffmpeg")
        sys.exit(1)

    print("=== Baixador de Áudio do YouTube ===\n")
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

    print("\nQualidade do MP3:")
    print("  128k -> qualidade menor, arquivo menor (padrão)")
    print("  192k -> qualidade média")
    print("  256k -> qualidade alta")
    print("  320k -> máxima qualidade")
    qualidade = input("Escolha (padrão '192k'): ").strip() or "192k"

    if not qualidade.endswith("k"):
        qualidade += "k"

    print(f"\nBaixando {len(urls)} áudio(s) com qualidade {qualidade}...\n")

    if len(urls) == 1:
        baixar_audio(urls[0], pasta_saida=pasta_saida, qualidade=qualidade)
    else:
        baixar_multiplos_audios(urls, pasta_saida=pasta_saida, qualidade=qualidade)

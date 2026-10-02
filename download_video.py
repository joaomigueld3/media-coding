import os
import re
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
    "1080": 1080,
    "720p": 720,
    "720": 720,
    "480p": 480,
    "480": 480,
    "360p": 360,
    "360": 360,
    "240p": 240,
    "240": 240,
}


def verificar_ffmpeg():
    """Verifica se o ffmpeg está instalado e acessível no ambiente atual."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def limpar_e_extrair_url(texto):
    """Extrai uma URL limpa de uma string, ignorando títulos, nomes ou caracteres extras."""
    texto = texto.strip()
    match = re.search(r'(https?://[^\s<>"\'`,]+)', texto)
    if match:
        return match.group(1).strip()
    return texto


def parsear_links(entrada):
    """Separa links por vírgula e quebras de linha, limpando e extraindo URLs válidas."""
    if not entrada:
        return []

    itens_brutos = []
    for linha in entrada.splitlines():
        for parte in linha.split(','):
            parte = parte.strip()
            if parte:
                itens_brutos.append(parte)

    links_finais = []
    for item in itens_brutos:
        url_limpa = limpar_e_extrair_url(item)
        if url_limpa and url_limpa not in links_finais:
            links_finais.append(url_limpa)

    return links_finais


def obter_resolucao_video(arquivo):
    """Obtém a resolução (largura x altura) do arquivo de vídeo via ffprobe."""
    if not os.path.exists(arquivo):
        return None, None
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0',
            arquivo
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        partes = res.stdout.strip().split(',')
        if len(partes) == 2:
            return int(partes[0]), int(partes[1])
    except Exception:
        pass
    return None, None


def _montar_opcoes_ydl(pasta_saida, qualidade="1080p"):
    """Monta o dicionário de opções do yt-dlp priorizando alta definição (1080p)."""
    caminho_saida = os.path.join(pasta_saida, "%(title)s.%(ext)s")

    ydl_opts = {
        'outtmpl': caminho_saida,
        'windowsfilenames': True,       # Nomes seguros para Windows e WSL
        'overwrites': True,             # Sobrescreve para substituir versões de baixa qualidade
        'retries': 10,
        'fragment_retries': 10,
        'socket_timeout': 30,
        'continuedl': False,
        'noprogress': False,
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
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
        altura = RESOLUCOES.get(qualidade.lower())
        if altura is None and qualidade != "melhor":
            try:
                altura = int(qualidade.replace("p", "").strip())
            except ValueError:
                altura = 1080

        if qualidade == "melhor":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            ydl_opts['format'] = (
                f'bestvideo[height<={altura}]+bestaudio/'
                f'bestvideo[height<={altura}]+bestaudio/best[height<={altura}]/'
                f'bestvideo+bestaudio/best'
            )

        ydl_opts['merge_output_format'] = 'mp4'

    return ydl_opts


def baixar_video(url, pasta_saida=".", qualidade="1080p", max_tentativas=3):
    """Baixa um vídeo do YouTube em Full HD (1080p sempre que disponível)."""
    if "," in url:
        urls = parsear_links(url)
        sucesso, _ = baixar_multiplos_videos(urls, pasta_saida=pasta_saida, qualidade=qualidade, max_tentativas=max_tentativas)
        return sucesso[0][1] if sucesso else None

    url_limpa = limpar_e_extrair_url(url)
    if url_limpa != url:
        print(f"🔗 Link extraído: {url_limpa}")
        url = url_limpa

    os.makedirs(pasta_saida, exist_ok=True)

    tentativa = 1
    tempo_inicio = time.time()
    ydl_opts = _montar_opcoes_ydl(pasta_saida, qualidade)

    while tentativa <= max_tentativas:
        try:
            print(f"\n📥 Tentativa {tentativa}/{max_tentativas} — Baixando: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                titulo = info.get('title', 'video')
                
                req_formats = info.get('requested_formats')
                res_alvo = "Desconhecida"
                if req_formats:
                    for rf in req_formats:
                        if rf.get('height'):
                            res_alvo = f"{rf.get('width', '?')}x{rf.get('height')} ({rf.get('height')}p)"
                            break
                elif info.get('height'):
                    res_alvo = f"{info.get('width', '?')}x{info.get('height')} ({info.get('height')}p)"

                print(f"🎬 Vídeo: \"{titulo}\"")
                print(f"🎯 Resolução selecionada: {res_alvo}")

                ydl.download([url])
                caminho_final = ydl.prepare_filename(info)

                if not os.path.exists(caminho_final):
                    base, _ = os.path.splitext(caminho_final)
                    extensao_alvo = "mp3" if qualidade == "audio" else "mp4"
                    possivel_arquivo = base + "." + extensao_alvo
                    if os.path.exists(possivel_arquivo):
                        caminho_final = possivel_arquivo

            tempo_decorrido = time.time() - tempo_inicio
            minutos, segundos = divmod(tempo_decorrido, 60)

            tamanho_mb = os.path.getsize(caminho_final) / (1024 * 1024) if os.path.exists(caminho_final) else 0
            largura, altura = obter_resolucao_video(caminho_final)
            str_res = f"{largura}x{altura} ({altura}p)" if altura else "Áudio/N/A"

            print(f"\n✅ Download concluído com sucesso!")
            print(f"📁 Arquivo: {caminho_final}")
            print(f"📐 Resolução confirmada: {str_res}")
            print(f"📦 Tamanho: {tamanho_mb:.1f} MB")
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
            espera = 2 ** tentativa
            print(f"   Aguardando {espera}s antes de tentar novamente...")
            time.sleep(espera)

        tentativa += 1

    print(f"❌ Falha ao baixar o vídeo após {max_tentativas} tentativas: {url}")
    return None


def baixar_multiplos_videos(urls, pasta_saida=".", qualidade="1080p", max_tentativas=3):
    """Baixa múltiplos vídeos em alta resolução."""
    if isinstance(urls, str):
        urls = parsear_links(urls)

    sucesso = []
    falhas = []

    for i, url in enumerate(urls, 1):
        print(f"\n{'='*70}")
        print(f"Vídeo {i}/{len(urls)}")
        print(f"{'='*70}")

        caminho = baixar_video(url, pasta_saida, qualidade, max_tentativas)

        if caminho:
            sucesso.append((url, caminho))
        else:
            falhas.append(url)

    print(f"\n{'='*70}")
    print(f"Resumo: {len(sucesso)} sucesso(s), {len(falhas)} falha(s)")
    print(f"{'='*70}")

    if falhas:
        print("\n❌ Vídeos que falharam:")
        for url in falhas:
            print(f"   - {url}")

    return sucesso, falhas


if __name__ == "__main__":
    if not verificar_ffmpeg():
        print("\n" + "!" * 70)
        print("❌ ERRO CRÍTICO: O FFmpeg NÃO está instalado neste terminal!")
        print("!" * 70)
        print("Para baixar em 1080p (Full HD), o FFmpeg é obrigatório para unir o")
        print("fluxo de vídeo de alta resolução com o áudio.")
        print("\n👉 COMO RESOLVER (Super fácil):")
        print("   Você está no terminal do Windows (Git Bash / PowerShell)?")
        print("   Seu projeto está no WSL Ubuntu, onde o FFmpeg JÁ ESTÁ INSTALADO!")
        print("   Basta rodar adicionando 'wsl' na frente:")
        print("\n      wsl python3 download_video.py")
        print("\n   Ou instale o FFmpeg no Windows:")
        print("      winget install Gyan.FFmpeg\n")
        print("!" * 70 + "\n")
        sys.exit(1)

    urls = []

    if len(sys.argv) > 1:
        linha_args = " ".join(sys.argv[1:])
        urls = parsear_links(linha_args)
        if urls:
            print(f"📋 {len(urls)} link(s) detectado(s) via linha de comando:")
            for lk in urls:
                print(f"  - {lk}")

    if not urls:
        print("=" * 70)
        print("DOWNLOAD DE VÍDEOS EM ALTA DEFINIÇÃO (1080p)")
        print("=" * 70)
        print("Informe os links do YouTube.")
        print("👉 Você pode colar vários links separados por vírgula (,) ou um por linha.")
        print("Pressione Enter em branco para finalizar a lista.\n")

        while True:
            prompt_txt = f"Link {len(urls) + 1} (ou Enter para finalizar): " if urls else "Link(s) (separados por ',' ou linha única): "
            entrada = input(prompt_txt).strip()
            if not entrada:
                break

            links_encontrados = parsear_links(entrada)
            for lk in links_encontrados:
                if lk not in urls:
                    urls.append(lk)
                    print(f"  ✓ Adicionado: {lk}")

    if not urls:
        print("❌ Nenhum link informado. Encerrando.")
        sys.exit(1)

    pasta_saida = input("\nPasta de saída (padrão 'downloads'): ").strip() or "downloads"

    print("\nQualidade:")
    print("  1080p  -> Full HD (padrão recomendado, 1080p sempre que disponível)")
    print("  720p, 480p, 360p, 240p -> limita à resolução escolhida")
    print("  4k, 8k, melhor -> máxima resolução disponível")
    print("  audio  -> apenas o áudio, extraído em MP3")
    qualidade = input("Escolha (padrão '1080p'): ").strip().lower() or "1080p"

    if len(urls) == 1:
        baixar_video(urls[0], pasta_saida=pasta_saida, qualidade=qualidade)
    else:
        baixar_multiplos_videos(urls, pasta_saida=pasta_saida, qualidade=qualidade)
import subprocess
import os
import time
import sys


def verificar_ffmpeg():
    """Verifica se ffmpeg está instalado e acessível."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def validar_entrada(input_file):
    """Valida se o arquivo de entrada existe e é acessível."""
    if not input_file:
        print("❌ Caminho de entrada vazio.")
        return False

    if not os.path.exists(input_file):
        print(f"❌ Arquivo não encontrado: {input_file}")
        return False

    if not os.path.isfile(input_file):
        print(f"❌ Caminho não é um arquivo: {input_file}")
        return False

    if not os.access(input_file, os.R_OK):
        print(f"❌ Permissão negada ao ler: {input_file}")
        return False

    tamanho = os.path.getsize(input_file)
    if tamanho == 0:
        print(f"❌ Arquivo está vazio: {input_file}")
        return False

    print(f"✓ Arquivo validado ({tamanho / (1024**2):.1f} MB)")
    return True


def ajustar_e_validar_saida(output_file, input_file, formato):
    """Ajusta o caminho de saída se for uma pasta e valida permissões.

    Se output_file é uma pasta, gera um nome automático baseado no vídeo de entrada.
    """
    # Se output_file é uma pasta existente ou não tem extensão, gera nome automático
    if os.path.isdir(output_file):
        nome_base = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_file, f"{nome_base}.{formato}")
        print(f"✓ Usando saída: {output_file}")

    pasta = os.path.dirname(output_file) or "."

    if not os.path.exists(pasta):
        try:
            os.makedirs(pasta, exist_ok=True)
            print(f"✓ Pasta criada: {pasta}")
        except Exception as e:
            print(f"❌ Erro ao criar pasta: {e}")
            return None

    if not os.access(pasta, os.W_OK):
        print(f"❌ Permissão negada ao escrever em: {pasta}")
        return None

    if os.path.exists(output_file) and not os.access(output_file, os.W_OK):
        print(f"❌ Permissão negada ao sobrescrever: {output_file}")
        return None

    return output_file


def extrair_audio(input_file, output_file, formato="mp3", qualidade="192k", max_tentativas=3):
    """Extrai o áudio de um vídeo com resistência a falhas.

    Args:
        input_file: Caminho do vídeo de entrada
        output_file: Caminho do arquivo de áudio de saída (já ajustado e validado)
        formato: Formato do áudio ("mp3", "wav", "aac", "m4a", etc.)
        qualidade: Bitrate (ex: "192k", "320k") — ignorado para wav
        max_tentativas: Número máximo de tentativas em caso de falha

    Returns:
        Caminho do arquivo criado, ou None em caso de falha
    """
    # Valida entrada (saída já foi validada no main)
    if not validar_entrada(input_file):
        return None

    tempo_inicio = time.time()
    tentativa = 1

    while tentativa <= max_tentativas:
        try:
            print(f"\n📀 Tentativa {tentativa}/{max_tentativas} — Extraindo áudio de {os.path.basename(input_file)}...")

            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-vn',              # Descarta o vídeo
                '-loglevel', 'warning',
            ]

            if formato.lower() == "wav":
                cmd += ['-acodec', 'pcm_s16le', '-ar', '44100']
            else:
                cmd += ['-b:a', qualidade]

            cmd += ['-y', output_file]  # -y sobrescreve se já existir

            subprocess.run(cmd, check=True, capture_output=False, timeout=3600)

            # Verifica se o arquivo foi criado
            if not os.path.exists(output_file):
                print(f"⚠️  Aviso: arquivo não foi criado, mas ffmpeg não reportou erro.")
                if tentativa < max_tentativas:
                    tentativa += 1
                    espera = 2 ** tentativa
                    print(f"   Aguardando {espera}s antes de tentar novamente...")
                    time.sleep(espera)
                    continue
                return None

            tamanho_saida = os.path.getsize(output_file)
            if tamanho_saida == 0:
                print(f"❌ Arquivo de saída está vazio.")
                os.remove(output_file)
                if tentativa < max_tentativas:
                    tentativa += 1
                    espera = 2 ** tentativa
                    print(f"   Aguardando {espera}s antes de tentar novamente...")
                    time.sleep(espera)
                    continue
                return None

            tempo_decorrido = time.time() - tempo_inicio
            minutos, segundos = divmod(tempo_decorrido, 60)

            print(f"✅ Áudio extraído com sucesso: {output_file}")
            print(f"   Tamanho: {tamanho_saida / (1024**2):.1f} MB")
            print(f"⏱️  Tempo total: {int(minutos)}m {segundos:.2f}s")
            return output_file

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout: extração de áudio demorou muito (tentativa {tentativa}/{max_tentativas})")
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except Exception:
                    pass

        except subprocess.CalledProcessError as e:
            print(f"❌ Erro do ffmpeg (tentativa {tentativa}/{max_tentativas}): {e}")
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except Exception:
                    pass

        except KeyboardInterrupt:
            print("\n⚠️  Extração interrompida pelo usuário.")
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except Exception:
                    pass
            return None

        except Exception as e:
            print(f"❌ Erro inesperado (tentativa {tentativa}/{max_tentativas}): {e}")
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except Exception:
                    pass

        if tentativa < max_tentativas:
            espera = 2 ** tentativa  # Backoff exponencial: 2s, 4s, 8s...
            print(f"   Aguardando {espera}s antes de tentar novamente...")
            time.sleep(espera)

        tentativa += 1

    print(f"❌ Falha ao extrair áudio após {max_tentativas} tentativas.")
    return None


if __name__ == "__main__":
    if not verificar_ffmpeg():
        print("❌ ffmpeg não encontrado ou não está funcionando.")
        print("   Instale com: sudo apt install ffmpeg")
        sys.exit(1)

    print("=== Extrator de Áudio de Vídeo ===\n")

    input_file = input("Caminho do vídeo de entrada: ").strip()
    if not input_file:
        print("❌ Nenhum arquivo informado.")
        sys.exit(1)

    output_file = input("Caminho do áudio de saída (ex: audio.mp3 ou pasta): ").strip()
    if not output_file:
        print("❌ Nenhum arquivo de saída informado.")
        sys.exit(1)

    # Detecta formato pela extensão do arquivo de saída
    if os.path.isdir(output_file):
        # Se é uma pasta, pede o formato
        formato = input("Formato (padrão mp3, ex: mp3, wav, aac, m4a): ").strip().lower() or "mp3"
        print(f"✓ Será salvo em: {output_file}/{os.path.splitext(os.path.basename(input_file))[0]}.{formato}")
    else:
        formato = os.path.splitext(output_file)[1].lstrip(".").lower()
        if not formato:
            formato = "mp3"
            print(f"⚠️  Nenhuma extensão detectada, usando: {formato}")

    # Pede qualidade (ignorado para wav)
    if formato.lower() != "wav":
        qualidade = input("Qualidade do áudio em kbps (padrão 192k, ex: 320k): ").strip() or "192k"
        if not qualidade.endswith("k"):
            qualidade += "k"
    else:
        qualidade = "N/A"
        print("⚠️  Formato WAV: qualidade será PCM 16-bit 44.1kHz (sem perda)")

    # Ajusta output_file se for uma pasta e valida
    output_file = ajustar_e_validar_saida(output_file, input_file, formato)
    if not output_file:
        sys.exit(1)

    print(f"\nResumo:")
    print(f"  Entrada:  {input_file}")
    print(f"  Saída:    {output_file}")
    print(f"  Formato:  {formato.upper()}")
    print(f"  Qualidade: {qualidade}\n")

    resultado = extrair_audio(input_file, output_file, formato=formato, qualidade=qualidade)

    if resultado:
        print(f"\n✅ Concluído com sucesso!")
        sys.exit(0)
    else:
        print(f"\n❌ Falha na extração.")
        sys.exit(1)

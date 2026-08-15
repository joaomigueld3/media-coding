import subprocess
import os
import time
import sys


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


def validar_saida(output_file):
    """Valida se a pasta de saída existe e é gravável."""
    pasta = os.path.dirname(output_file) or "."

    if not os.path.exists(pasta):
        try:
            os.makedirs(pasta, exist_ok=True)
            print(f"✓ Pasta criada: {pasta}")
        except Exception as e:
            print(f"❌ Erro ao criar pasta: {e}")
            return False

    if not os.access(pasta, os.W_OK):
        print(f"❌ Permissão negada ao escrever em: {pasta}")
        return False

    return True


def cortar_audio(input_file, output_file, inicio="00:00:00", duracao=None, fim=None, max_tentativas=3):
    """Corta um trecho de áudio.

    Args:
        input_file: Caminho do áudio de entrada
        output_file: Caminho do áudio de saída
        inicio: Tempo de início (ex: "00:01:30")
        duracao: Duração do corte (ex: "00:05:00") — ignorado se `fim` for fornecido
        fim: Tempo de fim (ex: "00:06:30") — tem prioridade sobre `duracao`
        max_tentativas: Número máximo de tentativas em caso de falha

    Returns:
        Caminho do arquivo criado, ou None em caso de falha
    """
    if not validar_entrada(input_file):
        return None

    if not validar_saida(output_file):
        return None

    # Se fim foi fornecido, ignora duracao
    if fim:
        print(f"Cortando áudio de {inicio} até {fim}...")
    else:
        if not duracao:
            duracao = "00:05:00"
        print(f"Cortando áudio de {inicio} com duração {duracao}...")

    tempo_inicio = time.time()
    tentativa = 1

    while tentativa <= max_tentativas:
        try:
            print(f"\n✂️  Tentativa {tentativa}/{max_tentativas} — Processando áudio...")

            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-ss', inicio,
            ]

            if fim:
                cmd += ['-to', fim]
            else:
                cmd += ['-t', duracao]

            cmd += [
                '-c', 'copy',           # Copia sem re-encodar (mais rápido)
                '-y', output_file       # Sobrescreve se existir
            ]

            subprocess.run(cmd, check=True, capture_output=False)

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

            print(f"✅ Áudio cortado com sucesso: {output_file}")
            print(f"   Tamanho: {tamanho_saida / (1024**2):.1f} MB")
            print(f"⏱️  Tempo total: {int(minutos)}m {segundos:.2f}s")
            return output_file

        except subprocess.CalledProcessError as e:
            print(f"❌ Erro do ffmpeg (tentativa {tentativa}/{max_tentativas}): {e}")
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except Exception:
                    pass

        except KeyboardInterrupt:
            print("\n⚠️  Corte interrompido pelo usuário.")
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

    print(f"❌ Falha ao cortar áudio após {max_tentativas} tentativas.")
    return None


if __name__ == "__main__":
    print("=== Cortador de Áudio ===\n")

    input_file = input("Caminho do áudio de entrada: ").strip()
    if not input_file:
        print("❌ Nenhum arquivo informado.")
        sys.exit(1)

    output_file = input("Caminho do áudio de saída (arquivo ou pasta): ").strip()
    if not output_file:
        print("❌ Nenhum arquivo de saída informado.")
        sys.exit(1)

    # Se output_file é uma pasta, gera nome automático
    if os.path.isdir(output_file):
        nome_base = os.path.splitext(os.path.basename(input_file))[0]
        extensao = os.path.splitext(input_file)[1].lstrip(".")
        output_file = os.path.join(output_file, f"{nome_base}_cortado.{extensao}")
        print(f"✓ Usando saída: {output_file}")

    inicio = input("Tempo de início (padrão 00:00:00, ex: 00:01:30): ").strip() or "00:00:00"

    print("\nEscolha como especificar o corte:")
    print("  1. Por duração (quanto cortar)")
    print("  2. Por tempo final (até quando cortar)")
    opcao = input("Escolha (padrão 1): ").strip() or "1"

    duracao = None
    fim = None

    if opcao == "1":
        duracao = input("Duração do corte (padrão 00:05:00, ex: 00:02:30): ").strip() or "00:05:00"
    elif opcao == "2":
        fim = input("Tempo final (ex: 00:10:00): ").strip()
        if not fim:
            print("❌ Tempo final não pode ser vazio.")
            sys.exit(1)
    else:
        print("❌ Opção inválida, usando duração padrão.")
        duracao = "00:05:00"

    print(f"\nResumo:")
    print(f"  Entrada:  {input_file}")
    print(f"  Saída:    {output_file}")
    print(f"  Início:   {inicio}")
    if fim:
        print(f"  Fim:      {fim}")
    else:
        print(f"  Duração:  {duracao}\n")

    resultado = cortar_audio(input_file, output_file, inicio=inicio, duracao=duracao, fim=fim)

    if resultado:
        print(f"\n✅ Concluído com sucesso!")
        sys.exit(0)
    else:
        print(f"\n❌ Falha ao cortar áudio.")
        sys.exit(1)

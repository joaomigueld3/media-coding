import subprocess
import os
import time

def obter_duracao_video(input_file):
    """Obtém a duração de um vídeo em segundos."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1:nokey=1',
        input_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"❌ Erro ao obter duração: {e}")
        return None

def remover_final(input_file, output_file, duracao_remover):
    """Remove um trecho do final do vídeo.

    Args:
        input_file: Caminho do vídeo original
        output_file: Caminho do vídeo de saída
        duracao_remover: Duração a remover (em segundos ou formato "00:01:30")
    """
    tempo_inicio = time.time()
    print(f"Removendo {duracao_remover} do final do vídeo...")

    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-t', duracao_remover,  # Mantém até o tempo especificado
        '-c', 'copy',           # Copia sem re-processar
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        tempo_decorrido = time.time() - tempo_inicio
        minutos, segundos = divmod(tempo_decorrido, 60)
        print(f"✅ Vídeo processado com sucesso: {output_file}")
        print(f"⏱️  Tempo de execução: {int(minutos)}m {segundos:.2f}s")
    except Exception as e:
        print(f"❌ Erro ao remover trecho: {e}")

def remover_trecho_meio(input_file, output_file, inicio_remover, fim_remover):
    """Remove um trecho do meio do vídeo (junta as partes antes e depois).

    Args:
        input_file: Caminho do vídeo original
        output_file: Caminho do vídeo de saída
        inicio_remover: Tempo de início do trecho a remover (ex: "00:01:00")
        fim_remover: Tempo de fim do trecho a remover (ex: "00:02:00")
    """
    tempo_total = time.time()
    print(f"Removendo trecho entre {inicio_remover} e {fim_remover}...")

    # Criar arquivos temporários
    parte1 = "temp_parte1.mp4"
    parte2 = "temp_parte2.mp4"
    concat_file = "concat_list.txt"

    try:
        # Extrair primeira parte (do início até o início da remoção)
        print("  Extraindo primeira parte...")
        tempo_parte1 = time.time()
        cmd1 = [
            'ffmpeg',
            '-i', input_file,
            '-t', inicio_remover,
            '-c', 'copy',
            parte1
        ]
        subprocess.run(cmd1, check=True)
        tempo_parte1_decorrido = time.time() - tempo_parte1
        print(f"    ✓ Parte 1 concluída em {tempo_parte1_decorrido:.2f}s")

        # Extrair segunda parte (do fim da remoção até o final)
        print("  Extraindo segunda parte...")
        tempo_parte2 = time.time()
        cmd2 = [
            'ffmpeg',
            '-ss', fim_remover,
            '-i', input_file,
            '-c', 'copy',
            parte2
        ]
        subprocess.run(cmd2, check=True)
        tempo_parte2_decorrido = time.time() - tempo_parte2
        print(f"    ✓ Parte 2 concluída em {tempo_parte2_decorrido:.2f}s")

        # Juntar as duas partes
        print("  Juntando partes...")
        tempo_join = time.time()
        with open(concat_file, 'w') as f:
            f.write(f"file '{os.path.abspath(parte1)}'\n")
            f.write(f"file '{os.path.abspath(parte2)}'\n")

        cmd3 = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_file
        ]
        subprocess.run(cmd3, check=True)
        tempo_join_decorrido = time.time() - tempo_join
        print(f"    ✓ Junção concluída em {tempo_join_decorrido:.2f}s")

        tempo_total_decorrido = time.time() - tempo_total
        minutos, segundos = divmod(tempo_total_decorrido, 60)
        print(f"✅ Vídeo processado com sucesso: {output_file}")
        print(f"⏱️  Tempo total: {int(minutos)}m {segundos:.2f}s")

    except Exception as e:
        print(f"❌ Erro ao remover trecho: {e}")
    finally:
        # Limpar arquivos temporários
        for temp_file in [parte1, parte2, concat_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    print("O que você deseja fazer?")
    print("  1. Remover um trecho do final do vídeo")
    print("  2. Remover um trecho do meio do vídeo")
    opcao = input("Escolha (1 ou 2): ").strip()

    input_file = input("Caminho do vídeo de entrada: ").strip()
    output_file = input("Caminho do vídeo de saída: ").strip()

    if opcao == "1":
        duracao_remover = input("Duração a manter, removendo o restante do final (ex: 00:58:00): ").strip()
        remover_final(input_file, output_file, duracao_remover)
    elif opcao == "2":
        inicio_remover = input("Início do trecho a remover (ex: 00:01:00): ").strip()
        fim_remover = input("Fim do trecho a remover (ex: 00:02:00): ").strip()
        remover_trecho_meio(input_file, output_file, inicio_remover, fim_remover)
    else:
        print("❌ Opção inválida.")

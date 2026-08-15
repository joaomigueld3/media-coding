import subprocess

def extrair_amostra(input_file, output_file, inicio="00:00:00", duracao="00:05:00"):
    print(f"Cortando amostra de {duracao} a partir de {inicio}...")
    
    cmd = [
        'ffmpeg',
        '-ss', inicio,        # Ponto de partida
        '-i', input_file,     # Input (colocar após o -ss é mais rápido)
        '-t', duracao,        # Duração do corte
        '-c', 'copy',         # Copia sem re-processar (rápido e mantém qualidade)
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Amostra salva com sucesso: {output_file}")
    except Exception as e:
        print(f"❌ Erro ao cortar vídeo: {e}")

if __name__ == "__main__":
    input_file = input("Caminho do vídeo de entrada: ").strip()
    output_file = input("Caminho do vídeo de saída: ").strip()
    inicio = input("Ponto de início (padrão 00:00:00): ").strip() or "00:00:00"
    duracao = input("Duração do corte (padrão 00:05:00): ").strip() or "00:05:00"

    extrair_amostra(input_file, output_file, inicio=inicio, duracao=duracao)
import os
import subprocess

def extrair_amostra(input_file, output_file, inicio="00:00:00", duracao="00:05:00"):
    print(f"✂️ Cortando amostra ({duracao}) a partir de {inicio}...")
    
    cmd = [
        'ffmpeg', '-y',
        '-ss', inicio,
        '-i', input_file,
        '-t', duracao,
        '-c', 'copy',
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Vídeo salvo em: {output_file}")
    except Exception as e:
        print(f"❌ Erro ao cortar vídeo: {e}")

if __name__ == "__main__":
    PASTA_VIDEOS = "videos"
    os.makedirs(PASTA_VIDEOS, exist_ok=True)

    nome_input = input("Nome do vídeo de entrada (na pasta 'videos/'): ").strip()
    if not nome_input:
        print("❌ Nenhum arquivo de entrada informado.")
        exit(1)

    input_file = os.path.join(PASTA_VIDEOS, nome_input) if not os.path.dirname(nome_input) else nome_input

    # Gera nome de saída padrão automático caso o usuário aperte Enter
    nome_base, ext = os.path.splitext(os.path.basename(input_file))
    ext = ext if ext else ".mp4"
    saida_padrao = f"{nome_base}_corte{ext}"

    nome_output = input(f"Nome do vídeo de saída (padrão '{saida_padrao}'): ").strip()
    if not nome_output:
        nome_output = saida_padrao

    output_file = os.path.join(PASTA_VIDEOS, nome_output) if not os.path.dirname(nome_output) else nome_output

    inicio = input("Ponto de início (padrão 00:00:00): ").strip() or "00:00:00"
    duracao = input("Duração do corte (padrão 00:05:00): ").strip() or "00:05:00"

    extrair_amostra(input_file, output_file, inicio=inicio, duracao=duracao)
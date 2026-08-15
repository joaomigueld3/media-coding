import subprocess
import os

def juntar_videos(video1, video2, output_file):
    """Junta 2 vídeos em um único arquivo.

    Args:
        video1: Caminho do primeiro vídeo
        video2: Caminho do segundo vídeo
        output_file: Caminho do vídeo de saída
    """
    print(f"Juntando vídeos...\n  {video1}\n  {video2}")

    # Criar arquivo de configuração para o demuxer concat do ffmpeg
    concat_file = "concat_list.txt"
    try:
        with open(concat_file, 'w') as f:
            f.write(f"file '{os.path.abspath(video1)}'\n")
            f.write(f"file '{os.path.abspath(video2)}'\n")

        # Usar ffmpeg com demuxer concat (sem re-processar, mantém qualidade)
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',  # Copia sem re-processar (rápido e mantém qualidade)
            output_file
        ]

        subprocess.run(cmd, check=True)
        print(f"✅ Vídeos juntados com sucesso: {output_file}")

    except Exception as e:
        print(f"❌ Erro ao juntar vídeos: {e}")
    finally:
        # Limpar arquivo de configuração
        if os.path.exists(concat_file):
            os.remove(concat_file)

if __name__ == "__main__":
    video1 = input("Caminho do primeiro vídeo: ").strip()
    video2 = input("Caminho do segundo vídeo: ").strip()
    output_file = input("Caminho do vídeo de saída: ").strip()

    juntar_videos(video1, video2, output_file)

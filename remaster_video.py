import os
import sys
import platform
import subprocess
import requests
import zipfile
from tqdm import tqdm
import cv2

# URLs e configurações para os modelos
MODELS = {
    "FSRCNN_x2": "https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x2.pb",
    "EDSR_x2": "https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/EDSR_x2.pb"
}

REALESRGAN_URLS = {
    "Linux": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip",
    "Windows": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip",
    "Darwin": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-macos.zip"
}

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        return
    print(f"Baixando {os.path.basename(dest_path)}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    with open(dest_path, 'wb') as file, tqdm(
            desc=dest_path,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
        for data in response.iter_content(block_size):
            file.write(data)
            bar.update(len(data))

def prepare_realesrgan():
    os_name = platform.system()
    if os_name not in REALESRGAN_URLS:
        print("Sistema operacional não suportado para o Real-ESRGAN executável.")
        sys.exit(1)
    
    url = REALESRGAN_URLS[os_name]
    bin_dir = os.path.join("tools", "realesrgan")
    os.makedirs(bin_dir, exist_ok=True)
    
    executable_name = "realesrgan-ncnn-vulkan"
    if os_name == "Windows":
        executable_name += ".exe"
        
    executable_path = os.path.join(bin_dir, executable_name)
    
    if not os.path.exists(executable_path):
        zip_path = os.path.join(bin_dir, "realesrgan.zip")
        download_file(url, zip_path)
        print("Extraindo Real-ESRGAN...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(bin_dir)
        os.remove(zip_path)
        
        if os_name in ["Linux", "Darwin"]:
            os.chmod(executable_path, 0o755)
            
    return executable_path

def get_fps_and_audio(input_video, audio_path):
    import ffmpeg
    try:
        probe = ffmpeg.probe(input_video)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        fps_str = video_stream['r_frame_rate']
        try:
            num, den = map(int, fps_str.split('/'))
            fps = num / den
        except:
            fps = 30.0
            
        has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])
        if has_audio:
            print("Extraindo áudio original...")
            ffmpeg.input(input_video).output(audio_path, q=0, map='a').overwrite_output().run(quiet=True)
        return fps, has_audio
    except Exception as e:
        print(f"Erro ao analisar vídeo via FFmpeg: {e}")
        return 30.0, False

def remaster_ffmpeg(input_video, output_video):
    print("\nIniciando remasterização via FFmpeg (Filtros Básicos)...")
    import ffmpeg
    try:
        stream = ffmpeg.input(input_video)
        # Upscale usando lanczos, aplica nitidez e reduz ruído levemente
        video = stream.video.filter('scale', 1920, -2, flags='lanczos') \
                            .filter('unsharp', luma_msize_x=5, luma_msize_y=5, luma_amount=1.0) \
                            .filter('hqdn3d', luma_spatial=1.5, chroma_spatial=1.5, luma_tmp=6.0, chroma_tmp=6.0)
        audio = stream.audio
        ffmpeg.output(video, audio, output_video, vcodec='libx264', crf=18, preset='fast', acodec='aac').overwrite_output().run(quiet=True)
        print(f"✅ Sucesso! Vídeo salvo em: {output_video}")
    except ffmpeg.Error as e:
        print(f"Erro no FFmpeg: {e.stderr.decode('utf8')}")

def remaster_opencv(input_video, output_video, model_name="FSRCNN_x2", scale=2):
    print(f"\nIniciando remasterização via OpenCV ({model_name})...")
    model_url = MODELS.get(model_name)
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{model_name}.pb")
    
    download_file(model_url, model_path)
    
    print("Carregando modelo de IA...")
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path)
    
    model_type = model_name.split('_')[0].lower()
    sr.setModel(model_type, scale)
    
    # Usando processamento via CPU (padrão do OpenCV PyPI). 
    # Para usar GPU, compile o OpenCV com CUDA.
        
    temp_audio = "temp_audio.m4a"
    fps, has_audio = get_fps_and_audio(input_video, temp_audio)
    
    cap = cv2.VideoCapture(input_video)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    out_width = width * scale
    out_height = height * scale
    
    temp_video = "temp_video_no_audio.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (out_width, out_height))
    
    print(f"Processando {total_frames} frames (Saída: {out_width}x{out_height})...")
    pbar = tqdm(total=total_frames)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        result = sr.upsample(frame)
        out.write(result)
        pbar.update(1)
        
    pbar.close()
    cap.release()
    out.release()
    
    print("Remuxando áudio e vídeo...")
    import ffmpeg
    try:
        video_stream = ffmpeg.input(temp_video)
        if has_audio:
            audio_stream = ffmpeg.input(temp_audio)
            ffmpeg.output(video_stream, audio_stream, output_video, vcodec='libx264', crf=18, preset='fast', acodec='aac').overwrite_output().run(quiet=True)
            os.remove(temp_audio)
        else:
            ffmpeg.output(video_stream, output_video, vcodec='libx264', crf=18, preset='fast').overwrite_output().run(quiet=True)
        os.remove(temp_video)
        print(f"✅ Sucesso! Vídeo salvo em: {output_video}")
    except Exception as e:
        print(f"Erro ao juntar áudio/vídeo: {e}")

def remaster_realesrgan(input_video, output_video):
    print("\nIniciando remasterização via Real-ESRGAN...")
    exec_path = prepare_realesrgan()
    
    temp_audio = "temp_audio.m4a"
    fps, has_audio = get_fps_and_audio(input_video, temp_audio)
    
    frames_in_dir = "temp_frames_in"
    frames_out_dir = "temp_frames_out"
    os.makedirs(frames_in_dir, exist_ok=True)
    os.makedirs(frames_out_dir, exist_ok=True)
    
    print("Extraindo frames (isso pode levar um tempo)...")
    import ffmpeg
    ffmpeg.input(input_video).output(os.path.join(frames_in_dir, 'frame_%08d.jpg'), qscale=2).overwrite_output().run(quiet=True)
    
    num_frames = len(os.listdir(frames_in_dir))
    print(f"Aplicando Real-ESRGAN em {num_frames} frames (GPU Recomendada!)...")
    
    try:
        # Tenta utilizar o comando ncnn-vulkan
        subprocess.run([exec_path, "-i", frames_in_dir, "-o", frames_out_dir, "-n", "realesr-animevideov3"], check=True)
    except subprocess.CalledProcessError as e:
        print("Erro executando Real-ESRGAN:", e)
        return
        
    print("Montando o vídeo final...")
    try:
        video_input = ffmpeg.input(os.path.join(frames_out_dir, 'frame_%08d.jpg'), framerate=fps)
        if has_audio:
            audio_input = ffmpeg.input(temp_audio)
            ffmpeg.output(video_input, audio_input, output_video, vcodec='libx264', crf=18, preset='fast', acodec='aac').overwrite_output().run(quiet=True)
            os.remove(temp_audio)
        else:
            ffmpeg.output(video_input, output_video, vcodec='libx264', crf=18, preset='fast').overwrite_output().run(quiet=True)
        print(f"✅ Sucesso! Vídeo salvo em: {output_video}")
    except Exception as e:
        print(f"Erro ao juntar frames em vídeo: {e}")
        
    import shutil
    shutil.rmtree(frames_in_dir)
    shutil.rmtree(frames_out_dir)

def main():
    if len(sys.argv) > 1:
        # Modo CLI p/ testes automatizados
        choice = sys.argv[1]
        input_file = sys.argv[2]
        output_file = sys.argv[3]
    else:
        print("="*50)
        print("🎬 REMASTERIZADOR DE VÍDEOS COM IA")
        print("="*50)
        print("Opções de Remasterização:")
        print("1 - FFmpeg Básico (CPU) -> Rápido. Melhora nitidez e upscale.")
        print("2 - FSRCNN x2 (OpenCV) -> Rápido (ML Leve). Bom p/ CPU média.")
        print("3 - EDSR x2 (OpenCV) -> Lento. Alta Qualidade. GPU recomendada.")
        print("4 - Real-ESRGAN x4 (Vulkan) -> Pesado. Qualidade Extrema. Ideal para Colab.")
        
        choice = input("\nEscolha a técnica (1-4): ").strip()
        input_file = input("Caminho do vídeo de entrada: ").strip()
        output_file = input("Caminho do vídeo de saída: ").strip()
        
    if not os.path.exists(input_file):
        print("Arquivo não encontrado!")
        sys.exit(1)
        
    if choice == '1':
        remaster_ffmpeg(input_file, output_file)
    elif choice == '2':
        remaster_opencv(input_file, output_file, model_name="FSRCNN_x2", scale=2)
    elif choice == '3':
        remaster_opencv(input_file, output_file, model_name="EDSR_x2", scale=2)
    elif choice == '4':
        remaster_realesrgan(input_file, output_file)
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()

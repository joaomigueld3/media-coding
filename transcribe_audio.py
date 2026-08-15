import os
import time
import subprocess
import sys


def verificar_ffmpeg():
    """Verifica se ffmpeg está instalado."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def obter_duracao_audio(audio_file):
    """Obtém a duração do áudio em segundos usando ffprobe."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        return float(result.stdout.strip())
    except Exception:
        return None


def verificar_gpu():
    """Verifica se há GPU disponível (CUDA)."""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def validar_entrada(input_file):
    """Valida se o arquivo de entrada existe e é acessível."""
    if not os.path.exists(input_file):
        print(f"❌ Arquivo não encontrado: {input_file}")
        return False

    if not os.path.isfile(input_file):
        print(f"❌ Caminho não é um arquivo: {input_file}")
        return False

    if not os.access(input_file, os.R_OK):
        print(f"❌ Permissão negada ao ler: {input_file}")
        return False

    return True


def detectar_idioma_whisper(audio_file, device="cpu"):
    """Detecta o idioma do áudio usando Whisper."""
    try:
        import whisper
    except ImportError:
        return None

    try:
        print("🔍 Detectando idioma do áudio (isso pode levar alguns segundos)...")
        model = whisper.load_model("base", device=device)
        audio = whisper.load_audio(audio_file)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        _, probs = model.detect_language(mel)
        idioma_code = max(probs, key=probs.get)

        return idioma_code
    except Exception as e:
        print(f"⚠️  Não consegui detectar o idioma: {e}")
        return None


def selecionar_idioma():
    """Permite selecionar o idioma manualmente."""
    idiomas = {
        "pt": "Português (Brasil/Portugal)",
        "en": "English (Inglês)",
        "es": "Español (Espanhol)",
        "fr": "Français (Francês)",
        "de": "Deutsch (Alemão)",
        "it": "Italiano",
        "ja": "日本語 (Japonês)",
        "zh": "中文 (Chinês)",
        "ru": "Русский (Russo)",
        "auto": "Auto-detectar (deixar Whisper decidir)",
    }

    print("\n" + "="*70)
    print("IDIOMAS SUPORTADOS")
    print("="*70)

    for i, (codigo, nome) in enumerate(idiomas.items(), 1):
        print(f"[{codigo}] {nome}")

    while True:
        idioma = input("\nEscolha o idioma (padrão 'auto'): ").strip().lower() or "auto"
        if idioma in idiomas:
            print(f"✓ Idioma selecionado: {idiomas[idioma]}")
            return idioma if idioma != "auto" else None
        else:
            print("❌ Código de idioma inválido. Tente novamente.")



def exibir_ferramentas():
    """Exibe as opções de ferramentas com estimativas."""
    print("\n" + "="*70)
    print("OPÇÕES DE TRANSCRIÇÃO")
    print("="*70)

    ferramentas = {
        "1": {
            "nome": "Whisper Large (OpenAI)",
            "velocidade": "Lenta (0.5x em CPU, 2x em GPU)",
            "precisao": "Excelente (95%+)",
            "ram": "6-8 GB",
            "gpu": "Recomendada (NVIDIA)",
            "requisitos": "pip install openai-whisper",
            "vantagens": "Melhor precisão, suporta múltiplos idiomas",
            "desvantagens": "Mais lenta, consome mais memória",
        },
        "2": {
            "nome": "Whisper Base (OpenAI)",
            "velocidade": "Rápida (2x em CPU, 5x em GPU)",
            "precisao": "Boa (90%+)",
            "ram": "2-3 GB",
            "gpu": "Opcional",
            "requisitos": "pip install openai-whisper",
            "vantagens": "Bom equilíbrio velocidade/precisão",
            "desvantagens": "Um pouco menos preciso que Large",
        },
        "3": {
            "nome": "Faster-Whisper (CTransformers)",
            "velocidade": "Muito rápida (5-10x em CPU, 10-20x em GPU)",
            "precisao": "Boa (90%+)",
            "ram": "1-2 GB",
            "gpu": "Opcional (muito mais rápido com GPU)",
            "requisitos": "pip install faster-whisper",
            "vantagens": "Muito rápido, pouca memória, ótima performance",
            "desvantagens": "Um pouco menos preciso que Whisper original",
        },
        "4": {
            "nome": "Google Speech-to-Text (SpeechRecognition)",
            "velocidade": "Muito rápida (em tempo real)",
            "precisao": "Excelente (95%+)",
            "ram": "Mínimo (<1 GB)",
            "gpu": "Não necessário",
            "requisitos": "pip install SpeechRecognition pydub",
            "vantagens": "Muito rápido, online, altamente preciso",
            "desvantagens": "Requer internet, limite de requisições",
        },
    }

    for chave, dados in ferramentas.items():
        print(f"\n[{chave}] {dados['nome']}")
        print(f"    Velocidade:    {dados['velocidade']}")
        print(f"    Precisão:      {dados['precisao']}")
        print(f"    RAM:           {dados['ram']}")
        print(f"    GPU:           {dados['gpu']}")
        print(f"    Vantagens:     {dados['vantagens']}")
        print(f"    Desvantagens:  {dados['desvantagens']}")

    return ferramentas


def estimar_tempo_transcricao(duracao_segundos, ferramenta, tem_gpu):
    """Estima o tempo de transcrição baseado na duração e ferramenta."""
    if duracao_segundos is None:
        return None, None

    duracao_minutos = duracao_segundos / 60

    if ferramenta == "1":  # Whisper Large
        if tem_gpu:
            tempo_estimado = duracao_minutos * 0.5  # 0.5x em GPU
        else:
            tempo_estimado = duracao_minutos * 0.3  # 0.3x em CPU
    elif ferramenta == "2":  # Whisper Base
        if tem_gpu:
            tempo_estimado = duracao_minutos * 0.2  # 0.2x em GPU
        else:
            tempo_estimado = duracao_minutos * 0.1  # 0.1x em CPU
    elif ferramenta == "3":  # Faster-Whisper
        if tem_gpu:
            tempo_estimado = duracao_minutos * 0.05  # 10-20x mais rápido em GPU
        else:
            tempo_estimado = duracao_minutos * 0.1  # 5-10x mais rápido em CPU
    elif ferramenta == "4":  # Google Speech-to-Text
        tempo_estimado = duracao_minutos * 0.05  # ~3 segundos de processing
    else:
        return None, None

    minutos, segundos = divmod(int(tempo_estimado * 60), 60)
    return f"{minutos}m {segundos}s", tempo_estimado


def transcricao_faster_whisper(audio_file, output_file, model="base", device="auto", language=None):
    """Transcreve usando Faster-Whisper (muito mais rápido)."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("❌ Faster-Whisper não está instalado.")
        print("   Instale com: pip install faster-whisper")
        return None

    print(f"📥 Carregando modelo Faster-Whisper {model}...")
    try:
        if device == "cuda":
            device = "cuda"
            compute_type = "float16"
        else:
            device = "cpu"
            compute_type = "int8"

        model_obj = WhisperModel(model, device=device, compute_type=compute_type)
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return None

    tempo_inicio = time.time()
    print(f"🎤 Transcrevendo com Faster-Whisper {model}...")

    try:
        segments, info = model_obj.transcribe(audio_file, language=language)
        texto = "\n".join([segment.text for segment in segments])

        # Salva o resultado
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texto)

        tempo_decorrido = time.time() - tempo_inicio
        minutos, segundos = divmod(tempo_decorrido, 60)

        print(f"✅ Transcrição concluída com sucesso!")
        print(f"   Arquivo: {output_file}")
        print(f"⏱️  Tempo: {int(minutos)}m {segundos:.2f}s")
        return output_file

    except Exception as e:
        print(f"❌ Erro durante a transcrição: {e}")
        return None


def transcricao_whisper(audio_file, output_file, model="base", device="auto", language=None):
    """Transcreve usando Whisper (OpenAI)."""
    try:
        import whisper
    except ImportError:
        print("❌ Whisper não está instalado.")
        print("   Instale com: pip install openai-whisper")
        return None

    print(f"📥 Carregando modelo Whisper {model}...")
    try:
        model_obj = whisper.load_model(model, device=device)
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return None

    tempo_inicio = time.time()
    print(f"🎤 Transcrevendo com Whisper {model}...")

    try:
        resultado = model_obj.transcribe(audio_file, language=language)
        texto = resultado['text']

        # Salva o resultado
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texto)

        tempo_decorrido = time.time() - tempo_inicio
        minutos, segundos = divmod(tempo_decorrido, 60)

        print(f"✅ Transcrição concluída com sucesso!")
        print(f"   Arquivo: {output_file}")
        print(f"⏱️  Tempo: {int(minutos)}m {segundos:.2f}s")
        return output_file

    except Exception as e:
        print(f"❌ Erro durante a transcrição: {e}")
        return None


def transcricao_google(audio_file, output_file, language=None):
    """Transcreve usando Google Speech-to-Text (via SpeechRecognition)."""
    try:
        import speech_recognition as sr
    except ImportError:
        print("❌ SpeechRecognition não está instalado.")
        print("   Instale com: pip install SpeechRecognition pydub")
        return None

    # Mapeia código de idioma Whisper para Google Speech Recognition
    mapa_idiomas = {
        "pt": "pt-BR",
        "en": "en-US",
        "es": "es-ES",
        "fr": "fr-FR",
        "de": "de-DE",
        "it": "it-IT",
        "ja": "ja-JP",
        "zh": "zh-CN",
        "ru": "ru-RU",
    }

    idioma_google = mapa_idiomas.get(language, "en-US") if language else None

    tempo_inicio = time.time()
    print(f"🎤 Transcrevendo com Google Speech-to-Text...")

    try:
        recognizer = sr.Recognizer()

        # Carrega o áudio
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        # Transcreve usando Google Speech Recognition (online)
        print("   Enviando áudio para Google... (requer internet)")
        try:
            if idioma_google:
                texto = recognizer.recognize_google(audio, language=idioma_google)
            else:
                texto = recognizer.recognize_google(audio)  # Auto-detecta
        except sr.UnknownValueError:
            if idioma_google:
                texto = recognizer.recognize_google(audio, language="en-US")  # Tenta em inglês
            else:
                texto = recognizer.recognize_google(audio)

        # Salva o resultado
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(texto)

        tempo_decorrido = time.time() - tempo_inicio
        minutos, segundos = divmod(tempo_decorrido, 60)

        print(f"✅ Transcrição concluída com sucesso!")
        print(f"   Arquivo: {output_file}")
        print(f"⏱️  Tempo: {int(minutos)}m {segundos:.2f}s")
        return output_file

    except sr.RequestError as e:
        print(f"❌ Erro de conexão com Google API: {e}")
        return None
    except sr.UnknownValueError:
        print(f"❌ Áudio não reconhecido. Tente com outra ferramenta.")
        return None
    except Exception as e:
        print(f"❌ Erro durante a transcrição: {e}")
        return None


if __name__ == "__main__":
    if not verificar_ffmpeg():
        print("❌ ffmpeg não encontrado. Instale com: sudo apt install ffmpeg")
        sys.exit(1)

    print("="*70)
    print("TRANSCRIÇÃO DE ÁUDIO")
    print("="*70 + "\n")

    # Pede o arquivo de entrada
    input_file = input("Caminho do áudio de entrada: ").strip()
    if not input_file or not validar_entrada(input_file):
        sys.exit(1)

    # Obtém duração do áudio
    duracao = obter_duracao_audio(input_file)
    if duracao:
        minutos, segundos = divmod(int(duracao), 60)
        print(f"✓ Duração do áudio: {minutos}m {segundos}s")
    else:
        print("⚠️  Não consegui obter a duração do áudio.")

    # Verifica GPU
    tem_gpu = verificar_gpu()
    if tem_gpu:
        print("✓ GPU (CUDA) detectada")
    else:
        print("⚠️  Nenhuma GPU detectada, usando CPU")

    # Exibe opções e estimativas
    ferramentas = exibir_ferramentas()

    print("\n" + "="*70)
    print("ESTIMATIVAS DE TEMPO E RECURSOS")
    print("="*70)

    for chave in ["1", "2", "3", "4"]:
        tempo_est, _ = estimar_tempo_transcricao(duracao, chave, tem_gpu)
        if tempo_est:
            print(f"[{chave}] Tempo estimado: {tempo_est}")

    print("\n" + "="*70)

    # Pede seleção
    opcao = input("\nEscolha a ferramenta (1, 2, 3 ou 4): ").strip()

    if opcao not in ["1", "2", "3", "4"]:
        print("❌ Opção inválida.")
        sys.exit(1)

    # Detecta ou pergunta o idioma
    print("\n" + "="*70)
    print("CONFIGURAÇÃO DE IDIOMA")
    print("="*70)

    opcao_idioma = input("\nDeseja [D]etectar automaticamente ou [E]scolher manualmente? (padrão D): ").strip().upper() or "D"

    idioma = None
    if opcao_idioma == "E":
        idioma = selecionar_idioma()
    elif opcao_idioma == "D":
        # Tenta detectar apenas com Whisper (não com Google)
        if opcao in ["1", "2", "3"]:
            idioma = detectar_idioma_whisper(input_file, device="cuda" if tem_gpu else "cpu")
            if idioma:
                idiomas_nomes = {
                    "pt": "Português",
                    "en": "English",
                    "es": "Español",
                    "fr": "Français",
                    "de": "Deutsch",
                    "it": "Italiano",
                    "ja": "日本語",
                    "zh": "中文",
                    "ru": "Русский",
                }
                print(f"✓ Idioma detectado: {idiomas_nomes.get(idioma, idioma)}")
            else:
                print("⚠️  Deixando Whisper auto-detectar o idioma...")
                idioma = None
        else:
            print("ℹ️  Google Speech-to-Text detecta automaticamente.")
            idioma = None

    # Define nome de saída
    output_file = input("\nCaminho do arquivo de saída (padrão: transcricao.txt): ").strip() or "transcricao.txt"

    # Executa transcrição
    print(f"\n{'='*70}")
    print(f"Ferramenta: {ferramentas[opcao]['nome']}")
    print(f"Entrada:    {input_file}")
    print(f"Saída:      {output_file}")
    if idioma:
        print(f"Idioma:     {idioma}")
    print(f"{'='*70}\n")

    if opcao == "1":
        resultado = transcricao_whisper(input_file, output_file, model="large", device="cuda" if tem_gpu else "cpu", language=idioma)
    elif opcao == "2":
        resultado = transcricao_whisper(input_file, output_file, model="base", device="cuda" if tem_gpu else "cpu", language=idioma)
    elif opcao == "3":
        resultado = transcricao_faster_whisper(input_file, output_file, model="base", device="cuda" if tem_gpu else "cpu", language=idioma)
    elif opcao == "4":
        resultado = transcricao_google(input_file, output_file, language=idioma)

    if resultado:
        print(f"\n✅ Concluído com sucesso!")
        sys.exit(0)
    else:
        print(f"\n❌ Falha na transcrição.")
        sys.exit(1)

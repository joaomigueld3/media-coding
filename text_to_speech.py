import os
import time
import sys


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


def exibir_ferramentas():
    """Exibe as opções de ferramentas de síntese de voz."""
    print("\n" + "="*70)
    print("OPÇÕES DE TEXT-TO-SPEECH")
    print("="*70)

    ferramentas = {
        "1": {
            "nome": "Google Text-to-Speech (gTTS)",
            "velocidade": "Rápida (segundos a minutos)",
            "qualidade": "Excelente (natural)",
            "voz": "Natural, múltiplas vozes",
            "requisitos": "pip install gtts",
            "vantagens": "Vozes muito naturais, várias vozes por idioma, online",
            "desvantagens": "Requer internet, limite de requisições",
            "idiomas": "100+",
        },
        "2": {
            "nome": "pyttsx3 (Offline)",
            "velocidade": "Rápida (segundos)",
            "qualidade": "Boa (robótica)",
            "voz": "Sintética, local",
            "requisitos": "pip install pyttsx3",
            "vantagens": "Completamente offline, sem limite, customizável",
            "desvantagens": "Vozes menos naturais, menos idiomas",
            "idiomas": "~40",
        },
        "3": {
            "nome": "Edge TTS (Microsoft)",
            "velocidade": "Rápida (segundos a minutos)",
            "qualidade": "Muito boa (natural)",
            "voz": "Natural, muitas vozes",
            "requisitos": "pip install edge-tts",
            "vantagens": "Vozes muito boas, grátis, múltiplas vozes",
            "desvantagens": "Requer internet",
            "idiomas": "100+",
        },
        "4": {
            "nome": "Faster-Whisper TTS (Local)",
            "velocidade": "Lenta (minutos)",
            "qualidade": "Muito boa (natural)",
            "voz": "Natural, treináveis",
            "requisitos": "pip install TTS",
            "vantagens": "Offline, vozes customizáveis, open-source",
            "desvantagens": "Mais lento, requer download de modelo (~1GB)",
            "idiomas": "10+",
        },
    }

    for chave, dados in ferramentas.items():
        print(f"\n[{chave}] {dados['nome']}")
        print(f"    Velocidade:    {dados['velocidade']}")
        print(f"    Qualidade:     {dados['qualidade']}")
        print(f"    Voz:           {dados['voz']}")
        print(f"    Idiomas:       {dados['idiomas']}")
        print(f"    Vantagens:     {dados['vantagens']}")
        print(f"    Desvantagens:  {dados['desvantagens']}")

    return ferramentas


def selecionar_idioma():
    """Permite selecionar o idioma da síntese de voz."""
    idiomas = {
        "pt": "Português (Brasil)",
        "pt-PT": "Português (Portugal)",
        "en": "English (US)",
        "en-GB": "English (UK)",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
        "ja": "日本語",
        "zh": "中文",
        "ru": "Русский",
        "ko": "한국어",
    }

    print("\n" + "="*70)
    print("IDIOMAS SUPORTADOS")
    print("="*70)

    for codigo, nome in idiomas.items():
        print(f"[{codigo}] {nome}")

    while True:
        idioma = input("\nEscolha o idioma (padrão 'pt'): ").strip().lower() or "pt"
        if idioma in idiomas:
            print(f"✓ Idioma: {idiomas[idioma]}")
            return idioma
        else:
            print("❌ Código de idioma inválido. Tente novamente.")


def tts_gtts(texto, output_file, idioma):
    """Síntese de voz usando Google Text-to-Speech."""
    try:
        from gtts import gTTS
    except ImportError:
        print("❌ gTTS não está instalado.")
        print("   Instale com: pip install gtts")
        return False

    print(f"🔊 Convertendo texto para fala com gTTS ({idioma})...")
    tempo_inicio = time.time()

    try:
        tts = gTTS(text=texto, lang=idioma, slow=False)
        tts.save(output_file)

        tempo_decorrido = time.time() - tempo_inicio
        minutos, segundos = divmod(tempo_decorrido, 60)

        print(f"✅ Síntese concluída: {output_file}")
        print(f"⏱️  Tempo: {int(minutos)}m {segundos:.2f}s")
        return True

    except Exception as e:
        print(f"❌ Erro durante a síntese: {e}")
        return False


def tts_pyttsx3(texto, output_file, idioma):
    """Síntese de voz usando pyttsx3 (offline)."""
    try:
        import pyttsx3
    except ImportError:
        print("❌ pyttsx3 não está instalado.")
        print("   Instale com: pip install pyttsx3")
        return False

    print(f"🔊 Convertendo texto para fala com pyttsx3 ({idioma})...")
    tempo_inicio = time.time()

    try:
        engine = pyttsx3.init()

        # Configurações
        engine.setProperty('rate', 150)      # Velocidade
        engine.setProperty('volume', 0.9)    # Volume

        # Tenta definir idioma (se suportado)
        try:
            engine.setProperty('language', idioma)
        except Exception:
            print(f"⚠️  Idioma {idioma} pode não ser totalmente suportado.")

        engine.save_to_file(texto, output_file)
        engine.runAndWait()

        tempo_decorrido = time.time() - tempo_inicio
        minutos, segundos = divmod(tempo_decorrido, 60)

        print(f"✅ Síntese concluída: {output_file}")
        print(f"⏱️  Tempo: {int(minutos)}m {segundos:.2f}s")
        return True

    except Exception as e:
        print(f"❌ Erro durante a síntese: {e}")
        return False


def tts_edge(texto, output_file, idioma):
    """Síntese de voz usando Edge TTS (Microsoft)."""
    try:
        import asyncio
        import edge_tts
    except ImportError:
        print("❌ edge-tts não está instalado.")
        print("   Instale com: pip install edge-tts")
        return False

    print(f"🔊 Convertendo texto para fala com Edge TTS ({idioma})...")
    tempo_inicio = time.time()

    try:
        async def sintetizar():
            communicate = edge_tts.Communicate(texto, voice=f"{idioma}-Female")
            await communicate.save(output_file)

        asyncio.run(sintetizar())

        tempo_decorrido = time.time() - tempo_inicio
        minutos, segundos = divmod(tempo_decorrido, 60)

        print(f"✅ Síntese concluída: {output_file}")
        print(f"⏱️  Tempo: {int(minutos)}m {segundos:.2f}s")
        return True

    except Exception as e:
        print(f"❌ Erro durante a síntese: {e}")
        return False


def tts_faster_whisper(texto, output_file, idioma):
    """Síntese de voz usando TTS (local, offline)."""
    try:
        from TTS.api import TTS
    except ImportError:
        print("❌ TTS não está instalado.")
        print("   Instale com: pip install TTS")
        return False

    print(f"🔊 Convertendo texto para fala com TTS local ({idioma})...")
    print("   (Primeira execução vai baixar o modelo ~1GB)")
    tempo_inicio = time.time()

    try:
        # Carrega modelo padrão
        tts = TTS(model_name="tts_models/pt/cv/glow-tts", gpu=True)

        # Sintetiza
        tts.tts_to_file(text=texto, file_path=output_file)

        tempo_decorrido = time.time() - tempo_inicio
        minutos, segundos = divmod(tempo_decorrido, 60)

        print(f"✅ Síntese concluída: {output_file}")
        print(f"⏱️  Tempo: {int(minutos)}m {segundos:.2f}s")
        return True

    except Exception as e:
        print(f"❌ Erro durante a síntese: {e}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("SÍNTESE DE VOZ (TEXT-TO-SPEECH)")
    print("="*70 + "\n")

    # Pede o arquivo de entrada
    input_file = input("Caminho do arquivo de texto a converter: ").strip()
    if not input_file or not validar_entrada(input_file):
        sys.exit(1)

    # Lê o texto
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            texto = f.read()
        print(f"✓ Arquivo lido ({len(texto)} caracteres)")
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        sys.exit(1)

    # Exibe opções
    ferramentas = exibir_ferramentas()

    print("\n" + "="*70)

    # Pede seleção da ferramenta
    opcao = input("\nEscolha a ferramenta (1, 2, 3 ou 4): ").strip()

    if opcao not in ["1", "2", "3", "4"]:
        print("❌ Opção inválida.")
        sys.exit(1)

    # Seleciona idioma
    idioma = selecionar_idioma()

    # Define nome de saída
    output_file = input("\nCaminho do arquivo de saída (padrão: audio.mp3): ").strip() or "audio.mp3"

    # Executa síntese
    print(f"\n{'='*70}")
    print(f"Ferramenta: {ferramentas[opcao]['nome']}")
    print(f"Entrada:    {input_file}")
    print(f"Saída:      {output_file}")
    print(f"Idioma:     {idioma}")
    print(f"{'='*70}\n")

    if opcao == "1":
        resultado = tts_gtts(texto, output_file, idioma)
    elif opcao == "2":
        resultado = tts_pyttsx3(texto, output_file, idioma)
    elif opcao == "3":
        resultado = tts_edge(texto, output_file, idioma)
    elif opcao == "4":
        resultado = tts_faster_whisper(texto, output_file, idioma)

    if resultado:
        print(f"\n✅ Concluído com sucesso!")
        sys.exit(0)
    else:
        print(f"\n❌ Falha na síntese de voz.")
        sys.exit(1)

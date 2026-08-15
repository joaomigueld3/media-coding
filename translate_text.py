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
    """Exibe as opções de ferramentas de tradução."""
    print("\n" + "="*70)
    print("OPÇÕES DE TRADUÇÃO")
    print("="*70)

    ferramentas = {
        "1": {
            "nome": "Google Translate (googletrans)",
            "velocidade": "Muito rápida (segundos)",
            "qualidade": "Excelente (95%+)",
            "requisitos": "pip install googletrans==4.0.0rc1",
            "vantagens": "Muito preciso, suporta 100+ idiomas, gratuito",
            "desvantagens": "Requer internet, pode ter limite de requisições",
            "idiomas": "100+",
        },
        "2": {
            "nome": "Deep-Translator (múltiplas APIs)",
            "velocidade": "Rápida (segundos)",
            "qualidade": "Muito boa (90%+)",
            "requisitos": "pip install deep-translator",
            "vantagens": "Suporta múltiplas APIs, fallback automático",
            "desvantagens": "Requer internet",
            "idiomas": "50+",
        },
        "3": {
            "nome": "Ollama + Local LLM",
            "velocidade": "Lenta (minutos)",
            "qualidade": "Muito boa (90%+)",
            "requisitos": "ollama (https://ollama.ai)",
            "vantagens": "Completamente offline, privado, customizável",
            "desvantagens": "Requer instalação Ollama, bem mais lento",
            "idiomas": "Qualquer",
        },
    }

    for chave, dados in ferramentas.items():
        print(f"\n[{chave}] {dados['nome']}")
        print(f"    Velocidade:    {dados['velocidade']}")
        print(f"    Qualidade:     {dados['qualidade']}")
        print(f"    Idiomas:       {dados['idiomas']}")
        print(f"    Vantagens:     {dados['vantagens']}")
        print(f"    Desvantagens:  {dados['desvantagens']}")

    return ferramentas


def selecionar_idioma():
    """Permite selecionar o idioma de destino."""
    idiomas = {
        "pt": "Português",
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
        "ja": "日本語",
        "zh": "中文",
        "ru": "Русский",
        "ko": "한국어",
        "ar": "العربية",
        "hi": "हिन्दी",
    }

    print("\n" + "="*70)
    print("IDIOMAS DE DESTINO")
    print("="*70)

    for i, (codigo, nome) in enumerate(idiomas.items(), 1):
        print(f"[{codigo}] {nome}")

    while True:
        idioma = input("\nEscolha o idioma de destino: ").strip().lower()
        if idioma in idiomas:
            print(f"✓ Idioma de destino: {idiomas[idioma]}")
            return idioma
        else:
            print("❌ Código de idioma inválido. Tente novamente.")


def traduzir_google(texto, idioma_destino):
    """Traduz usando Google Translate (googletrans)."""
    try:
        from googletrans import Translator
    except ImportError:
        print("❌ googletrans não está instalado.")
        print("   Instale com: pip install --user --break-system-packages googletrans==4.0.0rc1")
        return None

    print(f"🌐 Traduzindo para {idioma_destino} com Google Translate...")
    tempo_inicio = time.time()

    try:
        translator = Translator()
        resultado = translator.translate(texto, src_lang='auto', dest_lang=idioma_destino)
        texto_traduzido = resultado.text

        tempo_decorrido = time.time() - tempo_inicio
        print(f"✅ Tradução concluída em {tempo_decorrido:.2f}s")
        return texto_traduzido

    except Exception as e:
        print(f"❌ Erro durante a tradução: {e}")
        return None


def traduzir_deep_translator(texto, idioma_destino):
    """Traduz usando Deep-Translator."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print("❌ deep-translator não está instalado.")
        print("   Instale com: pip install --user --break-system-packages deep-translator")
        return None

    print(f"📝 Traduzindo para {idioma_destino} com Deep-Translator...")
    tempo_inicio = time.time()

    try:
        translator = GoogleTranslator(source='auto', target=idioma_destino)
        texto_traduzido = translator.translate(texto)

        tempo_decorrido = time.time() - tempo_inicio
        print(f"✅ Tradução concluída em {tempo_decorrido:.2f}s")
        return texto_traduzido

    except Exception as e:
        print(f"❌ Erro durante a tradução: {e}")
        return None


def traduzir_ollama(texto, idioma_destino):
    """Traduz usando Ollama + LLM local."""
    try:
        import requests
    except ImportError:
        print("❌ requests não está instalado.")
        print("   Instale com: pip install requests")
        return None

    print(f"🤖 Traduzindo para {idioma_destino} com Ollama (LLM local)...")
    print("   (Certifique-se que Ollama está rodando: ollama serve)")
    tempo_inicio = time.time()

    try:
        idiomas_nomes = {
            "pt": "português",
            "en": "inglês",
            "es": "espanhol",
            "fr": "francês",
            "de": "alemão",
            "it": "italiano",
            "ja": "japonês",
            "zh": "chinês",
            "ru": "russo",
            "ko": "coreano",
            "ar": "árabe",
            "hi": "hindi",
        }

        prompt = f"Traduza o seguinte texto para {idiomas_nomes.get(idioma_destino, idioma_destino)}. Responda APENAS com o texto traduzido, sem explicações:\n\n{texto}"

        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
        }, timeout=300)

        if response.status_code == 200:
            resultado = response.json()
            texto_traduzido = resultado.get('response', '').strip()

            tempo_decorrido = time.time() - tempo_inicio
            minutos, segundos = divmod(tempo_decorrido, 60)
            print(f"✅ Tradução concluída em {int(minutos)}m {segundos:.2f}s")
            return texto_traduzido
        else:
            print(f"❌ Erro da API Ollama: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        print("❌ Não consegui conectar ao Ollama.")
        print("   Certifique-se que Ollama está rodando: ollama serve")
        return None
    except Exception as e:
        print(f"❌ Erro durante a tradução: {e}")
        return None


if __name__ == "__main__":
    print("="*70)
    print("TRADUTOR DE TEXTO")
    print("="*70 + "\n")

    # Pede o arquivo de entrada
    input_file = input("Caminho do arquivo de texto a traduzir: ").strip()
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
    opcao = input("\nEscolha a ferramenta (1, 2 ou 3): ").strip()

    if opcao not in ["1", "2", "3"]:
        print("❌ Opção inválida.")
        sys.exit(1)

    # Seleciona idioma de destino
    idioma_destino = selecionar_idioma()

    # Define nome de saída
    output_file = input("\nCaminho do arquivo de saída (padrão: traducao.txt): ").strip() or "traducao.txt"

    # Executa tradução
    print(f"\n{'='*70}")
    print(f"Ferramenta: {ferramentas[opcao]['nome']}")
    print(f"Entrada:    {input_file}")
    print(f"Saída:      {output_file}")
    print(f"Idioma:     {idioma_destino}")
    print(f"{'='*70}\n")

    if opcao == "1":
        texto_traduzido = traduzir_google(texto, idioma_destino)
    elif opcao == "2":
        texto_traduzido = traduzir_deep_translator(texto, idioma_destino)
    elif opcao == "3":
        texto_traduzido = traduzir_ollama(texto, idioma_destino)

    # Salva resultado
    if texto_traduzido:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(texto_traduzido)
            print(f"\n✅ Tradução salva com sucesso: {output_file}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            sys.exit(1)
    else:
        print(f"\n❌ Falha na tradução.")
        sys.exit(1)

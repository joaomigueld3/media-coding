# Ferramentas de IA do Projeto

Guia de instalação e uso das ferramentas de transcrição, tradução e síntese de voz.

## 1️⃣ Transcrição de Áudio (`transcribe_audio.py`)

### Ferramentas Disponíveis

| Ferramenta | Velocidade | Qualidade | Offline | Requisitos |
|-----------|-----------|-----------|---------|-----------|
| **Whisper Large** | Lenta | Excelente | ✅ | `openai-whisper` |
| **Whisper Base** | Média | Boa | ✅ | `openai-whisper` |
| **Faster-Whisper** | Rápida | Boa | ✅ | `faster-whisper` |
| **Google Speech-to-Text** | Muito rápida | Excelente | ❌ | `SpeechRecognition` |

### Instalação

```bash
# Whisper (OpenAI)
pip install --user --break-system-packages openai-whisper

# Faster-Whisper (Recomendado - mais rápido)
pip install --user --break-system-packages faster-whisper

# Google Speech-to-Text
pip install --user --break-system-packages SpeechRecognition pydub
```

### Uso

```bash
python3 transcribe_audio.py
```

**Fluxo:**
1. Escolha o arquivo de áudio
2. Selecione a ferramenta (1-4)
3. Escolha detectar ou selecionar idioma
4. Defina arquivo de saída

---

## 2️⃣ Tradução de Texto (`translate_text.py`)

### Ferramentas Disponíveis

| Ferramenta | Velocidade | Qualidade | Offline | Requisitos |
|-----------|-----------|-----------|---------|-----------|
| **Google Translate** | Muito rápida | Excelente | ❌ | `googletrans==4.0.0rc1` |
| **Deep-Translator** | Rápida | Muito boa | ❌ | `deep-translator` |
| **Ollama + LLM** | Lenta | Muito boa | ✅ | `ollama` + `requests` |

### Instalação

```bash
# Google Translate (recomendado - mais simples)
pip install --user --break-system-packages googletrans==4.0.0rc1

# Deep-Translator (alternativa)
pip install --user --break-system-packages deep-translator

# Ollama (offline - requer instalação separada)
# Visite: https://ollama.ai
pip install --user --break-system-packages requests
```

### Uso

```bash
python3 translate_text.py
```

**Fluxo:**
1. Escolha arquivo de texto
2. Selecione a ferramenta (1-3)
3. Escolha idioma de destino
4. Defina arquivo de saída (text)

**Idiomas Suportados:** pt, en, es, fr, de, it, ja, zh, ru, ko, ar, hi

---

## 3️⃣ Síntese de Voz (`text_to_speech.py`)

### Ferramentas Disponíveis

| Ferramenta | Velocidade | Qualidade | Offline | Requisitos |
|-----------|-----------|-----------|---------|-----------|
| **Google TTS (gTTS)** | Rápida | Excelente | ❌ | `gtts` |
| **pyttsx3** | Rápida | Boa | ✅ | `pyttsx3` |
| **Edge TTS** | Rápida | Muito boa | ❌ | `edge-tts` |
| **TTS Local** | Lenta | Muito boa | ✅ | `TTS` |

### Instalação

```bash
# Google Text-to-Speech (recomendado - simples e rápido)
pip install --user --break-system-packages gtts

# pyttsx3 (offline)
pip install --user --break-system-packages pyttsx3

# Edge TTS (vozes naturais da Microsoft)
pip install --user --break-system-packages edge-tts

# TTS Local (offline - modelo ~1GB)
pip install --user --break-system-packages TTS
```

### Uso

```bash
python3 text_to_speech.py
```

**Fluxo:**
1. Escolha arquivo de texto
2. Selecione a ferramenta (1-4)
3. Escolha idioma
4. Defina arquivo de saída (MP3/WAV)

**Idiomas Suportados:** pt, pt-PT, en, en-GB, es, fr, de, it, ja, zh, ru, ko

---

## 🚀 Instalação Rápida (Tudo)

```bash
# Transcrição
pip install --user --break-system-packages openai-whisper faster-whisper SpeechRecognition pydub

# Tradução
pip install --user --break-system-packages googletrans==4.0.0rc1 deep-translator

# Síntese de Voz
pip install --user --break-system-packages gtts pyttsx3 edge-tts TTS

# Sistema (ferramentas necessárias)
sudo apt install ffmpeg
```

---

## 📋 Requisitos do Sistema

### FFmpeg (Necessário)
```bash
sudo apt install ffmpeg
```

### GPU (Opcional - Melhora Performance)
- NVIDIA GPU com CUDA: Detectado automaticamente
- Para Whisper: GPU acelera 5-20x
- Para TTS: GPU acelera síntese

### Python
- Python 3.8+
- pip (gerenciador de pacotes)

---

## 🔧 Troubleshooting

### Erro: "externally-managed-environment"

Use `--break-system-packages`:
```bash
pip install --user --break-system-packages PACOTE
```

Ver: [INSTALACAO.md](INSTALACAO.md)

### Erro: "Modelo não encontrado" (Whisper)

Primeira execução baixa modelo (~1-3 GB). Aguarde pacientemente.

### Erro: "Conexão recusada" (Ollama)

Certifique-se que Ollama está rodando:
```bash
ollama serve
```

### Idioma não suportado

Verifique os idiomas suportados:
- **Transcrição:** Whisper suporta 98+ idiomas
- **Tradução:** Google suporta 100+ idiomas
- **TTS:** Varia por ferramenta (10-100 idiomas)

---

## 📊 Comparação Rápida

### Melhor Transcrição
**Whisper Large** = 95%+ preciso, mas lento (0.5x em GPU)

### Transcrição Mais Rápida
**Faster-Whisper** = 90%+ preciso, 10-20x mais rápido em GPU

### Tradução Mais Simples
**Google Translate** = googletrans, uma linha de código

### Melhor TTS
**Edge TTS** = vozes naturais, gratuito

### Melhor para Privacidade
**Offline:** Whisper Base + pyttsx3 + Ollama

---

## 🎯 Fluxo Completo Exemplo

**Transcrição → Tradução → TTS**

```bash
# 1. Transcrever áudio em português para texto
python3 transcribe_audio.py
# → downloads/video.mp3 → transcricao.txt (Português)

# 2. Traduzir para inglês
python3 translate_text.py
# → transcricao.txt → transcricao_en.txt (English)

# 3. Converter de volta para áudio (inglês)
python3 text_to_speech.py
# → transcricao_en.txt → audio_en.mp3 (English)
```

---

## 📚 Referências

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [googletrans](https://github.com/ssut/py-googletrans)
- [gTTS](https://github.com/pndurette/gTTS)
- [Edge TTS](https://github.com/rany2/edge-tts)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
- [Ollama](https://ollama.ai)

# 🎬 Media Coding

Toolkit modular em Python para download, edição, processamento e automação de mídia (áudio e vídeo), combinando o poder do **FFmpeg** com modelos modernos de **Inteligência Artificial** para transcrição (Speech-to-Text), tradução e síntese de voz (Text-to-Speech).

---

## 🚀 Principais Recursos

- 📥 **Download de Mídia:** Baixe vídeos em até 8K ou extraia faixas de áudio diretamente de links do YouTube e dezenas de outras plataformas via `yt-dlp`.
- ✂️ **Edição Ultra-rápida (Lossless):** Cortes e junção de vídeos utilizando `-c copy` no FFmpeg — sem reprocessamento (re-encoding), mantendo 100% da qualidade original e concluindo em segundos.
- 🎙️ **Transcrição de Áudio (STT):** Suporte a OpenAI Whisper (modelos `base` a `large`), Faster-Whisper (acelerado com CTranslate2) e Google Speech Recognition.
- 🌐 **Tradução Multilíngue:** Tradução automática via Google Translate, Deep-Translator ou modelos LLM locais rodando no Ollama (Llama 3, Mistral, etc.) para privacidade total.
- 🗣️ **Síntese de Voz (TTS):** Geração de áudio falado com vozes neurais realistas (Microsoft Edge TTS), Google TTS (`gTTS`) ou opções 100% offline (`pyttsx3`, Coqui TTS).

---

## 📁 Estrutura do Repositório

```text
media-coding/
├── videos/                 # Pasta padrão para guardar vídeos de entrada e saída
├── downloads/              # Pasta de downloads gerados via yt-dlp
│
├── download_video.py       # Download de vídeos com seleção de resolução (240p a 8K)
├── download_audio.py       # Download direto da faixa de áudio em MP3
├── extract_audio.py        # Extrai áudio de vídeos locais (MP4, MKV -> MP3/WAV)
│
├── cut_video.py            # Corte rápido de trechos de vídeo (lê e salva na pasta videos/)
├── remove_cut_video.py     # Remove trecho do final do vídeo via ffprobe
├── join_video.py           # Concatena 2 ou mais vídeos sem reprocessar
├── cut_audio.py            # Corte preciso de arquivos de áudio
│
├── transcribe_audio.py     # Transcrição de áudio para texto (Whisper / Faster-Whisper / Google)
├── translate_text.py       # Tradução de texto entre múltiplos idiomas (Google / Ollama)
├── text_to_speech.py       # Síntese de voz a partir de texto (Edge TTS / gTTS / pyttsx3)
│
├── docs/                   # Pasta central de documentação (AGENTS, HANDOVER, TASKS, AI_TOOLS, INSTALACAO)
├── links.txt               # Lista de URLs de referência e testes
```

---

## 🛠️ Pré-requisitos

### 1. FFmpeg & FFprobe (Obrigatório)
Essenciais para as manipulações e conversões de mídia:

```bash
# Ubuntu / Debian / WSL
sudo apt update && sudo apt install -y ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows (Winget)
winget install Gyan.FFmpeg
```

### 2. Python e Dependências

Recomendado **Python 3.8+**. Instale os módulos conforme a necessidade:

```bash
# Módulos de Download e Extração
pip install yt-dlp

# Módulos de Transcrição (Speech-to-Text)
pip install faster-whisper openai-whisper SpeechRecognition pydub

# Módulos de Tradução
pip install googletrans==4.0.0rc1 deep-translator

# Módulos de Síntese de Voz (TTS)
pip install edge-tts gtts pyttsx3
```

> 💡 **Dica:** Para ambientes Linux recentes (Ubuntu 24.04+ no WSL), utilize um ambiente virtual (`python3 -m venv .venv && source .venv/bin/activate`) ou a flag `--break-system-packages`. Consulte o [INSTALACAO.md](INSTALACAO.md) para o passo a passo completo.

---

## 📖 Como Usar

### 1. Download de Mídia

* **Download de Vídeo:**
  ```bash
  python3 download_video.py
  ```
  Permite informar a URL (YouTube, etc.) e escolher a qualidade (`1080p`, `720p`, `4k`, `best`, etc.). O vídeo será salvo na pasta `downloads/`.

* **Download de Áudio:**
  ```bash
  python3 download_audio.py
  ```
  Baixa exclusivamente a trilha de áudio do vídeo e converte automaticamente para MP3 de alta qualidade.

---

### 2. Edição de Vídeo e Áudio

* **Corte Rápido de Vídeo (`cut_video.py`):**
  ```bash
  python3 cut_video.py
  ```
  O script utiliza a pasta `videos/` como origem e destino padrão:
  - **Vídeo de entrada:** Informe o nome do arquivo presente na pasta `videos/` (ex: `meu_video.mp4`).
  - **Vídeo de saída:** Nome do arquivo a ser salvo em `videos/` (ex: `corte.mp4`).
  - **Início:** Tempo inicial (Padrão: `00:00:00`).
  - **Duração:** Duração do corte (Padrão: `00:05:00`).

* **Remover parte final do vídeo:**
  ```bash
  python3 remove_cut_video.py
  ```
  Calcula automaticamente a duração total com `ffprobe` e apara o tempo final desejado.

* **Juntar vídeos (Concatenação):**
  ```bash
  python3 join_video.py
  ```
  Mescla dois vídeos com os mesmos parâmetros de codec sem perda de qualidade.

* **Extrair áudio de vídeo local:**
  ```bash
  python3 extract_audio.py
  ```
  Converte a faixa de som de qualquer vídeo local para MP3 ou WAV.

---

### 3. Pipeline de IA: Transcrição ➔ Tradução ➔ Dublagem (TTS)

Você pode criar um pipeline completo de dublagem ou tradução de conteúdo executando a sequência:

```bash
# 1. Transcrever o áudio original para texto
python3 transcribe_audio.py
# Entrada: downloads/audio.mp3  ->  Saída: transcricao.txt

# 2. Traduzir o texto transcrito para o idioma desejado (ex: Inglês, Espanhol)
python3 translate_text.py
# Entrada: transcricao.txt  ->  Saída: transcricao_en.txt

# 3. Gerar a nova narração de áudio (voz neural)
python3 text_to_speech.py
# Entrada: transcricao_en.txt  ->  Saída: downloads/audio_en.mp3
```

---

## 🧠 Modelos de IA Disponíveis

| Etapa | Ferramenta Recomendada | Vantagens | Execução Offline |
|---|---|---|:---:|
| **Transcrição** | **Faster-Whisper** | Alta acurácia e processamento ultra-rápido | ✅ Sim |
| **Transcrição** | **Whisper (OpenAI)** | Modelo oficial de referência (Base a Large) | ✅ Sim |
| **Transcrição** | **Google Speech** | Extremamente leve (processamento em nuvem) | ❌ Não |
| **Tradução** | **Google Translate** | Rápido, estável e suporta centenas de idiomas | ❌ Não |
| **Tradução** | **Ollama (LLM)** | Suporta modelos como Llama 3 e Mistral localmente | ✅ Sim |
| **Síntese de Voz** | **Edge TTS** | Vozes neurais muito naturais (Microsoft) | ❌ Não |
| **Síntese de Voz** | **pyttsx3** | Leve e funciona em qualquer SO sem conexão | ✅ Sim |

Para um guia completo sobre cada modelo e benchmarks de performance, consulte [AI_TOOLS.md](docs/AI_TOOLS.md).

---

## 📄 Documentações Relacionadas

* [INSTALACAO.md](docs/INSTALACAO.md): Guia de resolução de dependências, drivers CUDA e FFmpeg.
* [AI_TOOLS.md](docs/AI_TOOLS.md): Detalhes técnicos, modelos suportados e parâmetros de IA.

---

## 📜 Licença

Este projeto é de código aberto sob a licença MIT. Sinta-se livre para utilizar, contribuir e customizar para seus próprios projetos de mídia!
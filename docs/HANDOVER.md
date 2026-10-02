# 📋 Handover Context — Project Media Coding

Este documento serve como transferência de contexto completa para novos agentes e desenvolvedores sobre o estado atual do repositório, decisões arquiteturais, scripts disponíveis e instruções de ambiente.

---

## 🖥️ 1. Ambiente de Execução & Arquitetura Híbrida (IMPORTANTE)

- **Sistema Local:** WSL2 Ubuntu (`/home/joao/media-coding`) sob Host Windows.
- **FFmpeg:** Instalado no Linux (`/usr/bin/ffmpeg`), **não** instalado no Windows PATH.
- **Regra de Execução Local:** Todos os scripts Python devem ser executados no ambiente WSL Ubuntu:
  ```bash
  wsl python3 script.py
  ```
- **Ambiente de Nuvem (Google Colab Pro):**
  - Utilizado para modelos pesados (Real-ESRGAN x4, Whisper Large-v3, clonagem de voz).
  - **Conexão recomendada (Opção 1):** VS Code Remote SSH via Cloudflare Tunnel (`cloudflared`).

---

## 🚀 2. Módulos do Toolkit (`/home/joao/media-coding`)

| Script | Função | Onde Rodar | Dependências Principais |
| :--- | :--- | :--- | :--- |
| `download_video.py` | Baixar vídeos do YouTube (Prioridade 1080p, múltiplos links) | Local (WSL) | `yt-dlp`, `ffmpeg` |
| `remaster_video.py` | Remasterização e Upscale de vídeo (4 técnicas) | Local / Colab | `opencv-contrib-python`, `ffmpeg-python`, `requests`, `tqdm` |
| `cut_video.py` / `cut_audio.py` | Corte e trim de mídias sem reencode | Local (WSL) | `ffmpeg` |
| `transcribe_audio.py` | Speech-to-Text (Whisper / Faster-Whisper / Google) | Local / Colab | `openai-whisper`, `faster-whisper` |
| `translate_text.py` | Tradução de textos transcritos | Local (WSL) | `googletrans`, `deep-translator` |
| `text_to_speech.py` | Síntese de voz / Dublagem (Edge-TTS / gTTS / pyttsx3) | Local (WSL) | `edge-tts`, `gtts` |

---

## 🎬 3. Módulo de Remasterização (`remaster_video.py`)

O script oferece 4 técnicas com diferentes níveis de qualidade e velocidade:
1. **FFmpeg Básico (CPU Local - Rápido):** Upscale Lanczos para 1080p + `unsharp` + `hqdn3d`.
2. **OpenCV FSRCNN x2 (CPU/ML - Leve):** Rede neural leve para dobrar a resolução.
3. **OpenCV EDSR x2 (GPU/ML - Alta Qualidade):** Rede neural de altíssima precisão.
4. **Real-ESRGAN x4 via Vulkan (GPU Colab - Avançado):** Processamento generativo via binário C++ Vulkan. Aumenta a resolução em 4x e reconstrói detalhes.

**Exemplo de Uso:**
```bash
# Modo Interativo:
wsl python3 remaster_video.py

# Modo CLI (Argumentos: <opcao> <entrada> <saida>):
wsl python3 remaster_video.py 1 "videos/input.mp4" "videos/output.mp4"
```

---

## 🔑 4. Como Conectar o VS Code ao Colab Pro (Passo a Passo)

1. **No Colab Pro:** Crie um Notebook com GPU ativada e rode a célula de conexão SSH com `cloudflared`:
   ```python
   !apt-get update -qq && apt-get install -qq -y openssh-server
   !wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared
   !echo "root:<SUA_SENHA_DEFINIDA>" | chpasswd
   !sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
   !service ssh restart
   import subprocess; subprocess.Popen(["cloudflared", "tunnel", "--url", "ssh://localhost:22"])
   ```
2. **No PC (Windows):** Instale o `cloudflared` (`winget install Cloudflare.cloudflared`).
3. **No VS Code:** Adicione a entrada no `~/.ssh/config`:
   ```ssh
   Host colab-gpu
       HostName <link-gerado-trycloudflare.com>
       User root
       ProxyCommand cloudflared.exe access ssh --hostname %h
       StrictHostKeyChecking no
       UserKnownHostsFile /dev/null
   ```
4. Conecte via **Remote-SSH: Connect to Host... -> colab-gpu** (Senha: `<SUA_SENHA_DEFINIDA>`).

---

## 🔮 5. Próximos Passos Recomendados

1. **Orquestrador Unificado (`pipeline.py`):**
   - Conectar Download ➔ Transcrição ➔ Tradução ➔ Dublagem (Edge-TTS) em um único comando CLI.
2. **Testes de Clonagem de Voz:**
   - Integrar `XTTS-v2` / `F5-TTS` no Colab Pro para dublagem com voz clonada a partir de amostra de áudio.
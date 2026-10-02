# Guia de Instalação e Troubleshooting

## Erro: "externally-managed-environment"

### O que é?
Debian/Ubuntu protegem o Python do sistema (PEP 668) para evitar conflitos entre pacotes. Quando você tenta `pip install`, aparece este erro:

```
error: externally-managed-environment
× This environment is externally managed
```

### 3 Soluções

#### **Opção 1: `--break-system-packages` (Rápida e Recomendada)**
Ignora a proteção do sistema. Baixo risco, já que você está instalando pacotes de confiança.

```bash
pip install --user --break-system-packages PACOTE
```

**Exemplos:**
```bash
pip install --user --break-system-packages faster-whisper
pip install --user --break-system-packages openai-whisper
pip install --user --break-system-packages yt-dlp
pip install --user --break-system-packages SpeechRecognition
```

✅ Funciona imediatamente  
✅ Sem dependências adicionais  
❌ Ignora proteção do Debian (mas é seguro para pacotes oficiais)

---

#### **Opção 2: Ambiente Virtual (Recomendado para Longo Prazo)**
Cria um ambiente isolado dentro do projeto. Evita conflitos com o sistema.

```bash
# Criar ambiente virtual
python3 -m venv ~/.venv-videos

# Ativar ambiente
source ~/.venv-videos/bin/activate

# Instalar pacotes
pip install faster-whisper openai-whisper yt-dlp SpeechRecognition
```

**Para usar os scripts:**
```bash
# Sempre ative o ambiente antes:
source ~/.venv-videos/bin/activate

# Depois rode os scripts normalmente:
python3 cut_video.py
python3 transcribe_audio.py
```

**Para desativar:**
```bash
deactivate
```

✅ Isolado do sistema  
✅ Sem conflitos  
✅ Fácil de gerenciar  
❌ Precisa ativar antes de usar

---

#### **Opção 3: `pipx` (Mais Limpo)**
Gerencia ambientes virtuais automaticamente para aplicações CLI.

```bash
# Instalar pipx (requer sudo)
sudo apt install pipx

# Instalar pacotes
pipx install faster-whisper
pipx install yt-dlp
```

✅ Gerenciamento automático  
✅ Sem ativar ambiente  
❌ Requer `sudo`  
❌ Melhor para aplicações, não bibliotecas

---

## Pacotes Necessários por Script

### `download_video.py` e `download_audio.py`
```bash
pip install --user --break-system-packages yt-dlp
```

### `transcribe_audio.py` - Opções de Transcrição
```bash
# Whisper (OpenAI)
pip install --user --break-system-packages openai-whisper

# Faster-Whisper (Recomendado - mais rápido)
pip install --user --break-system-packages faster-whisper

# Google Speech-to-Text
pip install --user --break-system-packages SpeechRecognition pydub
```

### Ferramentas do Sistema
```bash
# FFmpeg (necessário para todos os scripts de vídeo/áudio)
sudo apt install ffmpeg

# Python dev (opcional, para compilação de alguns pacotes)
sudo apt install python3-full python3-dev
```

---

## Verificar Instalação

```bash
# Verificar yt-dlp
python3 -c "import yt_dlp; print(yt_dlp.version.__version__)"

# Verificar Whisper
python3 -c "import whisper; print('Whisper OK')"

# Verificar Faster-Whisper
python3 -c "import faster_whisper; print('Faster-Whisper OK')"

# Verificar SpeechRecognition
python3 -c "import speech_recognition; print('SpeechRecognition OK')"

# Verificar ffmpeg
ffmpeg -version | head -1
```

---

## Dicas

1. **Use `--user` sempre**: Instala no home do usuário, não no sistema
2. **Use `--break-system-packages`**: Seguro para pacotes oficiais (PyPI)
3. **Se possível, use venv**: Melhor prática a longo prazo
4. **Atualize yt-dlp regularmente**: YouTube muda frequentemente
   ```bash
   pip install --user --break-system-packages -U yt-dlp
   ```

---

## Problemas Comuns

### "Nenhuma GPU encontrada"
É normal se sua máquina não tem NVIDIA CUDA. Os scripts funcionam com CPU, apenas mais lentamente.

### "Modelo não encontrado" (Whisper)
Primeira execução baixa o modelo automaticamente (~1-3 GB).

### "403 Forbidden" (YouTube)
Atualize yt-dlp:
```bash
pip install --user --break-system-packages -U yt-dlp
```

### Permissão negada ao criar pasta
Use `sudo mkdir -p pasta` para criar, depois `sudo chown $USER:$USER pasta`

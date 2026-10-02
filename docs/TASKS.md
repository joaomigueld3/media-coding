# 📋 Gestão de Tarefas (Spec-Driven Kanban) - Media Coding

Documento central para rastreamento de melhorias, refatorações e novas funcionalidades do repositório `media-coding`.

---

## 🏗️ Diretrizes de Arquitetura (Local CPU vs Google Colab Pro GPU)

Como a máquina local roda no WSL sem GPU dedicada, adotamos um modelo híbrido:

1. **Local (Processamento CPU / Scripts Rápido)**:
   - **Download e Recorte de Mídia**: `yt-dlp`, `ffmpeg`.
   - **Tratamento de Áudio**: Filtros FFmpeg (`afftdn`, `equalizer`, `loudnorm`).
   - **Text-to-Speech (TTS)**: `edge-tts` (síntese neural rápida via web API) e Coqui VITS CPU.
   - **Remaster Leve de Vídeo**: Filtros FFmpeg (`hqdn3d`, `nlmeans`, `unsharp`, Lanczos upscaling).
2. **Google Colab Pro (Processamento GPU T4/V100/A100)**:
   - **Upscaling & Restauração de Vídeo por IA**: Real-ESRGAN, GFPGAN / CodeFormer.
   - **Interpolação de Frames (60 FPS)**: RIFE AI.
   - **Speech-to-Text & Clonagem de Voz**: Whisper `large-v3`, XTTS v2, RVC.

---

## 📊 Kanban Board

| 🟢 To Do | 🟡 In Progress | ✅ Concluído |
| :--- | :--- | :--- |
| [`TASK-001`](#task-001-download-de-playlists-públicas-e-não-listadas) Download de Playlists | - | `[CORE]` Download individual (`download_video.py`) |
| [`TASK-002`](#task-002-listagem-e-metadados-de-canal-para-frontend) Metadados de Canal | - | `[CORE]` Recorte e Junção (`cut_video.py`, `join_video.py`) |
| [`TASK-003`](#task-003-download-de-canais-com-filtros-e-ordenação) Download de Canal com Filtros | - | `[CORE]` Transcrição base (`transcribe_audio.py`) |
| [`TASK-004`](#task-004-interface-frontend-para-seleção-visual-de-lote) UI Frontend Lote | - | `[CORE]` Remaster base (`remaster_video.py`) |
| [`TASK-005`](#task-005-tratamento-de-áudio-limpeza--normalização-local-cpu) Tratamento de Áudio (CPU) | - | |
| [`TASK-006`](#task-006-text-to-speech-tts--clonagem-de-voz-híbrida) TTS & Clonagem de Voz | - | |
| [`TASK-007`](#task-007-speech-to-text-stt-otimizado-local--colab-pro) STT Otimizado (Whisper) | - | |
| [`TASK-008`](#task-008-engine-de-remasterização-de-vídeo-multitécnicas-local--colab-gpu) Remaster Multitécnicas | - | |

---

## 🎯 Especificações de Tarefas

### Módulo: Download em Lote (`download_video.py` / API)

#### `TASK-001`: Download de Playlists Públicas e Não Listadas
- **Status**: 🟢 To Do | **Prioridade**: 🔥 High (Must Have)
- **Descrição**: Permitir o download completo de playlists via link direto.
- **Critérios de Aceitação**:
  - [ ] Suportar URLs no formato `https://www.youtube.com/playlist?list=...`
  - [ ] Preservar ordem salvando com prefixo numérico (`%(playlist_index)s - %(title)s.%(ext)s`).

#### `TASK-002`: Listagem e Metadados de Canal para Frontend
- **Status**: 🟢 To Do | **Prioridade**: 🔥 High (Must Have)
- **Descrição**: Extrair e retornar em JSON informações dos vídeos de um canal sem baixar mídia.
- **Critérios de Aceitação**:
  - [ ] Extrair via `yt-dlp` (`extract_flat`): `id`, `titulo`, `data`, `views`, `duracao`, `thumbnail`.

#### `TASK-003`: Download de Canais com Filtros e Ordenação
- **Status**: 🟢 To Do | **Prioridade**: 🔥 High (Must Have)
- **Descrição**: Baixar vídeos de canais (`@canal`) com filtros de ordenação e data.
- **Critérios de Aceitação**:
  - [ ] Ordenar por views e data (mais recentes / mais antigos).
  - [ ] Filtro por intervalo de data e limite de quantidade (top N).

#### `TASK-004`: Interface Frontend para Seleção Visual de Lote
- **Status**: 🟢 To Do | **Prioridade**: ⚡ Medium (Should Have)
- **Descrição**: Componente UI com grid de thumbnails e checkboxes para disparar downloads em lote.

---

### Módulo: Áudio & Voz

#### `TASK-005`: Tratamento de Áudio (Limpeza & Normalização Local CPU)
- **Status**: 🟢 To Do | **Prioridade**: 🔥 High (Must Have)
- **Ferramentas**: FFmpeg (`afftdn`, `loudnorm`, `equalizer`)
- **Descrição**: Criar pipeline em Python para remoção de ruído branco/fundo, clareza vocal e normalização de volume no padrão broadcast (EBU R128).

#### `TASK-006`: Text-to-Speech (TTS) & Clonagem de Voz Híbrida
- **Status**: 🟢 To Do | **Prioridade**: ⚡ Medium (Should Have)
- **Ferramentas**: Local: `edge-tts` / Colab Pro: XTTS v2, RVC
- **Descrição**: 
  - **Local**: Gerar narrações neurais ultra rápidas e sem custo usando `edge-tts`.
  - **Colab Pro**: Notebook/script para clonar voz a partir de áudios de referência.

#### `TASK-007`: Speech-to-Text (STT) Otimizado (Local + Colab Pro)
- **Status**: 🟢 To Do | **Prioridade**: ⚡ Medium (Should Have)
- **Ferramentas**: `whisper.cpp` / `faster-whisper`
- **Descrição**: Transcrição local ultrarrápida em CPU (modelos quantizados `base`/`small`) e suporte no Colab Pro para execução com GPU de vídeos longos usando `large-v3`.

---

### Módulo: Remasterização de Vídeo Multitécnicas

#### `TASK-008`: Engine de Remasterização de Vídeo Multitécnicas (Local & Colab GPU)
- **Status**: 🟢 To Do | **Prioridade**: 🔥 High (Must Have)
- **Arquivo Alvo**: `remaster_video.py` / Módulo de Remaster
- **Vídeo de Teste**: `videos/12 Hiperautomação： Robotic Process Automation (RPA) com Python (480p)_corte.mp4`
- **Descrição**: Desenvolver uma engine modular de remasterização que ofereça múltiplos perfis de acordo com o poder computacional disponível (CPU Local vs Colab Pro GPU).
- **Opções / Perfis de Remaster**:
  1. **Perfil 1 - Fast Denoise & Sharpen (CPU Local)**: Filtros FFmpeg `hqdn3d` + `unsharp` (removendo artefatos sem comprometer velocidade).
  2. **Perfil 2 - High Quality CPU Filter (CPU Local)**: `nlmeans` (denoise espacial de alta precisão), ajuste de curvas de cor/contraste e upscaling Lanczos.
  3. **Perfil 3 - AI Upscale 4X (Google Colab Pro GPU)**: Upscaling de resolução via Real-ESRGAN v4 com restauração facial opcional (CodeFormer/GFPGAN).
  4. **Perfil 4 - AI FPS Interpolation 60fps (Google Colab Pro GPU)**: Interpolação de quadros por IA utilizando RIFE.
- **Critérios de Aceitação**:
  - [ ] CLI/Opções claras para escolha de perfil.
  - [ ] Preservação e sincronização perfeita da trilha de áudio original.
  - [ ] Script pronto para rodar testes automatizados locais usando o arquivo de teste indicado.

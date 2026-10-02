---
name: repo-organizer
description: >-
  Regras e instruções padronizadas para manutenção da estrutura de diretórios e organização
  do repositório media-coding. Use sempre que for adicionar novos scripts, documentos ou arquivos de mídia.
---

# 📂 Repo Organizer Skill — Media Coding

Esta skill define a convenção de organização de arquivos do repositório `media-coding`.

## 📌 Convenções de Diretórios

- **`docs/`**: Todos os arquivos de documentação Markdown (`.md`), exceto o `README.md` da raiz.
- **`videos/`**: Diretório padrão para vídeos de entrada e vídeos cortados/processados locais.
- **`downloads/`**: Diretório exclusivo para downloads gerados via `yt-dlp`.
- **`tools/`**: Binários, ferramentas externas executáveis (ex: `realesrgan-ncnn-vulkan`).
- **`Raiz do Projeto`**: Apenas scripts Python principais (`*.py`), `README.md`, `.gitignore` e `requirements.txt`.

## 🧹 Regras de Execução

1. Nunca crie arquivos `.md` soltos na raiz (salve sempre em `docs/`).
2. Mantenha os arquivos temporários e binários de saída ignorados no `.gitignore`.

#!/usr/bin/env python3
import os
import re
import sys
import subprocess

# Padrões Regex para detectar segredos
PATTERNS = {
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{32,}",
    "Google API Key": r"AIzaSy[a-zA-Z0-9_\-]{35}",
    "GitHub Token": r"gh[pousr]_[a-zA-Z0-9]{36,}",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "Chave Privada PEM": r"-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----",
    "Senha/Token Atribuído": r'(?i)(api_key|secret|password|passwd|token|auth_token)\s*=\s*["\'][^"\']{6,}["\']'
}

EXTENSOES_IGNORADAS = {'.png', '.jpg', '.jpeg', '.mp4', '.mp3', '.wav', '.zip', '.pb', '.cache'}

def verificar_segredos():
    print("🔍 Auditando arquivos rastreados contra vazamento de credenciais...")
    result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
    arquivos = result.stdout.splitlines()

    vulnerabilidades = 0
    for file_path in arquivos:
        if not os.path.exists(file_path):
            continue
        _, ext = os.path.splitext(file_path)
        if ext.lower() in EXTENSOES_IGNORADAS:
            continue

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for nome_pattern, regex in PATTERNS.items():
                matches = re.finditer(regex, content)
                for m in matches:
                    texto_encontrado = m.group(0)
                    if "SUA_SENHA" in texto_encontrado or "YOUR_API_KEY" in texto_encontrado:
                        continue
                    print(f"❌ [VULNERABILIDADE DETECTADA] {nome_pattern} em '{file_path}'")
                    vulnerabilidades += 1
        except Exception as e:
            print(f"⚠️ Erro ao ler {file_path}: {e}")

    if vulnerabilidades == 0:
        print("✅ Nenhuma credencial ou chave secreta detectada!")
        return True
    else:
        print(f"\n🚨 {vulnerabilidades} possíveis segredos encontrados! Corrija antes de commit/push.")
        return False

if __name__ == "__main__":
    sucesso = verificar_segredos()
    sys.exit(0 if sucesso else 1)

#!/usr/bin/env python3
"""
Script para atualizar o versionamento do projeto
"""

import os
import re
from pathlib import Path


def update_file_version(file_path, old_version, new_version):
    """Atualiza a versão em um arquivo"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        original_content = content
        
        # Padrões de versão para substituir
        patterns = [
            (rf"version\s*=\s*[\"']?{re.escape(old_version)}[\"']?", f'version = "{new_version}"'),
            (rf"__version__\s*=\s*[\"']?{re.escape(old_version)}[\"']?", f'__version__ = "{new_version}"'),
            (rf"VERSION\s*=\s*[\"']?{re.escape(old_version)}[\"']?", f'VERSION = "{new_version}"'),
            (rf"versão\s+{re.escape(old_version)}", f"versão {new_version}"),
            (rf"Version\s+{re.escape(old_version)}", f"Version {new_version}"),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Atualizado: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False


def update_version_in_files(directory, old_version, new_version):
    """Atualiza versão em todos os arquivos de um diretório"""
    updated_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.yml', '.yaml')):
                file_path = os.path.join(root, file)
                if update_file_version(file_path, old_version, new_version):
                    updated_files.append(file_path)
    
    return updated_files


def main():
    """Função principal"""
    print("Atualizando versionamento do projeto...")
    
    # Versões
    old_version = "1.7"
    new_version = "1.7"
    
    # Diretórios para processar
    directories = [
        "src/",
        "tests/",
        "examples/",
        ".",
    ]
    
    total_updated = 0
    for directory in directories:
        if os.path.exists(directory):
            print(f"Processando {directory}...")
            updated = update_version_in_files(directory, old_version, new_version)
            total_updated += len(updated)
            print(f"Arquivos atualizados em {directory}: {len(updated)}")
    
    print(f"Total de arquivos atualizados: {total_updated}")


if __name__ == "__main__":
    main()

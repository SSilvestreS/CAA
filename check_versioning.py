#!/usr/bin/env python3
"""
Script para verificar a consistência do versionamento
"""

import os
import re
from pathlib import Path


def check_version_consistency():
    """Verifica a consistência do versionamento no projeto"""
    print("Verificando consistência do versionamento...")
    
    # Versão esperada
    expected_version = "1.7.0"
    
    # Arquivos para verificar
    files_to_check = [
        "setup.py",
        "src/__version__.py",
        "README.md",
        "CHANGELOG.md",
    ]
    
    issues = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Verifica se a versão está presente
                if expected_version not in content:
                    issues.append(f"Versão {expected_version} não encontrada em {file_path}")
                
                # Verifica versões antigas
                old_versions = ["1.6.0", "1.5.0", "1.4.0", "1.3.0"]
                for old_version in old_versions:
                    if old_version in content and file_path != "CHANGELOG.md":
                        issues.append(f"Versão antiga {old_version} encontrada em {file_path}")
                
            except Exception as e:
                issues.append(f"Erro ao ler {file_path}: {e}")
        else:
            issues.append(f"Arquivo não encontrado: {file_path}")
    
    # Verifica arquivos Python para imports de versão
    python_files = []
    for root, dirs, files in os.walk("src/"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Verifica se há referências a versões antigas
            if "1.6" in content and "1.7" not in content:
                issues.append(f"Referência à versão 1.6 em {file_path}")
                
        except Exception as e:
            issues.append(f"Erro ao verificar {file_path}: {e}")
    
    return issues


def main():
    """Função principal"""
    issues = check_version_consistency()
    
    if issues:
        print(f"\n❌ Encontrados {len(issues)} problemas de versionamento:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Versionamento consistente em todo o projeto!")
    
    # Verifica se o setup.py pode ser executado
    try:
        import subprocess
        result = subprocess.run(["python", "setup.py", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Versão do setup.py: {version}")
        else:
            print(f"❌ Erro ao executar setup.py: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro ao verificar setup.py: {e}")


if __name__ == "__main__":
    main()

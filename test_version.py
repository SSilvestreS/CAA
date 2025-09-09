#!/usr/bin/env python3
"""
Teste simples de versão
"""

VERSION = "1.7.0"

print(f"Versão definida: {VERSION}")

# Simula o que o setup.py faz
def get_version():
    return VERSION

print(f"Versão da função: {get_version()}")

# Testa se consegue importar do src
try:
    from src.__version__ import get_version as get_version_from_src
    print(f"Versão do src: {get_version_from_src()}")
except ImportError as e:
    print(f"Erro ao importar do src: {e}")

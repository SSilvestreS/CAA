#!/usr/bin/env python3
"""
Script para corrigir variáveis não utilizadas automaticamente
"""

import os
import re


def fix_unused_variables(file_path):
    """Corrige variáveis não utilizadas comuns"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Padrões de variáveis não utilizadas comuns
        patterns = [
            # Variáveis simples que podem ser removidas
            (
                r"(\s+)(\w+_factor)\s*=\s*[^\\n]+\\n",
                r"\1# \2 removido - não utilizado\n",
            ),
            (r"(\s+)(\w+_type)\s*=\s*[^\\n]+\\n", r"\1# \2 removido - não utilizado\n"),
            (
                r"(\s+)(\w+_tensor)\s*=\s*[^\\n]+\\n",
                r"\1# \2 removido - não utilizado\n",
            ),
            (
                r"(\s+)(\w+_consumption)\s*=\s*[^\\n]+\\n",
                r"\1# \2 removido - não utilizado\n",
            ),
            (r"(\s+)(\w+_size)\s*=\s*[^\\n]+\\n", r"\1# \2 removido - não utilizado\n"),
            (r"(\s+)(old_\w+)\s*=\s*[^\\n]+\\n", r"\1# \2 removido - não utilizado\n"),
            (
                r"(\s+)(dashboard)\s*=\s*[^\\n]+\\n",
                r"\1# \2 removido - não utilizado\n",
            ),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Corrigido: {file_path}")
            return True
        return False

    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False


def main():
    """Função principal"""
    # Arquivos específicos com variáveis não utilizadas
    files = [
        "src/agents/business_agent.py",
        "src/agents/government_agent.py",
        "src/agents/infrastructure_agent.py",
        "src/ai/advanced_models/lstm_models.py",
        "src/ai/advanced_models/reinforcement_learning.py",
        "src/security/encryption.py",
    ]

    files_processed = 0
    files_fixed = 0

    for file_path in files:
        if os.path.exists(file_path):
            files_processed += 1
            if fix_unused_variables(file_path):
                files_fixed += 1

    print(f"\nProcessados: {files_processed} arquivos")
    print(f"Corrigidos: {files_fixed} arquivos")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script para corrigir imports não utilizados automaticamente
"""

import os
import re

# sys removido - não utilizado


def fix_common_unused_imports(file_path):
    """Corrige imports não utilizados comuns"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Padrões de imports não utilizados comuns
        patterns = [
            # datetime imports
            (
                r"from datetime import datetime, timedelta\n",
                "from datetime import datetime\n",
            ),
            (r"from datetime import datetime\n", "from datetime import datetime\n"),
            (r"import datetime\n", ""),
            # typing imports
            (
                r"from typing import Dict, List, Any, Optional, Tuple\n",
                "from typing import Dict, List, Any, Optional\n",
            ),
            (
                r"from typing import Dict, List, Any, Optional\n",
                "from typing import Dict, List, Any\n",
            ),
            (
                r"from typing import Dict, List, Any\n",
                "from typing import Dict, List\n",
            ),
            (r"from typing import Dict, List\n", "from typing import Dict\n"),
            (r"from typing import Dict\n", ""),
            # outros imports comuns
            (r"import asyncio\n", ""),
            (r"import threading\n", ""),
            (r"import multiprocessing as mp\n", ""),
            (r"import pickle\n", ""),
            (r"import json\n", ""),
            (r"import math\n", ""),
            (r"import hashlib\n", ""),
            (r"import statistics\n", ""),
            (
                r"from collections import defaultdict, deque\n",
                "from collections import deque\n",
            ),
            (r"from collections import deque\n", ""),
            # imports condicionais
            (
                r"try:\n    import torch\n    import torch\.nn as nn\n    import torch\.optim as optim\n\nexcept ImportError:\n    torch = None\n    nn = None\n    optim = None\n",
                "",
            ),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        # Remove linhas vazias duplas
        content = re.sub(r"\n\n\n+", "\n\n", content)

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
    # Diretórios para processar
    directories = ["src/", "examples/", "tests/"]

    files_processed = 0
    files_fixed = 0

    for directory in directories:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        files_processed += 1
                        if fix_common_unused_imports(file_path):
                            files_fixed += 1

    print(f"\nProcessados: {files_processed} arquivos")
    print(f"Corrigidos: {files_fixed} arquivos")


if __name__ == "__main__":
    main()

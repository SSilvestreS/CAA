"""
Script de instalação para o projeto Cidades Autônomas com Agentes de IA.
"""

try:
    from setuptools import setup, find_packages  # type: ignore
except ImportError:
    print("setuptools não encontrado. Instalando...")
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
    from setuptools import setup, find_packages  # type: ignore

# Importa informações de versão
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.__version__ import get_version, __author__, __email__, __description__, __license__
except ImportError:
    # Fallback se não conseguir importar
    def get_version():
        return "1.7.0"
    __author__ = "Sistema de Simulação de Cidade Inteligente"
    __email__ = "contato@cidadesautonomas.com"
    __description__ = "Simulação de cidade inteligente com múltiplos agentes de IA"
    __license__ = "MIT"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="cidades-autonomas-ia",
    version=get_version(),
    author=__author__,
    author_email=__email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "black>=23.7.0",
            "flake8>=6.0.0",
        ],
        "gpu": [
            "torch>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smart-city=main:main",
            "city-scenarios=run_scenarios:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
)

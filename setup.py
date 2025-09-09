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

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="cidades-autonomas-ia",
    version="1.3.0",
    author="Sistema de Simulação de Cidade Inteligente",
    description="Simulação de cidade inteligente com múltiplos agentes de IA",
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

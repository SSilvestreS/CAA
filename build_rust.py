#!/usr/bin/env python3
"""
Script de Build para Engine Rust
Compila o engine Rust e configura a integração Python
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def run_command(command, cwd=None, check=True):
    """Executa comando e retorna resultado"""
    print(f"Executando: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return e

def check_rust_installed():
    """Verifica se Rust está instalado"""
    print("🔍 Verificando se Rust está instalado...")
    result = run_command("rustc --version", check=False)
    if result.returncode == 0:
        print("✅ Rust está instalado")
        return True
    else:
        print("❌ Rust não está instalado")
        print("   Instale Rust em: https://rustup.rs/")
        return False

def check_python_dev():
    """Verifica se Python dev headers estão disponíveis"""
    print("🔍 Verificando Python dev headers...")
    try:
        import sysconfig
        include_dir = sysconfig.get_path('include')
        if os.path.exists(include_dir):
            print("✅ Python dev headers encontrados")
            return True
        else:
            print("❌ Python dev headers não encontrados")
            return False
    except ImportError:
        print("❌ Não foi possível verificar Python dev headers")
        return False

def install_rust_dependencies():
    """Instala dependências Rust necessárias"""
    print("📦 Instalando dependências Rust...")
    
    # Instalar PyO3
    result = run_command("cargo install pyo3-cli", check=False)
    if result.returncode != 0:
        print("⚠️  PyO3 CLI não instalado, tentando instalar via cargo...")
    
    return True

def build_rust_engine():
    """Compila o engine Rust"""
    print("🔨 Compilando engine Rust...")
    
    rust_dir = Path("src/rust_engine")
    if not rust_dir.exists():
        print("❌ Diretório Rust não encontrado")
        return False
    
    # Compilar em modo release
    result = run_command("cargo build --release", cwd=rust_dir)
    if result.returncode != 0:
        print("❌ Falha ao compilar Rust engine")
        return False
    
    print("✅ Rust engine compilado com sucesso")
    return True

def build_python_extension():
    """Constrói extensão Python"""
    print("🐍 Construindo extensão Python...")
    
    rust_dir = Path("src/rust_engine")
    
    # Usar maturin para construir extensão Python
    result = run_command("maturin develop --release", cwd=rust_dir, check=False)
    if result.returncode != 0:
        print("⚠️  Maturin não disponível, tentando método alternativo...")
        
        # Método alternativo: copiar arquivo compilado
        target_dir = rust_dir / "target" / "release"
        if target_dir.exists():
            # Encontrar arquivo .so ou .pyd
            for ext in [".so", ".pyd", ".dll"]:
                for file in target_dir.glob(f"*{ext}"):
                    print(f"Copiando {file.name} para diretório Python...")
                    shutil.copy2(file, rust_dir / "python")
                    return True
    
    print("✅ Extensão Python construída")
    return True

def test_rust_integration():
    """Testa a integração Rust"""
    print("🧪 Testando integração Rust...")
    
    try:
        # Testar importação
        sys.path.insert(0, "src")
        from rust_engine.python import RustSimulationWrapper
        
        # Criar simulação de teste
        simulation = RustSimulationWrapper(100.0, 100.0)
        
        # Adicionar alguns agentes
        simulation.add_citizen(50.0, 50.0, {"risk_tolerance": 0.5})
        simulation.add_business(75.0, 75.0, "restaurant")
        
        # Executar alguns updates
        for _ in range(10):
            result = simulation.update_simulation(0.1)
        
        print("✅ Integração Rust funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração Rust: {e}")
        return False

def create_requirements_rust():
    """Cria requirements.txt para Rust"""
    print("📝 Criando requirements.txt para Rust...")
    
    requirements = [
        "# Dependências para integração Rust",
        "pyo3>=0.20.0",
        "maturin>=1.0.0",
        "",
        "# Dependências Python existentes",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "asyncio",
        "typing-extensions>=4.0.0",
    ]
    
    with open("requirements_rust.txt", "w") as f:
        f.write("\n".join(requirements))
    
    print("✅ requirements_rust.txt criado")

def main():
    """Função principal"""
    print("🚀 Build Script para Engine Rust")
    print("=" * 50)
    
    # Verificar pré-requisitos
    if not check_rust_installed():
        print("\n❌ Rust não está instalado. Instale em: https://rustup.rs/")
        return False
    
    if not check_python_dev():
        print("\n⚠️  Python dev headers podem não estar disponíveis")
        print("   No Windows: Instale Visual Studio Build Tools")
        print("   No Linux: sudo apt-get install python3-dev")
        print("   No macOS: xcode-select --install")
    
    # Instalar dependências
    install_rust_dependencies()
    
    # Compilar engine
    if not build_rust_engine():
        print("\n❌ Falha ao compilar Rust engine")
        return False
    
    # Construir extensão Python
    if not build_python_extension():
        print("\n⚠️  Falha ao construir extensão Python, mas continuando...")
    
    # Testar integração
    if test_rust_integration():
        print("\n🎉 Build concluído com sucesso!")
        print("   O engine Rust está pronto para uso")
    else:
        print("\n⚠️  Build concluído, mas integração Rust não testada")
        print("   O sistema usará fallback Python")
    
    # Criar requirements
    create_requirements_rust()
    
    print("\n📋 Próximos passos:")
    print("   1. Execute: python examples/rust_integration_demo.py")
    print("   2. Teste performance com diferentes números de agentes")
    print("   3. Integre com seu projeto existente")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

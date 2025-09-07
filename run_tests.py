#!/usr/bin/env python3
"""
Script para executar todos os testes do sistema.
"""

import unittest
import sys
import os
import logging
from pathlib import Path

# Adiciona src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Configura logging para testes
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def discover_and_run_tests():
    """Descobre e executa todos os testes"""
    # Diretório de testes
    test_dir = Path(__file__).parent / "tests"

    # Descobre testes
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern="test_*.py")

    # Executa testes
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, descriptions=True, failfast=False)

    print("=" * 70)
    print("EXECUTANDO TESTES - CIDADES AUTÔNOMAS COM AGENTES DE IA")
    print("=" * 70)
    print(f"Diretório de testes: {test_dir}")
    print(f"Padrão de arquivos: test_*.py")
    print("=" * 70)

    result = runner.run(suite)

    # Resumo dos resultados
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")

    if result.failures:
        print("\nFALHAS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERROS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    print("=" * 70)

    # Retorna código de saída
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_module):
    """Executa teste específico"""
    try:
        # Importa módulo de teste
        module = __import__(f"tests.{test_module}", fromlist=[""])

        # Cria suite de testes
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)

        # Executa testes
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return 0 if result.wasSuccessful() else 1

    except ImportError as e:
        print(f"Erro ao importar módulo de teste: {e}")
        return 1
    except Exception as e:
        print(f"Erro ao executar testes: {e}")
        return 1


def main():
    """Função principal"""
    if len(sys.argv) > 1:
        # Executa teste específico
        test_module = sys.argv[1]
        print(f"Executando teste específico: {test_module}")
        return run_specific_test(test_module)
    else:
        # Executa todos os testes
        return discover_and_run_tests()


if __name__ == "__main__":
    sys.exit(main())

"""
Arquivo principal para executar a simulação de cidade inteligente.
Integra todos os componentes: agentes, ambiente, visualização e cenários.
"""

import asyncio
import argparse
import sys
import os
from typing import Optional

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.environment.city_environment import CityEnvironment
from src.visualization.dashboard import CityDashboard


class SmartCitySimulation:
    """
    Classe principal que coordena a simulação de cidade inteligente.
    """

    def __init__(self, city_name: str = "Cidade Inteligente", city_size: tuple = (100, 100)):
        self.city_name = city_name
        self.city_size = city_size
        self.environment = CityEnvironment(city_name, city_size)
        self.dashboard = None

    async def initialize(self, num_citizens: int = 100, num_businesses: int = 20, num_infrastructure: int = 10):
        """Inicializa a simulação"""
        print("🏙️ Inicializando Simulação de Cidade Inteligente...")
        print("=" * 60)

        # Inicializa a cidade com agentes
        await self.environment.initialize_city(
            num_citizens=num_citizens, num_businesses=num_businesses, num_infrastructure=num_infrastructure
        )

        # Inicializa dashboard
        self.dashboard = CityDashboard(self.environment)

        print("✅ Simulação inicializada com sucesso!")
        print(f"📊 Dashboard disponível em: http://localhost:8050")
        print("=" * 60)

    async def run_simulation(self, duration_hours: Optional[int] = None):
        """Executa a simulação"""
        print("🚀 Iniciando simulação...")

        # Inicia dashboard em thread separada
        import threading

        dashboard_thread = threading.Thread(target=self.dashboard.run, kwargs={"debug": False})
        dashboard_thread.daemon = True
        dashboard_thread.start()

        # Aguarda um pouco para o dashboard inicializar
        await asyncio.sleep(2)

        # Inicia simulação
        try:
            if duration_hours:
                # Executa por tempo limitado
                await asyncio.wait_for(self.environment.start_simulation(), timeout=duration_hours * 3600)
            else:
                # Executa indefinidamente
                await self.environment.start_simulation()
        except asyncio.TimeoutError:
            print(f"⏰ Simulação finalizada após {duration_hours} horas")
        except KeyboardInterrupt:
            print("⏹️ Simulação interrompida pelo usuário")
        finally:
            await self.environment.stop_simulation()
            print("🏁 Simulação finalizada")

    def run_dashboard_only(self):
        """Executa apenas o dashboard (para visualizar simulação salva)"""
        print("📊 Iniciando apenas o dashboard...")
        self.dashboard = CityDashboard(self.environment)
        self.dashboard.run(debug=False)

    def get_status(self):
        """Retorna status atual da simulação"""
        return self.environment.get_city_status()

    def get_agent_data(self):
        """Retorna dados dos agentes"""
        return self.environment.get_agent_data()

    def get_metrics_history(self):
        """Retorna histórico de métricas"""
        return self.environment.get_metrics_history()


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Simulação de Cidade Inteligente")
    parser.add_argument("--citizens", type=int, default=100, help="Número de cidadãos (padrão: 100)")
    parser.add_argument("--businesses", type=int, default=20, help="Número de empresas (padrão: 20)")
    parser.add_argument("--infrastructure", type=int, default=10, help="Número de infraestruturas (padrão: 10)")
    parser.add_argument("--duration", type=int, help="Duração da simulação em horas (padrão: indefinida)")
    parser.add_argument("--dashboard-only", action="store_true", help="Executa apenas o dashboard")
    parser.add_argument("--city-name", type=str, default="Cidade Inteligente", help="Nome da cidade")
    parser.add_argument("--city-size", type=str, default="100,100", help="Tamanho da cidade (largura,altura)")

    args = parser.parse_args()

    # Parse do tamanho da cidade
    try:
        city_size = tuple(map(int, args.city_size.split(",")))
    except ValueError:
        print("❌ Erro: Tamanho da cidade deve ser no formato 'largura,altura'")
        return

    # Cria simulação
    simulation = SmartCitySimulation(city_name=args.city_name, city_size=city_size)

    if args.dashboard_only:
        # Executa apenas dashboard
        simulation.run_dashboard_only()
    else:
        # Inicializa e executa simulação completa
        await simulation.initialize(
            num_citizens=args.citizens, num_businesses=args.businesses, num_infrastructure=args.infrastructure
        )

        await simulation.run_simulation(duration_hours=args.duration)


def run_scenario_example():
    """Exemplo de execução de cenário específico"""
    print("🎯 Executando cenário de exemplo...")

    # Cria simulação com parâmetros específicos
    simulation = SmartCitySimulation("Cidade de Exemplo", (50, 50))

    # Inicializa com menos agentes para exemplo rápido
    asyncio.run(simulation.initialize(num_citizens=50, num_businesses=10, num_infrastructure=5))

    # Executa por 1 hora
    asyncio.run(simulation.run_simulation(duration_hours=1))


if __name__ == "__main__":
    print("🏙️ Cidades Autônomas com Agentes de IA")
    print("=" * 50)
    print("Sistema de simulação multi-agente para cidades inteligentes")
    print("=" * 50)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Simulação finalizada pelo usuário")
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        import traceback

        traceback.print_exc()

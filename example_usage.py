"""
Exemplo de uso da simulação de cidade inteligente.
Demonstra como usar os diferentes componentes do sistema.
"""

import asyncio
import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.environment.city_environment import CityEnvironment
from src.scenarios.scenario_manager import ScenarioManager
from src.ai.collective_learning import CollectiveLearningSystem
from src.visualization.dashboard import CityDashboard


async def basic_simulation_example():
    """Exemplo básico de simulação"""
    print("🏙️ Exemplo Básico de Simulação")
    print("=" * 50)
    
    # Cria ambiente
    environment = CityEnvironment("Cidade de Exemplo", (50, 50))
    
    # Inicializa cidade
    await environment.initialize_city(
        num_citizens=50,
        num_businesses=10,
        num_infrastructure=5
    )
    
    # Executa alguns ciclos
    for i in range(10):
        await environment._simulation_cycle()
        print(f"Ciclo {i+1} - População: {len(environment.citizens)}")
    
    # Exibe status
    status = environment.get_city_status()
    print(f"\nStatus da Cidade:")
    print(f"  População: {status['agents_count']['citizens']}")
    print(f"  Empresas: {status['agents_count']['businesses']}")
    print(f"  Infraestrutura: {status['agents_count']['infrastructure']}")


async def scenario_example():
    """Exemplo de execução de cenários"""
    print("\n🎯 Exemplo de Cenários")
    print("=" * 50)
    
    # Cria ambiente
    environment = CityEnvironment("Cidade de Teste", (30, 30))
    await environment.initialize_city(
        num_citizens=30,
        num_businesses=5,
        num_infrastructure=3
    )
    
    # Cria gerenciador de cenários
    scenario_manager = ScenarioManager(environment)
    
    # Executa cenário de crise energética
    print("Executando cenário: Crise Energética")
    results = await scenario_manager.run_scenario('energy_crisis', duration=20)
    
    print(f"Resultados:")
    for key, value in results.items():
        print(f"  {key}: {value:.3f}")


async def learning_example():
    """Exemplo de sistema de aprendizado coletivo"""
    print("\n🧠 Exemplo de Aprendizado Coletivo")
    print("=" * 50)
    
    # Cria sistema de aprendizado
    learning_system = CollectiveLearningSystem()
    
    # Simula experiências de agentes
    from src.ai.collective_learning import Experience
    import numpy as np
    
    # Adiciona algumas experiências
    for i in range(10):
        experience = Experience(
            state=np.random.rand(20),
            action=i % 3,
            reward=np.random.randn(),
            next_state=np.random.rand(20),
            done=False,
            agent_id=f"citizen_{i}"
        )
        learning_system.add_experience(experience)
    
    # Compartilha conhecimento
    learning_system.share_knowledge(
        "citizen_1", "strategy_a", 0.8, {"context": "high_demand"}
    )
    
    # Exibe estatísticas
    stats = learning_system.get_learning_statistics()
    print(f"Estatísticas de Aprendizado:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def dashboard_example():
    """Exemplo de dashboard (sem executar servidor)"""
    print("\n📊 Exemplo de Dashboard")
    print("=" * 50)
    
    # Cria ambiente
    environment = CityEnvironment("Cidade Dashboard", (40, 40))
    await environment.initialize_city(
        num_citizens=40,
        num_businesses=8,
        num_infrastructure=4
    )
    
    # Cria dashboard
    dashboard = CityDashboard(environment)
    
    print("Dashboard criado com sucesso!")
    print("Para executar o dashboard, use: dashboard.run()")
    
    # Simula alguns ciclos para gerar dados
    for i in range(5):
        await environment._simulation_cycle()
    
    # Exibe dados que seriam mostrados no dashboard
    status = environment.get_city_status()
    print(f"Dados do Dashboard:")
    print(f"  Métricas: {status['metrics']}")


async def complete_example():
    """Exemplo completo integrando todos os componentes"""
    print("\n🚀 Exemplo Completo")
    print("=" * 50)
    
    # Cria ambiente com aprendizado coletivo
    environment = CityEnvironment("Cidade Completa", (60, 60))
    learning_system = CollectiveLearningSystem()
    
    # Inicializa cidade
    await environment.initialize_city(
        num_citizens=60,
        num_businesses=12,
        num_infrastructure=6
    )
    
    # Integra sistema de aprendizado aos agentes
    for citizen in environment.citizens:
        from src.ai.collective_learning import AgentLearningModule
        citizen.learning_module = AgentLearningModule(
            citizen.state.id, "citizen", learning_system
        )
    
    # Executa simulação com cenários
    scenario_manager = ScenarioManager(environment)
    
    # Executa múltiplos cenários
    scenarios = ['economic_boom', 'energy_crisis', 'pandemic']
    
    for scenario in scenarios:
        print(f"Executando cenário: {scenario}")
        results = await scenario_manager.run_scenario(scenario, duration=15)
        
        # Exibe resultados principais
        satisfaction_change = results.get('citizen_satisfaction_change', 0)
        economic_change = results.get('economic_health_change', 0)
        
        print(f"  Mudança na satisfação: {satisfaction_change:.3f}")
        print(f"  Mudança econômica: {economic_change:.3f}")
    
    # Exibe estatísticas finais
    final_status = environment.get_city_status()
    learning_stats = learning_system.get_learning_statistics()
    
    print(f"\nStatus Final:")
    print(f"  População: {final_status['agents_count']['citizens']}")
    print(f"  Satisfação: {final_status['metrics']['citizen_satisfaction']:.1%}")
    print(f"  Saúde Econômica: {final_status['metrics']['economic_health']:.1%}")
    
    print(f"\nEstatísticas de Aprendizado:")
    print(f"  Experiências coletadas: {learning_stats['total_experiences']}")
    print(f"  Estratégias compartilhadas: {learning_stats['shared_strategies']}")


async def main():
    """Executa todos os exemplos"""
    print("🏙️ Exemplos de Uso - Cidade Inteligente")
    print("=" * 60)
    
    try:
        # Exemplo básico
        await basic_simulation_example()
        
        # Exemplo de cenários
        await scenario_example()
        
        # Exemplo de aprendizado
        await learning_example()
        
        # Exemplo de dashboard
        await dashboard_example()
        
        # Exemplo completo
        await complete_example()
        
        print("\n✅ Todos os exemplos executados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro nos exemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

"""
Demonstração interativa da simulação de cidade inteligente.
Executa uma simulação completa com dashboard e cenários.
"""

import asyncio
import sys
import os
import time

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.environment.city_environment import CityEnvironment
from src.scenarios.scenario_manager import ScenarioManager
from src.ai.collective_learning import CollectiveLearningSystem
from src.visualization.dashboard import CityDashboard


class SmartCityDemo:
    """
    Demonstração interativa da simulação de cidade inteligente.
    """
    
    def __init__(self):
        self.environment = None
        self.scenario_manager = None
        self.learning_system = None
        self.dashboard = None
        
    async def initialize_demo(self):
        """Inicializa a demonstração"""
        print("🏙️ DEMONSTRAÇÃO - CIDADES AUTÔNOMAS COM AGENTES DE IA")
        print("=" * 70)
        print("Inicializando simulação de cidade inteligente...")
        
        # Cria ambiente
        self.environment = CityEnvironment("Cidade Demo", (80, 80))
        
        # Inicializa cidade com agentes
        await self.environment.initialize_city(
            num_citizens=80,
            num_businesses=15,
            num_infrastructure=8
        )
        
        # Cria sistema de aprendizado coletivo
        self.learning_system = CollectiveLearningSystem()
        
        # Cria gerenciador de cenários
        self.scenario_manager = ScenarioManager(self.environment)
        
        # Cria dashboard
        self.dashboard = CityDashboard(self.environment)
        
        print("✅ Simulação inicializada com sucesso!")
        print(f"📊 Dashboard disponível em: http://localhost:8050")
        print("=" * 70)
    
    async def run_baseline_simulation(self, duration: int = 50):
        """Executa simulação baseline"""
        print(f"\n🔄 Executando simulação baseline ({duration} ciclos)...")
        
        for i in range(duration):
            await self.environment._simulation_cycle()
            
            if i % 10 == 0:
                status = self.environment.get_city_status()
                print(f"  Ciclo {i+1}: População={status['agents_count']['citizens']}, "
                      f"Satisfação={status['metrics']['citizen_satisfaction']:.1%}")
        
        print("✅ Simulação baseline concluída!")
    
    async def run_scenario_demo(self, scenario_name: str, duration: int = 30):
        """Executa demonstração de cenário"""
        print(f"\n🎯 Demonstração do cenário: {scenario_name}")
        print("-" * 50)
        
        # Captura estado inicial
        initial_status = self.environment.get_city_status()
        print(f"Estado inicial - Satisfação: {initial_status['metrics']['citizen_satisfaction']:.1%}")
        
        # Executa cenário
        results = await self.scenario_manager.run_scenario(scenario_name, duration)
        
        # Captura estado final
        final_status = self.environment.get_city_status()
        print(f"Estado final - Satisfação: {final_status['metrics']['citizen_satisfaction']:.1%}")
        
        # Exibe resultados
        print(f"\n📊 Resultados do cenário:")
        satisfaction_change = results.get('citizen_satisfaction_change', 0)
        economic_change = results.get('economic_health_change', 0)
        
        print(f"  Mudança na satisfação: {satisfaction_change:+.3f}")
        print(f"  Mudança econômica: {economic_change:+.3f}")
        
        if satisfaction_change > 0:
            print("  ✅ Cenário teve impacto positivo na satisfação")
        elif satisfaction_change < 0:
            print("  ❌ Cenário teve impacto negativo na satisfação")
        else:
            print("  ⚖️ Cenário teve impacto neutro na satisfação")
    
    async def run_learning_demo(self):
        """Demonstra sistema de aprendizado coletivo"""
        print(f"\n🧠 Demonstração do Sistema de Aprendizado Coletivo")
        print("-" * 50)
        
        # Simula experiências de aprendizado
        from src.ai.collective_learning import Experience
        import numpy as np
        
        print("Simulando experiências de agentes...")
        
        # Adiciona experiências variadas
        for i in range(20):
            experience = Experience(
                state=np.random.rand(20),
                action=i % 4,
                reward=np.random.randn() * 0.5,
                next_state=np.random.rand(20),
                done=False,
                agent_id=f"citizen_{i % 10}"
            )
            self.learning_system.add_experience(experience)
        
        # Compartilha conhecimento
        print("Compartilhando conhecimento entre agentes...")
        self.learning_system.share_knowledge(
            "citizen_1", "estratégia_otimista", 0.85, 
            {"contexto": "alta_demanda", "setor": "transporte"}
        )
        self.learning_system.share_knowledge(
            "citizen_2", "estratégia_conservadora", 0.75,
            {"contexto": "baixa_demanda", "setor": "energia"}
        )
        
        # Exibe estatísticas
        stats = self.learning_system.get_learning_statistics()
        print(f"\n📈 Estatísticas de Aprendizado:")
        print(f"  Experiências coletadas: {stats['total_experiences']}")
        print(f"  Estratégias compartilhadas: {stats['shared_strategies']}")
        print(f"  Conhecimento ativo: {stats['active_knowledge']}")
        print(f"  Taxa de sucesso: {stats['success_rate']:.1%}")
    
    async def run_comparative_analysis(self):
        """Executa análise comparativa de cenários"""
        print(f"\n📊 Análise Comparativa de Cenários")
        print("-" * 50)
        
        scenarios = [
            ('economic_boom', 'Boom Econômico'),
            ('energy_crisis', 'Crise Energética'),
            ('pandemic', 'Pandemia'),
            ('environmental_regulation', 'Regulamentação Ambiental')
        ]
        
        results = {}
        
        for scenario_key, scenario_name in scenarios:
            print(f"\n🔄 Testando: {scenario_name}")
            
            # Executa cenário
            scenario_results = await self.scenario_manager.run_scenario(scenario_key, 20)
            results[scenario_name] = scenario_results
            
            # Exibe resultado principal
            satisfaction_change = scenario_results.get('citizen_satisfaction_change', 0)
            print(f"  Impacto na satisfação: {satisfaction_change:+.3f}")
        
        # Análise comparativa
        print(f"\n📈 Análise Comparativa:")
        print("-" * 30)
        
        best_scenario = max(results.items(), 
                          key=lambda x: x[1].get('citizen_satisfaction_change', 0))
        worst_scenario = min(results.items(), 
                           key=lambda x: x[1].get('citizen_satisfaction_change', 0))
        
        print(f"✅ Melhor cenário: {best_scenario[0]}")
        print(f"   Impacto: {best_scenario[1].get('citizen_satisfaction_change', 0):+.3f}")
        
        print(f"❌ Pior cenário: {worst_scenario[0]}")
        print(f"   Impacto: {worst_scenario[1].get('citizen_satisfaction_change', 0):+.3f}")
    
    def display_final_statistics(self):
        """Exibe estatísticas finais"""
        print(f"\n🏁 ESTATÍSTICAS FINAIS")
        print("=" * 50)
        
        # Status da cidade
        status = self.environment.get_city_status()
        print(f"📊 Status da Cidade:")
        print(f"  População: {status['agents_count']['citizens']}")
        print(f"  Empresas: {status['agents_count']['businesses']}")
        print(f"  Infraestrutura: {status['agents_count']['infrastructure']}")
        print(f"  Eventos ativos: {status['active_events']}")
        
        # Métricas
        metrics = status['metrics']
        print(f"\n📈 Métricas de Qualidade:")
        print(f"  Satisfação cidadã: {metrics['citizen_satisfaction']:.1%}")
        print(f"  Saúde econômica: {metrics['economic_health']:.1%}")
        print(f"  Saúde da infraestrutura: {metrics['infrastructure_health']:.1%}")
        print(f"  Saúde ambiental: {metrics['environmental_health']:.1%}")
        
        # Estatísticas de aprendizado
        if self.learning_system:
            learning_stats = self.learning_system.get_learning_statistics()
            print(f"\n🧠 Estatísticas de Aprendizado:")
            print(f"  Experiências coletadas: {learning_stats['total_experiences']}")
            print(f"  Estratégias compartilhadas: {learning_stats['shared_strategies']}")
            print(f"  Taxa de sucesso: {learning_stats['success_rate']:.1%}")
        
        # Histórico de cenários
        if self.scenario_manager:
            scenario_results = self.scenario_manager.get_all_scenario_results()
            print(f"\n🎯 Cenários Executados: {len(scenario_results)}")
    
    async def run_interactive_demo(self):
        """Executa demonstração interativa"""
        print("🎮 MODO INTERATIVO")
        print("=" * 30)
        print("Escolha uma opção:")
        print("1. Simulação baseline")
        print("2. Cenário de crise energética")
        print("3. Cenário de boom econômico")
        print("4. Demonstração de aprendizado")
        print("5. Análise comparativa")
        print("6. Executar todos")
        print("0. Sair")
        
        while True:
            try:
                choice = input("\nDigite sua escolha (0-6): ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    await self.run_baseline_simulation(30)
                elif choice == '2':
                    await self.run_scenario_demo('energy_crisis', 25)
                elif choice == '3':
                    await self.run_scenario_demo('economic_boom', 25)
                elif choice == '4':
                    await self.run_learning_demo()
                elif choice == '5':
                    await self.run_comparative_analysis()
                elif choice == '6':
                    await self.run_complete_demo()
                    break
                else:
                    print("❌ Opção inválida. Tente novamente.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demonstração interrompida.")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    async def run_complete_demo(self):
        """Executa demonstração completa"""
        print("\n🚀 EXECUTANDO DEMONSTRAÇÃO COMPLETA")
        print("=" * 50)
        
        # 1. Simulação baseline
        await self.run_baseline_simulation(40)
        
        # 2. Demonstração de aprendizado
        await self.run_learning_demo()
        
        # 3. Cenários diversos
        scenarios = ['economic_boom', 'energy_crisis', 'pandemic']
        for scenario in scenarios:
            await self.run_scenario_demo(scenario, 20)
        
        # 4. Análise comparativa
        await self.run_comparative_analysis()
        
        # 5. Estatísticas finais
        self.display_final_statistics()
        
        print("\n🎉 Demonstração completa finalizada!")
        print("📊 Acesse o dashboard em: http://localhost:8050")


async def main():
    """Função principal da demonstração"""
    demo = SmartCityDemo()
    
    try:
        # Inicializa demonstração
        await demo.initialize_demo()
        
        # Pergunta se quer modo interativo
        print("\n🎮 Deseja executar em modo interativo? (s/n): ", end="")
        try:
            interactive = input().strip().lower() == 's'
        except:
            interactive = False
        
        if interactive:
            await demo.run_interactive_demo()
        else:
            await demo.run_complete_demo()
        
    except KeyboardInterrupt:
        print("\n👋 Demonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🏁 Demonstração finalizada. Obrigado!")


if __name__ == "__main__":
    print("🎯 DEMONSTRAÇÃO - CIDADES AUTÔNOMAS COM AGENTES DE IA")
    print("Sistema de simulação multi-agente para cidades inteligentes")
    print("=" * 70)
    
    asyncio.run(main())

"""
Script para executar cenários específicos da simulação de cidade inteligente.
Permite testar diferentes situações e políticas públicas.
"""

import asyncio
import argparse
import sys
import os
from typing import List

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.environment.city_environment import CityEnvironment
from src.scenarios.scenario_manager import ScenarioManager


async def run_single_scenario(scenario_name: str, duration: int = 100, 
                            city_size: tuple = (50, 50)):
    """Executa um cenário específico"""
    print(f"🎯 Executando cenário: {scenario_name}")
    print("=" * 60)
    
    # Cria ambiente
    environment = CityEnvironment("Cidade de Teste", city_size)
    
    # Inicializa cidade
    await environment.initialize_city(
        num_citizens=50,
        num_businesses=10,
        num_infrastructure=5
    )
    
    # Cria gerenciador de cenários
    scenario_manager = ScenarioManager(environment)
    
    # Executa cenário
    results = await scenario_manager.run_scenario(scenario_name, duration)
    
    # Exibe resultados
    print("\n📊 Resultados do Cenário:")
    print("-" * 40)
    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
    
    return results


async def run_multiple_scenarios(scenario_names: List[str], duration: int = 100):
    """Executa múltiplos cenários e compara resultados"""
    print("🎯 Executando múltiplos cenários")
    print("=" * 60)
    
    all_results = {}
    
    for scenario_name in scenario_names:
        print(f"\n🔄 Executando: {scenario_name}")
        results = await run_single_scenario(scenario_name, duration)
        all_results[scenario_name] = results
    
    # Compara resultados
    print("\n📈 Comparação de Resultados:")
    print("=" * 60)
    
    # Métricas para comparar
    metrics_to_compare = [
        'citizen_satisfaction_change',
        'economic_health_change',
        'infrastructure_health_change',
        'environmental_health_change'
    ]
    
    for metric in metrics_to_compare:
        print(f"\n{metric.replace('_', ' ').title()}:")
        for scenario, results in all_results.items():
            value = results.get(metric, 0)
            print(f"  {scenario}: {value:.3f}")
    
    return all_results


async def run_policy_comparison():
    """Executa comparação de políticas públicas"""
    print("🏛️ Comparação de Políticas Públicas")
    print("=" * 60)
    
    policies = [
        'tax_increase',
        'environmental_regulation',
        'social_inequality'
    ]
    
    results = await run_multiple_scenarios(policies, duration=50)
    
    # Análise específica de políticas
    print("\n🏛️ Análise de Políticas:")
    print("-" * 40)
    
    for policy, results in results.items():
        satisfaction_impact = results.get('citizen_satisfaction_change', 0)
        economic_impact = results.get('economic_health_change', 0)
        
        print(f"\n{policy.replace('_', ' ').title()}:")
        print(f"  Impacto na satisfação: {satisfaction_impact:.3f}")
        print(f"  Impacto econômico: {economic_impact:.3f}")
        
        if satisfaction_impact > 0 and economic_impact > 0:
            print("  ✅ Política benéfica")
        elif satisfaction_impact < 0 and economic_impact < 0:
            print("  ❌ Política prejudicial")
        else:
            print("  ⚖️ Política com trade-offs")


async def run_crisis_scenarios():
    """Executa cenários de crise"""
    print("🚨 Cenários de Crise")
    print("=" * 60)
    
    crises = [
        'energy_crisis',
        'pandemic',
        'infrastructure_failure'
    ]
    
    results = await run_multiple_scenarios(crises, duration=30)
    
    # Análise de resiliência
    print("\n🛡️ Análise de Resiliência:")
    print("-" * 40)
    
    for crisis, results in results.items():
        satisfaction_recovery = results.get('citizen_satisfaction_change', 0)
        economic_recovery = results.get('economic_health_change', 0)
        
        print(f"\n{crisis.replace('_', ' ').title()}:")
        print(f"  Recuperação da satisfação: {satisfaction_recovery:.3f}")
        print(f"  Recuperação econômica: {economic_recovery:.3f}")
        
        resilience_score = (satisfaction_recovery + economic_recovery) / 2
        if resilience_score > 0.1:
            print("  🟢 Alta resiliência")
        elif resilience_score > -0.1:
            print("  🟡 Resiliência moderada")
        else:
            print("  🔴 Baixa resiliência")


async def run_innovation_scenarios():
    """Executa cenários de inovação tecnológica"""
    print("🚀 Cenários de Inovação")
    print("=" * 60)
    
    innovations = [
        'autonomous_transport',
        'smart_grid'
    ]
    
    results = await run_multiple_scenarios(innovations, duration=80)
    
    # Análise de inovação
    print("\n💡 Análise de Inovação:")
    print("-" * 40)
    
    for innovation, results in results.items():
        satisfaction_impact = results.get('citizen_satisfaction_change', 0)
        economic_impact = results.get('economic_health_change', 0)
        environmental_impact = results.get('environmental_health_change', 0)
        
        print(f"\n{innovation.replace('_', ' ').title()}:")
        print(f"  Impacto na satisfação: {satisfaction_impact:.3f}")
        print(f"  Impacto econômico: {economic_impact:.3f}")
        print(f"  Impacto ambiental: {environmental_impact:.3f}")
        
        innovation_score = (satisfaction_impact + economic_impact + environmental_impact) / 3
        if innovation_score > 0.1:
            print("  ✅ Inovação altamente benéfica")
        elif innovation_score > 0:
            print("  ✅ Inovação benéfica")
        else:
            print("  ⚠️ Inovação com impactos mistos")


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar cenários da simulação")
    parser.add_argument("--scenario", type=str, 
                       help="Nome do cenário para executar")
    parser.add_argument("--duration", type=int, default=100,
                       help="Duração do cenário em ciclos")
    parser.add_argument("--list", action="store_true",
                       help="Lista cenários disponíveis")
    parser.add_argument("--policies", action="store_true",
                       help="Executa comparação de políticas")
    parser.add_argument("--crises", action="store_true",
                       help="Executa cenários de crise")
    parser.add_argument("--innovations", action="store_true",
                       help="Executa cenários de inovação")
    parser.add_argument("--all", action="store_true",
                       help="Executa todos os cenários")
    
    args = parser.parse_args()
    
    # Cria ambiente temporário para listar cenários
    temp_env = CityEnvironment("temp", (10, 10))
    scenario_manager = ScenarioManager(temp_env)
    
    if args.list:
        print("📋 Cenários Disponíveis:")
        print("=" * 40)
        for scenario in scenario_manager.get_available_scenarios():
            description = scenario_manager.get_scenario_description(scenario)
            print(f"• {scenario}: {description}")
        return
    
    if args.scenario:
        # Executa cenário específico
        if args.scenario not in scenario_manager.get_available_scenarios():
            print(f"❌ Cenário '{args.scenario}' não encontrado")
            print("Use --list para ver cenários disponíveis")
            return
        
        await run_single_scenario(args.scenario, args.duration)
    
    elif args.policies:
        await run_policy_comparison()
    
    elif args.crises:
        await run_crisis_scenarios()
    
    elif args.innovations:
        await run_innovation_scenarios()
    
    elif args.all:
        print("🎯 Executando todos os cenários")
        all_scenarios = scenario_manager.get_available_scenarios()
        await run_multiple_scenarios(all_scenarios, args.duration)
    
    else:
        print("❌ Especifique um cenário ou opção")
        print("Use --help para ver opções disponíveis")


if __name__ == "__main__":
    print("🎯 Executor de Cenários - Cidade Inteligente")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Execução interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        import traceback
        traceback.print_exc()

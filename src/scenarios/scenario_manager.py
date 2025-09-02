"""
Gerenciador de cenários para testar diferentes situações na cidade inteligente.
Implementa cenários como políticas públicas, crises, trânsito autônomo, etc.
"""

import asyncio
import random
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import numpy as np

from ..environment.city_environment import CityEnvironment, MarketEvent


class ScenarioManager:
    """
    Gerenciador de cenários para testar diferentes situações na simulação.
    """
    
    def __init__(self, environment: CityEnvironment):
        self.environment = environment
        self.active_scenarios = []
        self.scenario_history = []
        
    async def run_scenario(self, scenario_name: str, duration_cycles: int = 100) -> Dict[str, Any]:
        """
        Executa um cenário específico e retorna resultados.
        """
        print(f"🎯 Executando cenário: {scenario_name}")
        
        # Salva estado inicial
        initial_state = self._capture_initial_state()
        
        # Executa cenário
        scenario_func = self._get_scenario_function(scenario_name)
        if scenario_func:
            await scenario_func(duration_cycles)
        else:
            print(f"❌ Cenário '{scenario_name}' não encontrado")
            return {}
        
        # Captura estado final
        final_state = self._capture_final_state()
        
        # Calcula resultados
        results = self._calculate_scenario_results(initial_state, final_state)
        
        # Salva no histórico
        self.scenario_history.append({
            'name': scenario_name,
            'duration': duration_cycles,
            'initial_state': initial_state,
            'final_state': final_state,
            'results': results,
            'timestamp': datetime.now()
        })
        
        print(f"✅ Cenário '{scenario_name}' finalizado")
        return results
    
    def _get_scenario_function(self, scenario_name: str) -> Optional[Callable]:
        """Retorna função do cenário baseada no nome"""
        scenarios = {
            'tax_increase': self._scenario_tax_increase,
            'energy_crisis': self._scenario_energy_crisis,
            'pandemic': self._scenario_pandemic,
            'economic_boom': self._scenario_economic_boom,
            'infrastructure_failure': self._scenario_infrastructure_failure,
            'population_growth': self._scenario_population_growth,
            'environmental_regulation': self._scenario_environmental_regulation,
            'autonomous_transport': self._scenario_autonomous_transport,
            'smart_grid': self._scenario_smart_grid,
            'social_inequality': self._scenario_social_inequality
        }
        return scenarios.get(scenario_name)
    
    def _capture_initial_state(self) -> Dict[str, Any]:
        """Captura estado inicial da cidade"""
        return {
            'metrics': self.environment.city_metrics.__dict__.copy(),
            'agents_count': {
                'citizens': len(self.environment.citizens),
                'businesses': len(self.environment.businesses),
                'infrastructure': len(self.environment.infrastructure)
            },
            'active_events': len(self.environment.active_events)
        }
    
    def _capture_final_state(self) -> Dict[str, Any]:
        """Captura estado final da cidade"""
        return {
            'metrics': self.environment.city_metrics.__dict__.copy(),
            'agents_count': {
                'citizens': len(self.environment.citizens),
                'businesses': len(self.environment.businesses),
                'infrastructure': len(self.environment.infrastructure)
            },
            'active_events': len(self.environment.active_events)
        }
    
    def _calculate_scenario_results(self, initial: Dict, final: Dict) -> Dict[str, Any]:
        """Calcula resultados do cenário"""
        results = {}
        
        # Compara métricas
        for metric in ['population', 'citizen_satisfaction', 'economic_health', 
                      'infrastructure_health', 'environmental_health']:
            initial_val = initial['metrics'].get(metric, 0)
            final_val = final['metrics'].get(metric, 0)
            change = final_val - initial_val
            results[f'{metric}_change'] = change
            results[f'{metric}_change_percent'] = (change / initial_val * 100) if initial_val != 0 else 0
        
        # Compara contagem de agentes
        for agent_type in ['citizens', 'businesses', 'infrastructure']:
            initial_count = initial['agents_count'].get(agent_type, 0)
            final_count = final['agents_count'].get(agent_type, 0)
            results[f'{agent_type}_change'] = final_count - initial_count
        
        return results
    
    # ==================== CENÁRIOS ESPECÍFICOS ====================
    
    async def _scenario_tax_increase(self, duration: int):
        """Cenário: Aumento de impostos"""
        print("📈 Cenário: Aumento de Impostos")
        
        # Aumenta taxa de impostos
        for government in self.environment.governments:
            old_tax_rate = government.policies['tax_rate']
            government.policies['tax_rate'] = min(0.5, old_tax_rate + 0.1)
            print(f"  Taxa de impostos: {old_tax_rate:.1%} → {government.policies['tax_rate']:.1%}")
        
        # Executa simulação
        await self._run_scenario_cycles(duration)
    
    async def _scenario_energy_crisis(self, duration: int):
        """Cenário: Crise energética"""
        print("⚡ Cenário: Crise Energética")
        
        # Cria evento de crise energética
        energy_crisis = MarketEvent(
            event_type="energy_crisis",
            description="Crise energética severa - preços altos e escassez",
            impact={
                "energy_prices": 0.8,
                "production": -0.4,
                "transport": -0.5,
                "citizen_satisfaction": -0.3
            },
            duration=duration,
            probability=1.0
        )
        
        await self.environment._activate_event(energy_crisis)
        await self._run_scenario_cycles(duration)
    
    async def _scenario_pandemic(self, duration: int):
        """Cenário: Pandemia"""
        print("🦠 Cenário: Pandemia")
        
        # Cria evento de pandemia
        pandemic = MarketEvent(
            event_type="pandemic",
            description="Pandemia global - lockdown e redução de atividade",
            impact={
                "demand": -0.6,
                "healthcare": 0.8,
                "transport": -0.7,
                "citizen_satisfaction": -0.4,
                "economic_health": -0.5
            },
            duration=duration,
            probability=1.0
        )
        
        await self.environment._activate_event(pandemic)
        await self._run_scenario_cycles(duration)
    
    async def _scenario_economic_boom(self, duration: int):
        """Cenário: Boom econômico"""
        print("📈 Cenário: Boom Econômico")
        
        # Cria evento de boom econômico
        boom = MarketEvent(
            event_type="economic_boom",
            description="Boom econômico - alta demanda e crescimento",
            impact={
                "demand": 0.5,
                "prices": 0.2,
                "employment": 0.3,
                "citizen_satisfaction": 0.2,
                "economic_health": 0.4
            },
            duration=duration,
            probability=1.0
        )
        
        await self.environment._activate_event(boom)
        await self._run_scenario_cycles(duration)
    
    async def _scenario_infrastructure_failure(self, duration: int):
        """Cenário: Falha de infraestrutura"""
        print("🏗️ Cenário: Falha de Infraestrutura")
        
        # Simula falha em sistemas de infraestrutura
        for infrastructure in self.environment.infrastructure:
            if random.random() < 0.3:  # 30% chance de falha
                infrastructure.system_status['operational'] = False
                infrastructure.efficiency *= 0.5
                print(f"  Falha em: {infrastructure.name}")
        
        await self._run_scenario_cycles(duration)
    
    async def _scenario_population_growth(self, duration: int):
        """Cenário: Crescimento populacional"""
        print("👥 Cenário: Crescimento Populacional")
        
        # Adiciona novos cidadãos
        new_citizens = 20
        for i in range(new_citizens):
            from ..agents.citizen_agent import CitizenAgent
            position = self.environment._generate_random_position()
            citizen = CitizenAgent(
                name=f"Novo_Cidadão_{i+1}",
                position=position
            )
            await self.environment.add_agent(citizen)
        
        print(f"  Adicionados {new_citizens} novos cidadãos")
        await self._run_scenario_cycles(duration)
    
    async def _scenario_environmental_regulation(self, duration: int):
        """Cenário: Regulamentação ambiental"""
        print("🌱 Cenário: Regulamentação Ambiental")
        
        # Aumenta regulamentações ambientais
        for government in self.environment.governments:
            old_reg = government.policies['environmental_regulations']
            government.policies['environmental_regulations'] = min(1.0, old_reg + 0.3)
            print(f"  Regulamentação ambiental: {old_reg:.1%} → {government.policies['environmental_regulations']:.1%}")
        
        # Impacta empresas
        for business in self.environment.businesses:
            business.operating_cost *= 1.2  # Aumenta custos
            business.efficiency *= 0.9  # Reduz eficiência temporariamente
        
        await self._run_scenario_cycles(duration)
    
    async def _scenario_autonomous_transport(self, duration: int):
        """Cenário: Transporte autônomo"""
        print("🚗 Cenário: Transporte Autônomo")
        
        # Melhora eficiência do transporte
        for infrastructure in self.environment.infrastructure:
            if infrastructure.infrastructure_type == 'transport':
                infrastructure.efficiency *= 1.3
                infrastructure.operating_cost *= 0.8
                print(f"  Transporte autônomo ativado em: {infrastructure.name}")
        
        # Cria evento de inovação
        innovation = MarketEvent(
            event_type="technological_breakthrough",
            description="Transporte autônomo - redução de custos e acidentes",
            impact={
                "transport_efficiency": 0.3,
                "transport_costs": -0.2,
                "citizen_satisfaction": 0.1,
                "economic_health": 0.1
            },
            duration=duration,
            probability=1.0
        )
        
        await self.environment._activate_event(innovation)
        await self._run_scenario_cycles(duration)
    
    async def _scenario_smart_grid(self, duration: int):
        """Cenário: Smart Grid (rede elétrica inteligente)"""
        print("⚡ Cenário: Smart Grid")
        
        # Melhora eficiência energética
        for infrastructure in self.environment.infrastructure:
            if infrastructure.infrastructure_type == 'energy':
                infrastructure.efficiency *= 1.4
                infrastructure.optimization_algorithms['energy_optimization'] = True
                print(f"  Smart Grid ativado em: {infrastructure.name}")
        
        # Cria evento de inovação energética
        smart_grid = MarketEvent(
            event_type="technological_breakthrough",
            description="Smart Grid - otimização energética inteligente",
            impact={
                "energy_efficiency": 0.4,
                "energy_costs": -0.3,
                "environmental_health": 0.2,
                "citizen_satisfaction": 0.1
            },
            duration=duration,
            probability=1.0
        )
        
        await self.environment._activate_event(smart_grid)
        await self._run_scenario_cycles(duration)
    
    async def _scenario_social_inequality(self, duration: int):
        """Cenário: Aumento da desigualdade social"""
        print("⚖️ Cenário: Desigualdade Social")
        
        # Aumenta desigualdade entre cidadãos
        for citizen in self.environment.citizens:
            if random.random() < 0.3:  # 30% dos cidadãos ficam mais pobres
                citizen.income *= 0.7
                citizen.stress_level += 0.2
            elif random.random() < 0.1:  # 10% ficam mais ricos
                citizen.income *= 1.5
                citizen.stress_level -= 0.1
        
        # Cria evento de desigualdade
        inequality = MarketEvent(
            event_type="social_inequality",
            description="Aumento da desigualdade social",
            impact={
                "social_stability": -0.3,
                "crime_rate": 0.2,
                "citizen_satisfaction": -0.2,
                "economic_health": -0.1
            },
            duration=duration,
            probability=1.0
        )
        
        await self.environment._activate_event(inequality)
        await self._run_scenario_cycles(duration)
    
    async def _run_scenario_cycles(self, duration: int):
        """Executa ciclos da simulação para o cenário"""
        for cycle in range(duration):
            # Executa um ciclo da simulação
            await self.environment._simulation_cycle()
            
            # Log de progresso
            if cycle % 20 == 0:
                print(f"  Ciclo {cycle}/{duration} - {self.environment.simulation_time}")
    
    def get_available_scenarios(self) -> List[str]:
        """Retorna lista de cenários disponíveis"""
        return [
            'tax_increase',
            'energy_crisis',
            'pandemic',
            'economic_boom',
            'infrastructure_failure',
            'population_growth',
            'environmental_regulation',
            'autonomous_transport',
            'smart_grid',
            'social_inequality'
        ]
    
    def get_scenario_description(self, scenario_name: str) -> str:
        """Retorna descrição do cenário"""
        descriptions = {
            'tax_increase': 'Testa o impacto de um aumento de impostos na economia e satisfação cidadã',
            'energy_crisis': 'Simula uma crise energética com preços altos e escassez',
            'pandemic': 'Simula uma pandemia com lockdown e redução de atividade econômica',
            'economic_boom': 'Testa um boom econômico com alta demanda e crescimento',
            'infrastructure_failure': 'Simula falhas em sistemas de infraestrutura crítica',
            'population_growth': 'Testa o impacto do crescimento populacional na cidade',
            'environmental_regulation': 'Simula implementação de regulamentações ambientais',
            'autonomous_transport': 'Testa a implementação de transporte autônomo',
            'smart_grid': 'Simula implementação de rede elétrica inteligente',
            'social_inequality': 'Testa o impacto do aumento da desigualdade social'
        }
        return descriptions.get(scenario_name, 'Cenário não encontrado')
    
    def get_scenario_results(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Retorna resultados de um cenário específico"""
        for scenario in self.scenario_history:
            if scenario['name'] == scenario_name:
                return scenario['results']
        return None
    
    def get_all_scenario_results(self) -> List[Dict[str, Any]]:
        """Retorna resultados de todos os cenários executados"""
        return [
            {
                'name': scenario['name'],
                'timestamp': scenario['timestamp'].isoformat(),
                'duration': scenario['duration'],
                'results': scenario['results']
            }
            for scenario in self.scenario_history
        ]

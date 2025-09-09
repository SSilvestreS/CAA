"""
Ambiente da Cidade - Coordena a simulação de todos os agentes.
Gerencia interações, eventos aleatórios e mecânicas de mercado.
"""

import asyncio
import random
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass, field
import json

from ..agents.base_agent import BaseAgent
from ..agents.citizen_agent import CitizenAgent
from ..agents.business_agent import BusinessAgent
from ..agents.government_agent import GovernmentAgent
from ..agents.infrastructure_agent import InfrastructureAgent


@dataclass
class CityMetrics:
    """Métricas agregadas da cidade"""

    population: int = 0
    total_income: float = 0.0
    unemployment_rate: float = 0.0
    crime_rate: float = 0.0
    environmental_health: float = 0.0
    citizen_satisfaction: float = 0.0
    economic_health: float = 0.0
    infrastructure_health: float = 0.0
    government_efficiency: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MarketEvent:
    """Evento de mercado"""

    event_type: str
    description: str
    impact: Dict[str, float]  # Impacto em diferentes setores
    duration: int  # Duração em ciclos
    probability: float  # Probabilidade de ocorrência
    timestamp: datetime = field(default_factory=datetime.now)


class CityEnvironment:
    """
    Ambiente principal que coordena a simulação da cidade inteligente.
    Gerencia agentes, eventos, mercado e interações.
    """

    def __init__(
        self,
        city_name: str = "Cidade Inteligente",
        city_size: tuple = (100, 100),
        **kwargs,
    ):
        self.city_name = city_name
        self.city_size = city_size

        # Agentes da cidade
        self.agents: List[BaseAgent] = []
        self.citizens: List[CitizenAgent] = []
        self.businesses: List[BusinessAgent] = []
        self.governments: List[GovernmentAgent] = []
        self.infrastructure: List[InfrastructureAgent] = []

        # Estado da simulação
        self.simulation_time = datetime.now()
        self.simulation_speed = 1.0  # Multiplicador de velocidade
        self.is_running = False
        self.cycle_count = 0

        # Eventos e mercado
        self.market_events: List[MarketEvent] = []
        self.active_events: List[MarketEvent] = []
        self.event_history: List[MarketEvent] = []

        # Métricas da cidade
        self.city_metrics = CityMetrics()
        self.metrics_history: List[CityMetrics] = []

        # Configurações
        self.config = {
            "max_agents": 1000,
            "event_probability": 0.1,  # Probabilidade de evento por ciclo
            "market_update_frequency": 5,  # Atualiza mercado a cada N ciclos
            "metrics_update_frequency": 10,  # Atualiza métricas a cada N ciclos
            "save_frequency": 100,  # Salva estado a cada N ciclos
        }

        # Sistema de aprendizado coletivo
        self.collective_memory = {
            "successful_strategies": [],
            "failed_strategies": [],
            "market_patterns": [],
            "crisis_responses": [],
        }

        # Inicializa eventos de mercado
        self._initialize_market_events()

    def _initialize_market_events(self) -> None:
        """Inicializa eventos de mercado possíveis"""
        self.market_events = [
            MarketEvent(
                event_type="economic_boom",
                description="Boom econômico - aumento na demanda",
                impact={"demand": 0.3, "prices": 0.1, "employment": 0.2},
                duration=20,
                probability=0.05,
            ),
            MarketEvent(
                event_type="economic_recession",
                description="Recessão econômica - queda na demanda",
                impact={"demand": -0.3, "prices": -0.2, "employment": -0.3},
                duration=30,
                probability=0.08,
            ),
            MarketEvent(
                event_type="energy_crisis",
                description="Crise energética - aumento nos preços de energia",
                impact={"energy_prices": 0.5, "production": -0.2, "transport": -0.3},
                duration=15,
                probability=0.06,
            ),
            MarketEvent(
                event_type="pandemic",
                description="Pandemia - redução na atividade econômica",
                impact={"demand": -0.4, "healthcare": 0.6, "transport": -0.5},
                duration=50,
                probability=0.03,
            ),
            MarketEvent(
                event_type="natural_disaster",
                description="Desastre natural - danos à infraestrutura",
                impact={"infrastructure": -0.4, "insurance": 0.3, "construction": 0.4},
                duration=25,
                probability=0.04,
            ),
            MarketEvent(
                event_type="technological_breakthrough",
                description="Avance tecnológico - aumento na eficiência",
                impact={"efficiency": 0.3, "innovation": 0.4, "costs": -0.2},
                duration=40,
                probability=0.07,
            ),
            MarketEvent(
                event_type="population_growth",
                description="Crescimento populacional - aumento na demanda",
                impact={"demand": 0.2, "housing": 0.3, "services": 0.2},
                duration=60,
                probability=0.06,
            ),
            MarketEvent(
                event_type="environmental_regulation",
                description="Nova regulamentação ambiental",
                impact={
                    "environmental_costs": 0.3,
                    "innovation": 0.2,
                    "compliance": 0.4,
                },
                duration=100,
                probability=0.05,
            ),
        ]

    async def add_agent(self, agent: BaseAgent) -> None:
        """Adiciona agente ao ambiente"""
        agent.environment = self
        self.agents.append(agent)

        # Adiciona à lista específica baseada no tipo
        if isinstance(agent, CitizenAgent):
            self.citizens.append(agent)
        elif isinstance(agent, BusinessAgent):
            self.businesses.append(agent)
        elif isinstance(agent, GovernmentAgent):
            self.governments.append(agent)
        elif isinstance(agent, InfrastructureAgent):
            self.infrastructure.append(agent)

    async def remove_agent(self, agent: BaseAgent) -> None:
        """Remove agente do ambiente"""
        if agent in self.agents:
            self.agents.remove(agent)

            # Remove da lista específica
            if isinstance(agent, CitizenAgent) and agent in self.citizens:
                self.citizens.remove(agent)
            elif isinstance(agent, BusinessAgent) and agent in self.businesses:
                self.businesses.remove(agent)
            elif isinstance(agent, GovernmentAgent) and agent in self.governments:
                self.governments.remove(agent)
            elif (
                isinstance(agent, InfrastructureAgent) and agent in self.infrastructure
            ):
                self.infrastructure.remove(agent)

    async def initialize_city(
        self,
        num_citizens: int = 100,
        num_businesses: int = 20,
        num_infrastructure: int = 10,
    ) -> None:
        """Inicializa a cidade com agentes"""
        print(f"Inicializando {self.city_name}...")

        # Cria cidadãos
        for i in range(num_citizens):
            position = self._generate_random_position()
            citizen = CitizenAgent(name=f"Cidadão_{i + 1}", position=position)
            await self.add_agent(citizen)

        # Cria empresas
        business_types = [
            "energy",
            "food",
            "transport",
            "healthcare",
            "entertainment",
            "housing",
        ]
        for i in range(num_businesses):
            position = self._generate_random_position()
            business_type = random.choice(business_types)
            business = BusinessAgent(
                name=f"Empresa_{business_type}_{i + 1}",
                business_type=business_type,
                position=position,
            )
            await self.add_agent(business)

        # Cria infraestrutura
        infrastructure_types = [
            "energy",
            "transport",
            "water",
            "healthcare",
            "communication",
        ]
        for i in range(num_infrastructure):
            position = self._generate_random_position()
            infra_type = random.choice(infrastructure_types)
            infrastructure = InfrastructureAgent(
                name=f"Infraestrutura_{infra_type}_{i + 1}",
                infrastructure_type=infra_type,
                position=position,
            )
            await self.add_agent(infrastructure)

        # Cria governo
        government = GovernmentAgent(
            name="Governo Municipal",
            position=(self.city_size[0] // 2, self.city_size[1] // 2),
        )
        await self.add_agent(government)

        print(f"Cidade inicializada com {len(self.agents)} agentes:")
        print(f"  - {len(self.citizens)} cidadãos")
        print(f"  - {len(self.businesses)} empresas")
        print(f"  - {len(self.infrastructure)} infraestruturas")
        print(f"  - {len(self.governments)} governos")

    def _generate_random_position(self) -> Tuple[int, int]:
        """Gera posição aleatória na cidade"""
        x = random.randint(0, self.city_size[0] - 1)
        y = random.randint(0, self.city_size[1] - 1)
        return (x, y)

    async def start_simulation(self) -> None:
        """Inicia a simulação"""
        self.is_running = True
        self.simulation_time = datetime.now()
        print(f"Simulação iniciada em {self.simulation_time}")

        while self.is_running:
            await self._simulation_cycle()
            await asyncio.sleep(0.1 / self.simulation_speed)  # Controla velocidade

    async def stop_simulation(self) -> None:
        """Para a simulação"""
        self.is_running = False
        print(f"Simulação parada após {self.cycle_count} ciclos")

    async def _simulation_cycle(self) -> None:
        """Executa um ciclo da simulação"""
        self.cycle_count += 1
        delta_time = 1.0 * self.simulation_speed

        # Atualiza tempo da simulação
        self.simulation_time += timedelta(hours=1)  # Cada ciclo = 1 hora

        # Gera eventos aleatórios
        await self._check_random_events()

        # Atualiza eventos ativos
        await self._update_active_events()

        # Coleta contexto para agentes
        context = await self._collect_environment_context()

        # Executa agentes em paralelo
        await self._execute_agents(context, delta_time)

        # Atualiza mercado
        if self.cycle_count % self.config["market_update_frequency"] == 0:
            await self._update_market()

        # Atualiza métricas
        if self.cycle_count % self.config["metrics_update_frequency"] == 0:
            await self._update_city_metrics()

        # Salva estado
        if self.cycle_count % self.config["save_frequency"] == 0:
            await self._save_simulation_state()

        # Log de progresso
        if self.cycle_count % 100 == 0:
            print(f"Ciclo {self.cycle_count} - {self.simulation_time}")

    async def _check_random_events(self) -> None:
        """Verifica se deve gerar eventos aleatórios"""
        if random.random() < self.config["event_probability"]:
            await self._trigger_random_event()

    async def _trigger_random_event(self) -> None:
        """Dispara um evento aleatório"""
        # Seleciona evento baseado na probabilidade
        available_events = [
            e for e in self.market_events if e not in self.active_events
        ]
        if not available_events:
            return

        # Seleciona evento baseado na probabilidade
        probabilities = [e.probability for e in available_events]
        total_prob = sum(probabilities)

        if total_prob > 0:
            rand = random.random() * total_prob
            cumulative = 0

            for event in available_events:
                cumulative += event.probability
                if rand <= cumulative:
                    await self._activate_event(event)
                    break

    async def _activate_event(self, event: MarketEvent) -> None:
        """Ativa um evento"""
        self.active_events.append(event)
        self.event_history.append(event)

        print(f"Evento ativado: {event.description}")

        # Notifica agentes sobre o evento
        await self._notify_agents_about_event(event)

    async def _notify_agents_about_event(self, event: MarketEvent) -> None:
        """Notifica agentes sobre evento"""
        for agent in self.agents:
            message = {
                "type": "market_event",
                "event": event.event_type,
                "description": event.description,
                "impact": event.impact,
                "duration": event.duration,
            }

            # Cria mensagem para o agente
            from ..agents.base_agent import AgentMessage

            agent_message = AgentMessage(
                sender_id="environment",
                receiver_id=agent.state.id,
                message_type="market_event",
                content=message,
                priority=2,
            )

            agent.message_queue.append(agent_message)

    async def _update_active_events(self) -> None:
        """Atualiza eventos ativos"""
        events_to_remove = []

        for event in self.active_events:
            event.duration -= 1
            if event.duration <= 0:
                events_to_remove.append(event)

        for event in events_to_remove:
            self.active_events.remove(event)
            print(f"Evento finalizado: {event.description}")

    async def _collect_environment_context(self) -> Dict[str, Any]:
        """Coleta contexto do ambiente para os agentes"""
        # Calcula métricas básicas
        total_population = len(self.citizens)
        total_businesses = len(self.businesses)

        # Calcula demanda agregada
        total_demand = sum(citizen.needs for citizen in self.citizens)

        # Calcula oferta agregada
        total_supply = sum(business.current_production for business in self.businesses)

        # Calcula preços médios
        avg_prices = {}
        for business in self.businesses:
            business_type = business.business_type
            if business_type not in avg_prices:
                avg_prices[business_type] = []
            avg_prices[business_type].append(business.current_price)

        for business_type in avg_prices:
            avg_prices[business_type] = np.mean(avg_prices[business_type])

        # Calcula impacto de eventos ativos
        event_impact = {}
        for event in self.active_events:
            for impact_type, impact_value in event.impact.items():
                if impact_type not in event_impact:
                    event_impact[impact_type] = 0
                event_impact[impact_type] += impact_value

        return {
            "population": total_population,
            "businesses": total_businesses,
            "demand": total_demand,
            "supply": total_supply,
            "avg_prices": avg_prices,
            "event_impact": event_impact,
            "active_events": len(self.active_events),
            "simulation_time": self.simulation_time,
            "cycle_count": self.cycle_count,
        }

    async def _execute_agents(self, context: Dict[str, Any], delta_time: float) -> None:
        """Executa todos os agentes em paralelo"""
        # Prepara contexto específico para cada tipo de agente
        citizen_context = {**context, "citizens": [c.to_dict() for c in self.citizens]}
        business_context = {
            **context,
            "businesses": [b.to_dict() for b in self.businesses],
        }
        government_context = {
            **context,
            "governments": [g.to_dict() for g in self.governments],
        }
        infrastructure_context = {
            **context,
            "infrastructure": [i.to_dict() for i in self.infrastructure],
        }

        # Executa agentes em paralelo
        tasks = []

        # Cidadãos
        for citizen in self.citizens:
            tasks.append(citizen.make_decision(citizen_context))
            tasks.append(citizen.update_state(delta_time))
            tasks.append(citizen.process_messages())

        # Empresas
        for business in self.businesses:
            tasks.append(business.make_decision(business_context))
            tasks.append(business.update_state(delta_time))
            tasks.append(business.process_messages())

        # Governos
        for government in self.governments:
            tasks.append(government.make_decision(government_context))
            tasks.append(government.update_state(delta_time))
            tasks.append(government.process_messages())

        # Infraestrutura
        for infrastructure in self.infrastructure:
            tasks.append(infrastructure.make_decision(infrastructure_context))
            tasks.append(infrastructure.update_state(delta_time))
            tasks.append(infrastructure.process_messages())

        # Executa todas as tarefas em paralelo
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _update_market(self) -> None:
        """Atualiza o mercado dinâmico"""
        # Calcula oferta e demanda por tipo de produto/serviço
        market_data = {}

        for business in self.businesses:
            business_type = business.business_type
            if business_type not in market_data:
                market_data[business_type] = {
                    "supply": 0,
                    "demand": 0,
                    "prices": [],
                    "businesses": [],
                }

            market_data[business_type]["supply"] += business.current_production
            market_data[business_type]["prices"].append(business.current_price)
            market_data[business_type]["businesses"].append(business)

        # Calcula demanda por tipo
        for citizen in self.citizens:
            for need_type, need_level in citizen.needs.items():
                if need_type in market_data:
                    market_data[need_type]["demand"] += need_level

        # Atualiza preços baseado na oferta e demanda
        for business_type, data in market_data.items():
            if data["supply"] > 0 and data["demand"] > 0:
                supply_demand_ratio = data["supply"] / data["demand"]

                # Ajusta preços baseado na relação oferta/demanda
                for business in data["businesses"]:
                    if supply_demand_ratio > 1.2:  # Oferta alta
                        business.current_price *= 0.98  # Reduz preço
                    elif supply_demand_ratio < 0.8:  # Demanda alta
                        business.current_price *= 1.02  # Aumenta preço

    async def _update_city_metrics(self) -> None:
        """Atualiza métricas da cidade"""
        # Calcula métricas agregadas
        total_population = len(self.citizens)
        total_income = sum(citizen.income for citizen in self.citizens)

        # Taxa de desemprego
        unemployed = sum(1 for citizen in self.citizens if citizen.income < 1000)
        unemployment_rate = unemployed / total_population if total_population > 0 else 0

        # Taxa de criminalidade
        high_stress_citizens = sum(
            1 for citizen in self.citizens if citizen.stress_level > 0.7
        )
        crime_rate = (
            high_stress_citizens / total_population if total_population > 0 else 0
        )

        # Saúde ambiental
        environmental_health = (
            1.0
            - sum(
                business.get_business_metrics().get("environmental_impact", 0)
                for business in self.businesses
            )
            / len(self.businesses)
            if self.businesses
            else 1.0
        )

        # Satisfação cidadã
        citizen_satisfaction = np.mean(
            [citizen.state.satisfaction for citizen in self.citizens]
        )

        # Saúde econômica
        economic_health = np.mean(
            [
                business.get_business_metrics().get("profit_margin", 0)
                for business in self.businesses
            ]
        )

        # Saúde da infraestrutura
        infrastructure_health = np.mean(
            [
                infra.get_infrastructure_metrics().get("system_health", 0)
                for infra in self.infrastructure
            ]
        )

        # Eficiência governamental
        government_efficiency = np.mean(
            [
                gov.get_governance_metrics().get("efficiency", 0)
                for gov in self.governments
            ]
        )

        # Atualiza métricas
        self.city_metrics = CityMetrics(
            population=total_population,
            total_income=total_income,
            unemployment_rate=unemployment_rate,
            crime_rate=crime_rate,
            environmental_health=environmental_health,
            citizen_satisfaction=citizen_satisfaction,
            economic_health=economic_health,
            infrastructure_health=infrastructure_health,
            government_efficiency=government_efficiency,
            timestamp=self.simulation_time,
        )

        # Adiciona ao histórico
        self.metrics_history.append(self.city_metrics)

        # Mantém apenas últimos 1000 registros
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-500:]

    async def _save_simulation_state(self) -> None:
        """Salva estado da simulação"""
        state = {
            "simulation_time": self.simulation_time.isoformat(),
            "cycle_count": self.cycle_count,
            "city_metrics": {
                "population": self.city_metrics.population,
                "total_income": self.city_metrics.total_income,
                "unemployment_rate": self.city_metrics.unemployment_rate,
                "crime_rate": self.city_metrics.crime_rate,
                "environmental_health": self.city_metrics.environmental_health,
                "citizen_satisfaction": self.city_metrics.citizen_satisfaction,
                "economic_health": self.city_metrics.economic_health,
                "infrastructure_health": self.city_metrics.infrastructure_health,
                "government_efficiency": self.city_metrics.government_efficiency,
            },
            "active_events": len(self.active_events),
            "agents_count": len(self.agents),
        }

        # Salva em arquivo (implementação básica)
        filename = f"simulation_state_{self.cycle_count}.json"
        try:
            with open(filename, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar estado: {e}")

    def get_city_status(self) -> Dict[str, Any]:
        """Retorna status atual da cidade"""
        return {
            "city_name": self.city_name,
            "simulation_time": self.simulation_time.isoformat(),
            "cycle_count": self.cycle_count,
            "is_running": self.is_running,
            "agents_count": {
                "total": len(self.agents),
                "citizens": len(self.citizens),
                "businesses": len(self.businesses),
                "governments": len(self.governments),
                "infrastructure": len(self.infrastructure),
            },
            "active_events": len(self.active_events),
            "metrics": {
                "population": self.city_metrics.population,
                "unemployment_rate": self.city_metrics.unemployment_rate,
                "crime_rate": self.city_metrics.crime_rate,
                "citizen_satisfaction": self.city_metrics.citizen_satisfaction,
                "economic_health": self.city_metrics.economic_health,
                "infrastructure_health": self.city_metrics.infrastructure_health,
                "environmental_health": self.city_metrics.environmental_health,
            },
        }

    def get_agent_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna dados de todos os agentes"""
        return {
            "citizens": [citizen.to_dict() for citizen in self.citizens],
            "businesses": [business.to_dict() for business in self.businesses],
            "governments": [government.to_dict() for government in self.governments],
            "infrastructure": [
                infrastructure.to_dict() for infrastructure in self.infrastructure
            ],
        }

    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Retorna histórico de métricas"""
        return [
            {
                "timestamp": metrics.timestamp.isoformat(),
                "population": metrics.population,
                "unemployment_rate": metrics.unemployment_rate,
                "crime_rate": metrics.crime_rate,
                "citizen_satisfaction": metrics.citizen_satisfaction,
                "economic_health": metrics.economic_health,
                "infrastructure_health": metrics.infrastructure_health,
                "environmental_health": metrics.environmental_health,
            }
            for metrics in self.metrics_history
        ]

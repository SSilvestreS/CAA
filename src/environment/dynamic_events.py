"""
Sistema de Eventos Dinâmicos para Simulação de Cidade Inteligente
Versão 1.2 - Eventos em tempo real e emergências
"""

# json import removido - não utilizado
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Tipos de eventos que podem ocorrer na simulação"""

    CRISIS_ENERGIA = "crisis_energia"
    PANDEMIA = "pandemia"
    DESASTRE_NATURAL = "desastre_natural"
    CRISE_ECONOMICA = "crise_economica"
    CRESCIMENTO_POPULACIONAL = "crescimento_populacional"
    INOVACAO_TECNOLOGICA = "inovacao_tecnologica"
    MUDANCA_CLIMATICA = "mudanca_climatica"
    ACIDENTE_TRANSPORTE = "acidente_transporte"
    FALHA_INFRAESTRUTURA = "falha_infraestrutura"
    PROTESTOS_SOCIAIS = "protestos_sociais"


class EventSeverity(Enum):
    """Severidade dos eventos"""

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


@dataclass
class EventConfig:
    """Configuração de um tipo de evento"""

    event_type: EventType
    probability: float  # Probabilidade por hora
    duration_range: tuple  # (min, max) em segundos
    severity_distribution: Dict[EventSeverity, float]
    impact_factors: Dict[str, float]  # Fatores de impacto
    recovery_time: int  # Tempo de recuperação em segundos
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class ActiveEvent:
    """Evento ativo na simulação"""

    id: str
    event_type: EventType
    severity: EventSeverity
    start_time: datetime
    duration: int
    end_time: datetime
    impact_factors: Dict[str, float]
    affected_agents: List[str] = field(default_factory=list)
    recovery_progress: float = 0.0
    is_resolved: bool = False


class DynamicEventSystem:
    """Sistema de eventos dinâmicos para simulação em tempo real"""

    def __init__(self, simulation_manager):
        self.simulation_manager = simulation_manager
        self.active_events: Dict[str, ActiveEvent] = {}
        self.event_configs: Dict[EventType, EventConfig] = {}
        self.event_handlers: Dict[EventType, Callable] = {}
        self.running = False
        self.event_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Estatísticas
        self.total_events = 0
        self.resolved_events = 0
        self.event_history: List[Dict] = []

        self._initialize_default_configs()
        self._register_default_handlers()

    def _initialize_default_configs(self):
        """Inicializa configurações padrão dos eventos"""

        # Crise de Energia
        self.event_configs[EventType.CRISIS_ENERGIA] = EventConfig(
            event_type=EventType.CRISIS_ENERGIA,
            probability=0.05,  # 5% por hora
            duration_range=(1800, 7200),  # 30min a 2h
            severity_distribution={
                EventSeverity.BAIXA: 0.4,
                EventSeverity.MEDIA: 0.3,
                EventSeverity.ALTA: 0.2,
                EventSeverity.CRITICA: 0.1,
            },
            impact_factors={
                "energy_consumption": -0.3,
                "productivity": -0.2,
                "satisfaction": -0.4,
            },
            recovery_time=3600,
        )

        # Pandemia
        self.event_configs[EventType.PANDEMIA] = EventConfig(
            event_type=EventType.PANDEMIA,
            probability=0.02,  # 2% por hora
            duration_range=(3600, 14400),  # 1h a 4h
            severity_distribution={
                EventSeverity.BAIXA: 0.3,
                EventSeverity.MEDIA: 0.4,
                EventSeverity.ALTA: 0.2,
                EventSeverity.CRITICA: 0.1,
            },
            impact_factors={
                "mobility": -0.5,
                "health": -0.6,
                "economy": -0.3,
                "social_interaction": -0.7,
            },
            recovery_time=7200,
        )

        # Desastre Natural
        self.event_configs[EventType.DESASTRE_NATURAL] = EventConfig(
            event_type=EventType.DESASTRE_NATURAL,
            probability=0.01,  # 1% por hora
            duration_range=(900, 3600),  # 15min a 1h
            severity_distribution={
                EventSeverity.BAIXA: 0.2,
                EventSeverity.MEDIA: 0.3,
                EventSeverity.ALTA: 0.3,
                EventSeverity.CRITICA: 0.2,
            },
            impact_factors={
                "infrastructure": -0.8,
                "mobility": -0.6,
                "safety": -0.7,
                "economy": -0.4,
            },
            recovery_time=10800,
        )

        # Crise Econômica
        self.event_configs[EventType.CRISE_ECONOMICA] = EventConfig(
            event_type=EventType.CRISE_ECONOMICA,
            probability=0.03,  # 3% por hora
            duration_range=(7200, 28800),  # 2h a 8h
            severity_distribution={
                EventSeverity.BAIXA: 0.3,
                EventSeverity.MEDIA: 0.4,
                EventSeverity.ALTA: 0.2,
                EventSeverity.CRITICA: 0.1,
            },
            impact_factors={
                "economic_growth": -0.5,
                "employment": -0.3,
                "investment": -0.4,
                "satisfaction": -0.3,
            },
            recovery_time=14400,
        )

        # Crescimento Populacional
        self.event_configs[EventType.CRESCIMENTO_POPULACIONAL] = EventConfig(
            event_type=EventType.CRESCIMENTO_POPULACIONAL,
            probability=0.08,  # 8% por hora
            duration_range=(3600, 14400),  # 1h a 4h
            severity_distribution={
                EventSeverity.BAIXA: 0.5,
                EventSeverity.MEDIA: 0.3,
                EventSeverity.ALTA: 0.15,
                EventSeverity.CRITICA: 0.05,
            },
            impact_factors={
                "population": 0.1,
                "resource_demand": 0.2,
                "infrastructure_pressure": 0.3,
                "economic_activity": 0.15,
            },
            recovery_time=1800,
        )

    def _register_default_handlers(self):
        """Registra handlers padrão para os eventos"""

        self.event_handlers[EventType.CRISIS_ENERGIA] = self._handle_energy_crisis
        self.event_handlers[EventType.PANDEMIA] = self._handle_pandemic
        self.event_handlers[EventType.DESASTRE_NATURAL] = self._handle_natural_disaster
        self.event_handlers[EventType.CRISE_ECONOMICA] = self._handle_economic_crisis
        self.event_handlers[EventType.CRESCIMENTO_POPULACIONAL] = (
            self._handle_population_growth
        )

    def start(self):
        """Inicia o sistema de eventos dinâmicos"""
        if self.running:
            return

        self.running = True
        self.event_thread = threading.Thread(target=self._event_loop, daemon=True)
        self.event_thread.start()
        logger.info("Sistema de eventos dinâmicos iniciado")

    def stop(self):
        """Para o sistema de eventos dinâmicos"""
        self.running = False
        if self.event_thread:
            self.event_thread.join(timeout=5.0)
        logger.info("Sistema de eventos dinâmicos parado")

    def _event_loop(self):
        """Loop principal do sistema de eventos"""
        while self.running:
            try:
                self._check_for_new_events()
                self._update_active_events()
                time.sleep(60)  # Verifica a cada minuto
            except Exception as e:
                logger.error(f"Erro no loop de eventos: {e}")
                time.sleep(60)

    def _check_for_new_events(self):
        """Verifica se novos eventos devem ser gerados"""
        for event_type, config in self.event_configs.items():
            if (
                random.random() < config.probability / 60
            ):  # Converter para probabilidade por minuto
                self._generate_event(event_type, config)

    def _generate_event(self, event_type: EventType, config: EventConfig):
        """Gera um novo evento"""
        with self.lock:
            # Determinar severidade
            severity = self._determine_severity(config.severity_distribution)

            # Determinar duração
            duration = random.randint(*config.duration_range)

            # Criar evento
            event_id = f"{event_type.value}_{int(time.time())}"
            event = ActiveEvent(
                id=event_id,
                event_type=event_type,
                severity=severity,
                start_time=datetime.now(),
                duration=duration,
                end_time=datetime.now() + timedelta(seconds=duration),
                impact_factors=config.impact_factors.copy(),
            )

            # Aplicar multiplicadores de severidade
            severity_multiplier = self._get_severity_multiplier(severity)
            for factor in event.impact_factors:
                event.impact_factors[factor] *= severity_multiplier

            self.active_events[event_id] = event
            self.total_events += 1

            # Executar handler
            if event_type in self.event_handlers:
                self.event_handlers[event_type](event)

            logger.info(
                f"Evento gerado: {event_type.value} (Severidade: {severity.value})"
            )

    def _determine_severity(
        self, distribution: Dict[EventSeverity, float]
    ) -> EventSeverity:
        """Determina a severidade baseada na distribuição"""
        rand = random.random()
        cumulative = 0.0

        for severity, probability in distribution.items():
            cumulative += probability
            if rand <= cumulative:
                return severity

        return EventSeverity.BAIXA

    def _get_severity_multiplier(self, severity: EventSeverity) -> float:
        """Retorna multiplicador baseado na severidade"""
        multipliers = {
            EventSeverity.BAIXA: 0.5,
            EventSeverity.MEDIA: 1.0,
            EventSeverity.ALTA: 1.5,
            EventSeverity.CRITICA: 2.0,
        }
        return multipliers[severity]

    def _update_active_events(self):
        """Atualiza eventos ativos"""
        current_time = datetime.now()
        events_to_remove = []

        with self.lock:
            for event_id, event in self.active_events.items():
                if current_time >= event.end_time:
                    # Evento expirou
                    self._resolve_event(event)
                    events_to_remove.append(event_id)
                else:
                    # Atualizar progresso de recuperação
                    elapsed = (current_time - event.start_time).total_seconds()
                    event.recovery_progress = min(elapsed / event.duration, 1.0)

        # Remover eventos resolvidos
        for event_id in events_to_remove:
            del self.active_events[event_id]

    def _resolve_event(self, event: ActiveEvent):
        """Resolve um evento"""
        event.is_resolved = True
        self.resolved_events += 1

        # Registrar no histórico
        self.event_history.append(
            {
                "id": event.id,
                "type": event.event_type.value,
                "severity": event.severity.value,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "duration": event.duration,
                "impact_factors": event.impact_factors,
            }
        )

        logger.info(f"Evento resolvido: {event.event_type.value}")

    # Handlers específicos para cada tipo de evento

    def _handle_energy_crisis(self, event: ActiveEvent):
        """Handler para crise de energia"""
        # Reduzir consumo de energia dos agentes
        for agent in self.simulation_manager.get_all_agents():
            if hasattr(agent, "energy_consumption"):
                agent.energy_consumption *= 1 + event.impact_factors.get(
                    "energy_consumption", 0
                )

    def _handle_pandemic(self, event: ActiveEvent):
        """Handler para pandemia"""
        # Reduzir mobilidade e interações sociais
        for agent in self.simulation_manager.get_all_agents():
            if hasattr(agent, "mobility"):
                agent.mobility *= 1 + event.impact_factors.get("mobility", 0)
            if hasattr(agent, "social_interaction"):
                agent.social_interaction *= 1 + event.impact_factors.get(
                    "social_interaction", 0
                )

    def _handle_natural_disaster(self, event: ActiveEvent):
        """Handler para desastre natural"""
        # Danificar infraestrutura
        for agent in self.simulation_manager.get_all_agents():
            if hasattr(agent, "infrastructure_health"):
                agent.infrastructure_health *= 1 + event.impact_factors.get(
                    "infrastructure", 0
                )

    def _handle_economic_crisis(self, event: ActiveEvent):
        """Handler para crise econômica"""
        # Reduzir atividade econômica
        for agent in self.simulation_manager.get_all_agents():
            if hasattr(agent, "economic_activity"):
                agent.economic_activity *= 1 + event.impact_factors.get(
                    "economic_growth", 0
                )

    def _handle_population_growth(self, event: ActiveEvent):
        """Handler para crescimento populacional"""
        # Aumentar população e demanda por recursos
        population_increase = event.impact_factors.get("population", 0)
        if population_increase > 0:
            # Adicionar novos agentes cidadãos
            for _ in range(
                int(population_increase * 10)
            ):  # Escalar para número de agentes
                self.simulation_manager.add_citizen_agent()

    def get_active_events(self) -> List[ActiveEvent]:
        """Retorna lista de eventos ativos"""
        with self.lock:
            return list(self.active_events.values())

    def get_event_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos eventos"""
        return {
            "total_events": self.total_events,
            "resolved_events": self.resolved_events,
            "active_events": len(self.active_events),
            "event_types": {
                event_type.value: sum(
                    1
                    for event in self.event_history
                    if event["type"] == event_type.value
                )
                for event_type in EventType
            },
            "severity_distribution": {
                severity.value: sum(
                    1
                    for event in self.event_history
                    if event["severity"] == severity.value
                )
                for severity in EventSeverity
            },
        }

    def trigger_event(
        self,
        event_type: EventType,
        severity: EventSeverity = EventSeverity.MEDIA,
    ):
        """Força a geração de um evento específico"""
        if event_type in self.event_configs:
            config = self.event_configs[event_type]
            self._generate_event(event_type, config)
            logger.info(f"Evento forçado: {event_type.value}")

    def get_impact_on_agent(self, agent_id: str) -> Dict[str, float]:
        """Retorna impacto total dos eventos ativos em um agente"""
        total_impact = {}

        with self.lock:
            for event in self.active_events.values():
                for factor, impact in event.impact_factors.items():
                    if factor not in total_impact:
                        total_impact[factor] = 0.0
                    total_impact[factor] += impact * (1 - event.recovery_progress)

        return total_impact

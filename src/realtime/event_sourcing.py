"""
Sistema de Event Sourcing para auditoria e reconstrução de estado.
"""

from typing import Dict, List, Any, Optional, Callable

import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from collections import defaultdict


class EventType(Enum):
    """Tipos de eventos do sistema."""

    # Agentes
    AGENT_CREATED = "agent_created"
    AGENT_UPDATED = "agent_updated"
    AGENT_DELETED = "agent_deleted"
    AGENT_ACTION_PERFORMED = "agent_action_performed"
    AGENT_STATE_CHANGED = "agent_state_changed"

    # Simulação
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_STOPPED = "simulation_stopped"
    SIMULATION_PAUSED = "simulation_paused"
    SIMULATION_RESUMED = "simulation_resumed"
    SIMULATION_CYCLE_COMPLETED = "simulation_cycle_completed"

    # Eventos Dinâmicos
    DYNAMIC_EVENT_TRIGGERED = "dynamic_event_triggered"
    DYNAMIC_EVENT_HANDLED = "dynamic_event_handled"

    # Interações
    AGENT_INTERACTION = "agent_interaction"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"

    # Sistema
    CONFIGURATION_CHANGED = "configuration_changed"
    USER_ACTION = "user_action"
    SYSTEM_ERROR = "system_error"


class EventStatus(Enum):
    """Status do evento."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DomainEvent:
    """Evento de domínio base."""

    event_id: str
    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    version: int
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    status: EventStatus = EventStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = self.event_type.value
        data["status"] = self.status.value
        return data

    def to_json(self) -> str:
        """Converte evento para JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class EventStore:
    """Armazenamento de eventos com persistência."""

    def __init__(self, storage_backend: Optional[Callable] = None):
        self.events: List[DomainEvent] = []
        self.aggregate_events: Dict[str, List[DomainEvent]] = defaultdict(list)
        self.storage_backend = storage_backend
        self.event_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        self.snapshot_interval = 100  # Eventos por snapshot

    def append_event(self, event: DomainEvent) -> bool:
        """
        Adiciona evento ao store.

        Args:
            event: Evento para adicionar

        Returns:
            True se evento foi adicionado com sucesso
        """
        try:
            # Valida evento
            if not self._validate_event(event):
                return False

            # Adiciona evento
            self.events.append(event)
            self.aggregate_events[event.aggregate_id].append(event)

            # Persiste se backend disponível
            if self.storage_backend:
                self.storage_backend(event)

            # Processa handlers
            self._process_event_handlers(event)

            # Cria snapshot se necessário
            if len(self.aggregate_events[event.aggregate_id]) % self.snapshot_interval == 0:
                self._create_snapshot(event.aggregate_id)

            return True

        except Exception as e:
            print(f"Erro ao adicionar evento: {e}")
            return False

    def _validate_event(self, event: DomainEvent) -> bool:
        """Valida evento antes de adicionar."""
        if not event.event_id or not event.aggregate_id:
            return False

        if event.version <= 0:
            return False

        return True

    def _process_event_handlers(self, event: DomainEvent):
        """Processa handlers registrados para o evento."""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Erro no handler de evento: {e}")

    def _create_snapshot(self, aggregate_id: str):
        """Cria snapshot do estado do agregado."""
        events = self.aggregate_events[aggregate_id]
        if not events:
            return

        # Simula criação de snapshot
        snapshot = {
            "aggregate_id": aggregate_id,
            "version": events[-1].version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_count": len(events),
        }

        self.snapshots[aggregate_id] = snapshot

    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[DomainEvent]:
        """Recupera eventos de um agregado."""
        events = self.aggregate_events.get(aggregate_id, [])
        return [e for e in events if e.version >= from_version]

    def get_events_by_type(self, event_type: EventType, limit: int = 1000) -> List[DomainEvent]:
        """Recupera eventos por tipo."""
        events = [e for e in self.events if e.event_type == event_type]
        return events[-limit:] if limit > 0 else events

    def get_events_since(self, since: datetime, limit: int = 1000) -> List[DomainEvent]:
        """Recupera eventos desde uma data."""
        events = [e for e in self.events if e.timestamp >= since]
        return events[-limit:] if limit > 0 else events

    def register_handler(self, event_type: EventType, handler: Callable):
        """Registra handler para tipo de evento."""
        self.event_handlers[event_type].append(handler)

    def get_aggregate_state(self, aggregate_id: str, at_version: Optional[int] = None) -> Dict[str, Any]:
        """Reconstrói estado do agregado a partir dos eventos."""
        events = self.get_events(aggregate_id)

        if at_version:
            events = [e for e in events if e.version <= at_version]

        # Aplica eventos para reconstruir estado
        state = {}
        for event in events:
            state = self._apply_event_to_state(state, event)

        return state

    def _apply_event_to_state(self, state: Dict[str, Any], event: DomainEvent) -> Dict[str, Any]:
        """Aplica evento ao estado (implementação específica por domínio)."""
        # Implementação genérica - pode ser sobrescrita
        state.update(event.data)
        state["version"] = event.version
        state["last_updated"] = event.timestamp.isoformat()
        return state


class EventBus:
    """Barramento de eventos para comunicação assíncrona."""

    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_queue = asyncio.Queue()
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None

    async def start(self):
        """Inicia o barramento de eventos."""
        self.running = True
        self.worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Para o barramento de eventos."""
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

    async def publish(self, event: DomainEvent):
        """Publica evento no barramento."""
        await self.event_queue.put(event)

    async def subscribe(self, event_type: EventType, handler: Callable):
        """Inscreve handler para tipo de evento."""
        self.subscribers[event_type].append(handler)

    async def _worker(self):
        """Worker que processa eventos da fila."""
        while self.running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Erro no worker de eventos: {e}")

    async def _process_event(self, event: DomainEvent):
        """Processa evento individual."""
        handlers = self.subscribers.get(event.event_type, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"Erro no handler de evento: {e}")


class EventSourcedAggregate:
    """Agregado base com Event Sourcing."""

    def __init__(self, aggregate_id: str, aggregate_type: str):
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type
        self.version = 0
        self.uncommitted_events: List[DomainEvent] = []

    def _apply_event(self, event: DomainEvent):
        """Aplica evento ao agregado (implementar em subclasses)."""
        self.version = event.version
        # Implementação específica por domínio

    def _add_event(self, event_type: EventType, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Adiciona evento não commitado."""
        event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            aggregate_id=self.aggregate_id,
            aggregate_type=self.aggregate_type,
            version=self.version + 1,
            timestamp=datetime.now(timezone.utc),
            data=data,
            metadata=metadata or {},
        )

        self.uncommitted_events.append(event)
        self._apply_event(event)

    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Retorna eventos não commitados."""
        return self.uncommitted_events.copy()

    def mark_events_as_committed(self):
        """Marca eventos como commitados."""
        self.uncommitted_events.clear()

    @classmethod
    def from_events(cls, aggregate_id: str, events: List[DomainEvent]):
        """Reconstrói agregado a partir de eventos."""
        instance = cls(aggregate_id, events[0].aggregate_type if events else "unknown")

        for event in events:
            instance._apply_event(event)

        return instance


class EventReplay:
    """Utilitário para replay de eventos."""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def replay_events(
        self, aggregate_id: str, from_version: int = 0, to_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Reconstrói estado através de replay de eventos."""
        events = self.event_store.get_events(aggregate_id, from_version)

        if to_version:
            events = [e for e in events if e.version <= to_version]

        # Aplica eventos sequencialmente
        state = {}
        for event in events:
            state = self._apply_event_to_state(state, event)

        return state

    def _apply_event_to_state(self, state: Dict[str, Any], event: DomainEvent) -> Dict[str, Any]:
        """Aplica evento ao estado durante replay."""
        # Implementação genérica - pode ser customizada
        state.update(event.data)
        state["version"] = event.version
        state["last_event_id"] = event.event_id
        state["last_event_time"] = event.timestamp.isoformat()
        return state

    def get_event_timeline(self, aggregate_id: str) -> List[Dict[str, Any]]:
        """Retorna timeline de eventos de um agregado."""
        events = self.event_store.get_events(aggregate_id)
        return [event.to_dict() for event in events]

    def find_events_by_criteria(
        self,
        event_type: Optional[EventType] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[DomainEvent]:
        """Encontra eventos por critérios."""
        events = self.event_store.events

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if since:
            events = [e for e in events if e.timestamp >= since]

        if until:
            events = [e for e in events if e.timestamp <= until]

        return events[-limit:] if limit > 0 else events

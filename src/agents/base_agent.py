"""
Classe base para todos os agentes da simulação de cidade inteligente.
Define a interface comum e funcionalidades básicas.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from pydantic import BaseModel


@dataclass
class AgentState:
    """Estado interno do agente"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    position: tuple = (0, 0)  # Coordenadas na cidade
    resources: Dict[str, float] = field(default_factory=dict)
    memory: List[Dict[str, Any]] = field(default_factory=list)
    satisfaction: float = 0.5  # Nível de satisfação (0-1)
    energy: float = 1.0  # Nível de energia (0-1)
    last_update: datetime = field(default_factory=datetime.now)


class AgentMessage(BaseModel):
    """Mensagem entre agentes"""

    sender_id: str
    receiver_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1=baixa, 2=média, 3=alta


class BaseAgent(ABC):
    """
    Classe base para todos os agentes da simulação.
    Implementa funcionalidades comuns e define interface para subclasses.
    """

    def __init__(self, name: str, position: tuple = (0, 0), **kwargs):
        self.state = AgentState(name=name, position=position)
        self.personality = self._generate_personality()
        self.decision_model = None
        self.message_queue: List[AgentMessage] = []
        self.neighbors: List["BaseAgent"] = []
        self.environment = None

    def _generate_personality(self) -> Dict[str, float]:
        """Gera traços de personalidade aleatórios para o agente"""
        return {
            "risk_tolerance": np.random.uniform(0, 1),
            "cooperation": np.random.uniform(0, 1),
            "innovation": np.random.uniform(0, 1),
            "conservatism": np.random.uniform(0, 1),
            "social_orientation": np.random.uniform(0, 1),
        }

    @abstractmethod
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método abstrato para tomada de decisão.
        Cada tipo de agente deve implementar sua própria lógica.
        """
        pass

    @abstractmethod
    async def update_state(self, delta_time: float) -> None:
        """
        Atualiza o estado interno do agente.
        Deve ser chamado a cada ciclo da simulação.
        """
        pass

    async def send_message(
        self,
        receiver: "BaseAgent",
        message_type: str,
        content: Dict[str, Any],
        priority: int = 1,
    ) -> None:
        """Envia uma mensagem para outro agente"""
        message = AgentMessage(
            sender_id=self.state.id,
            receiver_id=receiver.state.id,
            message_type=message_type,
            content=content,
            priority=priority,
        )
        receiver.message_queue.append(message)

    async def process_messages(self) -> List[Dict[str, Any]]:
        """Processa mensagens recebidas e retorna respostas"""
        responses = []
        for message in self.message_queue:
            response = await self._handle_message(message)
            if response:
                responses.append(response)
        self.message_queue.clear()
        return responses

    async def _handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Processa uma mensagem individual"""
        # Implementação básica - pode ser sobrescrita por subclasses
        return {
            "sender_id": self.state.id,
            "message_type": "acknowledgment",
            "content": {"received": True},
        }

    def add_resource(self, resource_type: str, amount: float) -> None:
        """Adiciona recursos ao agente"""
        if resource_type not in self.state.resources:
            self.state.resources[resource_type] = 0
        self.state.resources[resource_type] += amount

    def consume_resource(self, resource_type: str, amount: float) -> bool:
        """Consome recursos do agente. Retorna True se bem-sucedido"""
        if resource_type not in self.state.resources:
            return False
        if self.state.resources[resource_type] < amount:
            return False
        self.state.resources[resource_type] -= amount
        return True

    def get_distance_to(self, other_agent: "BaseAgent") -> float:
        """Calcula distância para outro agente"""
        pos1 = np.array(self.state.position)
        pos2 = np.array(other_agent.state.position)
        return np.linalg.norm(pos1 - pos2)

    def find_nearest_agents(
        self, agent_type: type, max_distance: float = 100
    ) -> List["BaseAgent"]:
        """Encontra agentes mais próximos de um tipo específico"""
        if not self.environment:
            return []

        nearby_agents = []
        for agent in self.environment.agents:
            if isinstance(agent, agent_type) and agent != self:
                distance = self.get_distance_to(agent)
                if distance <= max_distance:
                    nearby_agents.append((agent, distance))

        # Ordena por distância
        nearby_agents.sort(key=lambda x: x[1])
        return [agent for agent, _ in nearby_agents]

    def update_satisfaction(self, change: float) -> None:
        """Atualiza nível de satisfação do agente"""
        self.state.satisfaction = max(0, min(1, self.state.satisfaction + change))

    def update_energy(self, change: float) -> None:
        """Atualiza nível de energia do agente"""
        self.state.energy = max(0, min(1, self.state.energy + change))

    def to_dict(self) -> Dict[str, Any]:
        """Converte estado do agente para dicionário"""
        return {
            "id": self.state.id,
            "name": self.state.name,
            "position": self.state.position,
            "resources": self.state.resources.copy(),
            "satisfaction": self.state.satisfaction,
            "energy": self.state.energy,
            "personality": self.personality.copy(),
            "last_update": self.state.last_update.isoformat(),
        }

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.state.name}, pos={self.state.position})"
        )

    def __repr__(self) -> str:
        return self.__str__()

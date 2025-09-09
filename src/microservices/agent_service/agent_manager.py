"""
Gerenciador de agentes para o microserviço
versão 1.7 - MLOps e Escalabilidade
"""

import logging
from uuid import uuid4
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from .agent_models import Agent, AgentType, AgentStatus, AgentMetrics, AgentHealthCheck

logger = logging.getLogger(__name__)


class AgentManager:
    """Gerenciador principal de agentes"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.health_checks: Dict[str, AgentHealthCheck] = {}
        self._running = False
        self._health_check_interval = 30  # segundos

    async def start(self):
        """Inicia o gerenciador de agentes"""
        self._running = True
        logger.info("Agent Manager iniciado")

        # Inicia health checks em background
        asyncio.create_task(self._health_check_loop())

    async def stop(self):
        """Para o gerenciador de agentes"""
        self._running = False
        logger.info("Agent Manager parado")

    async def create_agent(
        self,
        agent_type: AgentType,
        name: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        """Cria um novo agente"""
        agent_id = str(uuid4())

        agent = Agent(
            id=agent_id,
            type=agent_type,
            name=name,
            description=description,
            config=config or {},
            status=AgentStatus.INACTIVE,
        )

        self.agents[agent_id] = agent
        logger.info(f"Agente criado: {agent_id} ({agent_type})")

        return agent

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Obtém um agente por ID"""
        return self.agents.get(agent_id)

    async def list_agents(
        self,
        agent_type: Optional[AgentType] = None,
        status: Optional[AgentStatus] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Agent]:
        """Lista agentes com filtros e paginação"""
        filtered_agents = list(self.agents.values())

        # Aplica filtros
        if agent_type:
            filtered_agents = [a for a in filtered_agents if a.type == agent_type]
        if status:
            filtered_agents = [a for a in filtered_agents if a.status == status]

        # Aplica paginação
        start = (page - 1) * page_size
        end = start + page_size

        return filtered_agents[start:end]

    async def update_agent(
        self, agent_id: str, updates: Dict[str, Any]
    ) -> Optional[Agent]:
        """Atualiza um agente"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        # Atualiza campos permitidos
        for key, value in updates.items():
            if hasattr(agent, key) and key not in ["id", "created_at"]:
                setattr(agent, key, value)

        agent.updated_at = datetime.now()
        logger.info(f"Agente atualizado: {agent_id}")

        return agent

    async def delete_agent(self, agent_id: str) -> bool:
        """Remove um agente"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            if agent_id in self.health_checks:
                del self.health_checks[agent_id]
            logger.info(f"Agente removido: {agent_id}")
            return True
        return False

    async def start_agent(self, agent_id: str) -> bool:
        """Inicia um agente"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        agent.status = AgentStatus.ACTIVE
        agent.updated_at = datetime.now()
        logger.info(f"Agente iniciado: {agent_id}")

        return True

    async def stop_agent(self, agent_id: str) -> bool:
        """Para um agente"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        agent.status = AgentStatus.INACTIVE
        agent.updated_at = datetime.now()
        logger.info(f"Agente parado: {agent_id}")

        return True

    async def pause_agent(self, agent_id: str) -> bool:
        """Pausa um agente"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        agent.status = AgentStatus.PAUSED
        agent.updated_at = datetime.now()
        logger.info(f"Agente pausado: {agent_id}")

        return True

    async def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Obtém métricas de um agente"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        return agent.metrics

    async def update_agent_metrics(self, agent_id: str, metrics: AgentMetrics) -> bool:
        """Atualiza métricas de um agente"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        agent.metrics = metrics
        agent.updated_at = datetime.now()

        return True

    async def health_check(self, agent_id: str) -> AgentHealthCheck:
        """Executa health check de um agente"""
        agent = self.agents.get(agent_id)
        if not agent:
            return AgentHealthCheck(
                agent_id=agent_id,
                status=AgentStatus.ERROR,
                is_healthy=False,
                last_check=datetime.now(),
                response_time=0.0,
                error_message="Agente não encontrado",
            )

        start_time = datetime.now()

        try:
            # Simula health check (implementar lógica real)
            await asyncio.sleep(0.1)  # Simula latência

            response_time = (datetime.now() - start_time).total_seconds() * 1000
            is_healthy = agent.status == AgentStatus.ACTIVE

            health_check = AgentHealthCheck(
                agent_id=agent_id,
                status=agent.status,
                is_healthy=is_healthy,
                last_check=datetime.now(),
                response_time=response_time,
            )

        except Exception as e:
            health_check = AgentHealthCheck(
                agent_id=agent_id,
                status=AgentStatus.ERROR,
                is_healthy=False,
                last_check=datetime.now(),
                response_time=0.0,
                error_message=str(e),
            )

        self.health_checks[agent_id] = health_check
        return health_check

    async def _health_check_loop(self):
        """Loop de health checks em background"""
        while self._running:
            try:
                for agent_id in list(self.agents.keys()):
                    await self.health_check(agent_id)

                await asyncio.sleep(self._health_check_interval)

            except Exception as e:
                logger.error(f"Erro no health check loop: {e}")
                await asyncio.sleep(5)

    async def get_health_status(self) -> Dict[str, Any]:
        """Obtém status geral de saúde do sistema"""
        total_agents = len(self.agents)
        active_agents = len(
            [a for a in self.agents.values() if a.status == AgentStatus.ACTIVE]
        )
        healthy_agents = len([h for h in self.health_checks.values() if h.is_healthy])

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "healthy_agents": healthy_agents,
            "health_percentage": (
                (healthy_agents / total_agents * 100) if total_agents > 0 else 0
            ),
            "last_check": datetime.now(),
        }

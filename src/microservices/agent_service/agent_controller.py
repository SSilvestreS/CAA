"""
Controller REST para o Agent Service
versão 1.7 - MLOps e Escalabilidade
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from typing import Optional

from .agent_manager import AgentManager
from .agent_models import (
    Agent,
    AgentType,
    AgentStatus,
    AgentMetrics,
    AgentHealthCheck,
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentListResponse,
)

logger = logging.getLogger(__name__)

# Router para as rotas da API
router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

# Instância global do gerenciador
agent_manager = AgentManager()


@router.on_event("startup")
async def startup_event():
    """Inicializa o gerenciador na startup"""
    await agent_manager.start()


@router.on_event("shutdown")
async def shutdown_event():
    """Para o gerenciador no shutdown"""
    await agent_manager.stop()


@router.post("/", response_model=Agent, status_code=201)
async def create_agent(agent_data: AgentCreateRequest):
    """Cria um novo agente"""
    try:
        agent = await agent_manager.create_agent(
            agent_type=agent_data.type,
            name=agent_data.name,
            description=agent_data.description,
            config=agent_data.config,
        )
        return agent
    except Exception as e:
        logger.error(f"Erro ao criar agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str = Path(..., description="ID do agente")):
    """Obtém um agente por ID"""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    return agent


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    agent_type: Optional[AgentType] = Query(None, description="Filtrar por tipo"),
    status: Optional[AgentStatus] = Query(None, description="Filtrar por status"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
):
    """Lista agentes com filtros e paginação"""
    try:
        agents = await agent_manager.list_agents(
            agent_type=agent_type, status=status, page=page, page_size=page_size
        )

        # Calcula informações de paginação
        total_agents = len(
            await agent_manager.list_agents(agent_type=agent_type, status=status)
        )
        has_next = (page * page_size) < total_agents
        has_prev = page > 1

        return AgentListResponse(
            agents=agents,
            total=total_agents,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_prev=has_prev,
        )
    except Exception as e:
        logger.error(f"Erro ao listar agentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str = Path(..., description="ID do agente"),
    updates: AgentUpdateRequest = Body(..., description="Dados para atualização"),
):
    """Atualiza um agente"""
    try:
        # Converte Pydantic model para dict, removendo valores None
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}

        agent = await agent_manager.update_agent(agent_id, update_dict)
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str = Path(..., description="ID do agente")):
    """Remove um agente"""
    try:
        success = await agent_manager.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return JSONResponse(content=None, status_code=204)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/start", status_code=200)
async def start_agent(agent_id: str = Path(..., description="ID do agente")):
    """Inicia um agente"""
    try:
        success = await agent_manager.start_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return {"message": "Agente iniciado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/stop", status_code=200)
async def stop_agent(agent_id: str = Path(..., description="ID do agente")):
    """Para um agente"""
    try:
        success = await agent_manager.stop_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return {"message": "Agente parado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao parar agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/pause", status_code=200)
async def pause_agent(agent_id: str = Path(..., description="ID do agente")):
    """Pausa um agente"""
    try:
        success = await agent_manager.pause_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return {"message": "Agente pausado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao pausar agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/metrics", response_model=AgentMetrics)
async def get_agent_metrics(agent_id: str = Path(..., description="ID do agente")):
    """Obtém métricas de um agente"""
    try:
        metrics = await agent_manager.get_agent_metrics(agent_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/health", response_model=AgentHealthCheck)
async def health_check_agent(agent_id: str = Path(..., description="ID do agente")):
    """Executa health check de um agente"""
    try:
        health_check = await agent_manager.health_check(agent_id)
        return health_check
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/status")
async def get_health_status():
    """Obtém status geral de saúde do sistema"""
    try:
        status = await agent_manager.get_health_status()
        return status
    except Exception as e:
        logger.error(f"Erro ao obter status de saúde: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_stats_summary():
    """Obtém resumo estatístico dos agentes"""
    try:
        agents = await agent_manager.list_agents()

        # Calcula estatísticas
        stats = {
            "total_agents": len(agents),
            "by_type": {},
            "by_status": {},
            "avg_response_time": 0.0,
            "total_errors": 0,
        }

        response_times = []

        for agent in agents:
            # Conta por tipo
            agent_type = agent.type.value
            stats["by_type"][agent_type] = stats["by_type"].get(agent_type, 0) + 1

            # Conta por status
            agent_status = agent.status.value
            stats["by_status"][agent_status] = (
                stats["by_status"].get(agent_status, 0) + 1
            )

            # Coleta métricas
            if agent.metrics:
                response_times.append(agent.metrics.response_time)
                stats["total_errors"] += agent.metrics.error_count

        # Calcula média de tempo de resposta
        if response_times:
            stats["avg_response_time"] = sum(response_times) / len(response_times)

        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AgentController:
    """Controller principal para o Agent Service"""

    def __init__(self):
        self.agent_manager = AgentManager()
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Configura as rotas da API"""
        # Rotas já definidas no router acima
        pass

    def get_router(self):
        """Retorna o router configurado"""
        return self.router

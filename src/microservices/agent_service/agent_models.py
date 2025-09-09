"""
Modelos de dados para o Agent Service
Versão 1.6 - MLOps e Escalabilidade
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Tipos de agentes disponíveis"""

    CITIZEN = "citizen"
    BUSINESS = "business"
    GOVERNMENT = "government"
    INFRASTRUCTURE = "infrastructure"


class AgentStatus(str, Enum):
    """Status dos agentes"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AgentMetrics(BaseModel):
    """Métricas de performance do agente"""

    cpu_usage: float = Field(ge=0, le=100, description="Uso de CPU em %")
    memory_usage: float = Field(ge=0, le=100, description="Uso de memória em %")
    response_time: float = Field(ge=0, description="Tempo de resposta em ms")
    success_rate: float = Field(ge=0, le=1, description="Taxa de sucesso")
    error_count: int = Field(ge=0, description="Número de erros")
    last_activity: datetime = Field(default_factory=datetime.now)


class Agent(BaseModel):
    """Modelo de agente"""

    id: str = Field(..., description="ID único do agente")
    type: AgentType = Field(..., description="Tipo do agente")
    status: AgentStatus = Field(
        default=AgentStatus.INACTIVE, description="Status atual"
    )
    name: str = Field(..., description="Nome do agente")
    description: Optional[str] = Field(None, description="Descrição do agente")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configurações")
    metrics: Optional[AgentMetrics] = Field(None, description="Métricas de performance")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0.0", description="Versão do agente")

    class Config:
        use_enum_values = True


class AgentCreateRequest(BaseModel):
    """Request para criação de agente"""

    type: AgentType
    name: str
    description: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class AgentUpdateRequest(BaseModel):
    """Request para atualização de agente"""

    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[AgentStatus] = None


class AgentListResponse(BaseModel):
    """Response para lista de agentes"""

    agents: List[Agent]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class AgentHealthCheck(BaseModel):
    """Health check do agente"""

    agent_id: str
    status: AgentStatus
    is_healthy: bool
    last_check: datetime
    response_time: float
    error_message: Optional[str] = None

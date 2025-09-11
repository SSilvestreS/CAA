"""
Aplicação FastAPI principal com todos os endpoints.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import uvicorn
from datetime import datetime
import logging
from typing import Optional, Dict, Any

# Imports dos módulos do sistema
from src.security.auth import AuthService, User, UserRole
from src.security.rbac import RBACService, Permission, Resource
from src.security.audit import AuditLogger
from src.monitoring.metrics import MetricsRegistry, MetricsCollector
from src.monitoring.alerts import AlertManager, AlertRule, AlertSeverity
from src.realtime.event_sourcing import EventStore

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização dos serviços
auth_service = AuthService(secret_key="your-secret-key-here")
rbac_service = RBACService()
audit_logger = AuditLogger()
metrics_registry = MetricsRegistry()
metrics_collector = MetricsCollector(metrics_registry)
alert_manager = AlertManager()
event_store = EventStore()

# Cria aplicação FastAPI
app = FastAPI(
    title="Cidades Autônomas com Agentes de IA API",
    description="API RESTful para simulação de cidade inteligente com múltiplos agentes de IA",
    version="1.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]
)  # Em produção, especificar hosts permitidos

# Security
security = HTTPBearer()


# Middleware de autenticação
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware de autenticação para rotas protegidas."""
    # Rotas públicas que não precisam de autenticação
    public_routes = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/metrics",
        "/auth/login",
        "/auth/register",
    ]

    if request.url.path in public_routes:
        response = await call_next(request)
        return response

    # Verifica token de autenticação
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token de autenticação necessário"},
        )

    token = authorization.split(" ")[1]
    token_payload = auth_service.verify_token(token)

    if not token_payload:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token inválido ou expirado"},
        )

    # Adiciona informações do usuário ao request
    request.state.user_id = token_payload.user_id
    request.state.user_role = token_payload.role

    response = await call_next(request)
    return response


# Middleware de métricas
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware para coleta de métricas."""
    start_time = datetime.now()

    response = await call_next(request)

    # Calcula duração da requisição
    duration = (datetime.now() - start_time).total_seconds()

    # Registra métricas
    metrics_collector.record_request(
        method=request.method,
        endpoint=request.url.path,
        duration=duration,
        status=response.status_code,
    )

    return response


# Middleware de auditoria
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Middleware para auditoria de requisições."""
    start_time = datetime.now()

    response = await call_next(request)

    # Registra evento de auditoria
    if hasattr(request.state, "user_id"):
        audit_event = {
            "event_id": f"req_{int(start_time.timestamp())}",
            "event_type": "user_action",
            "severity": "low",
            "timestamp": start_time,
            "user_id": request.state.user_id,
            "resource": request.url.path,
            "action": request.method,
            "details": {
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent", ""),
                "status_code": response.status_code,
            },
            "result": "success" if response.status_code < 400 else "failure",
            "message": f"Requisição {request.method} {request.url.path}",
        }

        # Aqui você salvaria o evento de auditoria
        logger.info(f"Audit: {audit_event}")

    return response


# Dependências
def get_current_user(request: Request) -> Dict[str, Any]:
    """Obtém usuário atual do request."""
    return {"user_id": request.state.user_id, "role": request.state.user_role}




# Rotas de saúde e status
@app.get("/health")
async def health_check():
    """Verifica saúde da aplicação."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.4.0",
    }


@app.get("/metrics")
async def get_metrics():
    """Retorna métricas da aplicação."""
    return metrics_registry.get_all_metrics_data()


# Rotas de autenticação
@app.post("/auth/login")
async def login(credentials: Dict[str, str]):
    """Endpoint de login."""
    username = credentials.get("username")
    password = credentials.get("password")

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username e password são obrigatórios",
        )

    # Aqui você validaria as credenciais no banco de dados
    # Por simplicidade, vamos criar um usuário mock
    user = User(
        id="user_123",
        username=username,
        email=f"{username}@example.com",
        password_hash=auth_service.hash_password(password),
        role=UserRole.VIEWER,
    )

    # Verifica senha
    if not auth_service.verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )

    # Gera tokens
    tokens = auth_service.generate_tokens(user)

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "expires_in": tokens["expires_in"],
    }


@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Endpoint para renovar access token."""
    tokens = auth_service.refresh_access_token(refresh_token)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido"
        )

    return tokens


@app.post("/auth/logout")
async def logout(token: str = Depends(security)):
    """Endpoint de logout."""
    success = auth_service.revoke_token(token.credentials)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido"
        )

    return {"message": "Logout realizado com sucesso"}


# Rotas de simulação
@app.get("/simulation/status")
async def get_simulation_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retorna status da simulação."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.SIMULATION, Permission.READ_SIMULATION
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    return {
        "status": "running",
        "cycle": 150,
        "agents_count": 100,
        "started_at": "2024-01-01T10:00:00Z",
        "last_update": datetime.now().isoformat(),
    }


@app.post("/simulation/start")
async def start_simulation(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Inicia simulação."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.SIMULATION, Permission.START_SIMULATION
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para iniciar simulação
    return {
        "message": "Simulação iniciada com sucesso",
        "simulation_id": "sim_123",
        "started_at": datetime.now().isoformat(),
    }


@app.post("/simulation/stop")
async def stop_simulation(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Para simulação."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.SIMULATION, Permission.STOP_SIMULATION
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para parar simulação
    return {
        "message": "Simulação parada com sucesso",
        "stopped_at": datetime.now().isoformat(),
    }


@app.post("/simulation/pause")
async def pause_simulation(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Pausa simulação."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.SIMULATION, Permission.PAUSE_SIMULATION
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para pausar simulação
    return {
        "message": "Simulação pausada com sucesso",
        "paused_at": datetime.now().isoformat(),
    }


# Rotas de agentes
@app.get("/agents")
async def list_agents(
    page: int = 1,
    limit: int = 20,
    agent_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Lista agentes."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.AGENTS, Permission.READ_AGENT
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para listar agentes
    agents = [
        {
            "id": f"agent_{i}",
            "type": (
                "citizen" if i % 3 == 0 else "business" if i % 3 == 1 else "government"
            ),
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        for i in range(1, 21)
    ]

    if agent_type:
        agents = [a for a in agents if a["type"] == agent_type]

    return {
        "agents": agents,
        "pagination": {"page": page, "limit": limit, "total": len(agents)},
    }


@app.get("/agents/{agent_id}")
async def get_agent(
    agent_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obtém detalhes de um agente."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.AGENTS, Permission.READ_AGENT
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para obter agente
    return {
        "id": agent_id,
        "type": "citizen",
        "status": "active",
        "position": {"x": 100, "y": 200},
        "properties": {"age": 30, "income": 50000, "happiness": 0.8},
        "created_at": datetime.now().isoformat(),
    }


@app.post("/agents")
async def create_agent(
    agent_data: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Cria novo agente."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.AGENTS, Permission.CREATE_AGENT
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para criar agente
    agent_id = f"agent_{int(datetime.now().timestamp())}"

    return {
        "id": agent_id,
        "message": "Agente criado com sucesso",
        "created_at": datetime.now().isoformat(),
    }


@app.put("/agents/{agent_id}")
async def update_agent(
    agent_id: str,
    agent_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Atualiza agente."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.AGENTS, Permission.UPDATE_AGENT
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para atualizar agente
    return {
        "id": agent_id,
        "message": "Agente atualizado com sucesso",
        "updated_at": datetime.now().isoformat(),
    }


@app.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Deleta agente."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.AGENTS, Permission.DELETE_AGENT
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para deletar agente
    return {
        "message": "Agente deletado com sucesso",
        "deleted_at": datetime.now().isoformat(),
    }


# Rotas de relatórios
@app.get("/reports")
async def list_reports(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Lista relatórios disponíveis."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.REPORTS, Permission.READ_REPORTS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    reports = [
        {
            "id": "report_1",
            "name": "Relatório de Performance",
            "type": "performance",
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": "report_2",
            "name": "Relatório de Agentes",
            "type": "agents",
            "created_at": datetime.now().isoformat(),
        },
    ]

    return {"reports": reports}


@app.get("/reports/{report_id}")
async def get_report(
    report_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Obtém relatório específico."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.REPORTS, Permission.READ_REPORTS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para obter relatório
    return {
        "id": report_id,
        "name": "Relatório de Performance",
        "data": {
            "metrics": metrics_registry.get_all_metrics_data(),
            "generated_at": datetime.now().isoformat(),
        },
    }


# Rotas de alertas
@app.get("/alerts")
async def list_alerts(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Lista alertas ativos."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.LOGS, Permission.READ_LOGS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    active_alerts = alert_manager.get_active_alerts()
    return {"alerts": [alert.to_dict() for alert in active_alerts]}


@app.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Reconhece alerta."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.LOGS, Permission.READ_LOGS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    success = alert_manager.acknowledge_alert(alert_id, current_user["user_id"])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alerta não encontrado"
        )

    return {"message": "Alerta reconhecido com sucesso"}


# Rotas de configuração
@app.get("/config")
async def get_config(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Obtém configurações do sistema."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.CONFIG, Permission.READ_CONFIG
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    return {
        "simulation": {"max_agents": 1000, "cycle_duration": 1.0, "auto_save": True},
        "ai": {"learning_rate": 0.01, "batch_size": 32, "epochs": 100},
    }


@app.put("/config")
async def update_config(
    config_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Atualiza configurações do sistema."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.CONFIG, Permission.UPDATE_CONFIG
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para atualizar configurações
    return {
        "message": "Configurações atualizadas com sucesso",
        "updated_at": datetime.now().isoformat(),
    }


# Rotas de eventos
@app.get("/events")
async def list_events(
    event_type: Optional[str] = None,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Lista eventos do sistema."""
    if not rbac_service.has_resource_permission(
        current_user["user_id"], Resource.LOGS, Permission.READ_LOGS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
        )

    # Lógica para listar eventos
    events = [
        {
            "id": f"event_{i}",
            "type": "agent_action",
            "timestamp": datetime.now().isoformat(),
            "data": {"agent_id": f"agent_{i}", "action": "move"},
        }
        for i in range(1, 11)
    ]

    if event_type:
        events = [e for e in events if e["type"] == event_type]

    return {"events": events[:limit], "total": len(events)}


# Handler de erros
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais."""
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor"},
    )


def _initialize_default_alerts():
    """Inicializa alertas padrão do sistema."""
    # Alerta de alta utilização de CPU
    cpu_alert = AlertRule(
        name="high_cpu_usage",
        description="Alerta de alta utilização de CPU",
        metric_name="cpu_usage_percent",
        condition=">",
        threshold=80.0,
        severity=AlertSeverity.WARNING,
        duration=60,  # 1 minuto
    )
    alert_manager.add_rule(cpu_alert)

    # Alerta de alta utilização de memória
    memory_alert = AlertRule(
        name="high_memory_usage",
        description="Alerta de alta utilização de memória",
        metric_name="memory_usage_bytes",
        condition=">",
        threshold=8 * 1024 * 1024 * 1024,  # 8GB
        severity=AlertSeverity.ERROR,
        duration=30,  # 30 segundos
    )
    alert_manager.add_rule(memory_alert)

    # Alerta de muitas requisições falhadas
    error_alert = AlertRule(
        name="high_error_rate",
        description="Alerta de alta taxa de erro",
        metric_name="request_errors_total",
        condition=">",
        threshold=10,
        severity=AlertSeverity.CRITICAL,
        duration=0,  # Imediato
    )
    alert_manager.add_rule(error_alert)

    # Inicia avaliação de alertas
    alert_manager.start_evaluation()


# Inicializa alertas padrão
_initialize_default_alerts()

if __name__ == "__main__":
    uvicorn.run("src.api.fastapi_app:app", host="0.0.0.0", port=8000, reload=True)

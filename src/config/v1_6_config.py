"""
Configuração da Versão 1.6 - MLOps e Escalabilidade
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class Environment(str, Enum):
    """Ambientes de execução"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Níveis de log"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseModel):
    """Configuração do banco de dados"""

    url: str = Field(..., description="URL de conexão do banco")
    pool_size: int = Field(default=10, description="Tamanho do pool de conexões")
    max_overflow: int = Field(default=20, description="Overflow máximo do pool")
    echo: bool = Field(default=False, description="Echo de queries SQL")
    pool_pre_ping: bool = Field(default=True, description="Pre-ping do pool")


class RedisConfig(BaseModel):
    """Configuração do Redis"""

    url: str = Field(..., description="URL de conexão do Redis")
    max_connections: int = Field(default=20, description="Máximo de conexões")
    socket_timeout: int = Field(default=5, description="Timeout do socket")
    socket_connect_timeout: int = Field(default=5, description="Timeout de conexão")
    retry_on_timeout: bool = Field(default=True, description="Retry em timeout")


class KafkaConfig(BaseModel):
    """Configuração do Kafka"""

    brokers: List[str] = Field(..., description="Lista de brokers")
    client_id: str = Field(default="cities-ai", description="ID do cliente")
    group_id: str = Field(default="cities-ai-group", description="ID do grupo")
    auto_offset_reset: str = Field(default="latest", description="Reset de offset")
    enable_auto_commit: bool = Field(default=True, description="Auto commit habilitado")
    session_timeout_ms: int = Field(default=30000, description="Timeout de sessão")


class MonitoringConfig(BaseModel):
    """Configuração de monitoramento"""

    prometheus_enabled: bool = Field(default=True, description="Prometheus habilitado")
    jaeger_enabled: bool = Field(default=True, description="Jaeger habilitado")
    metrics_port: int = Field(default=9090, description="Porta de métricas")
    tracing_endpoint: str = Field(
        default="http://jaeger:14268/api/traces", description="Endpoint de tracing"
    )
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Nível de log")


class SecurityConfig(BaseModel):
    """Configuração de segurança"""

    jwt_secret: str = Field(..., description="Chave secreta JWT")
    jwt_algorithm: str = Field(default="HS256", description="Algoritmo JWT")
    jwt_expiration: int = Field(default=3600, description="Expiração JWT em segundos")
    encryption_key: str = Field(..., description="Chave de criptografia")
    cors_origins: List[str] = Field(
        default=["*"], description="Origens CORS permitidas"
    )
    rate_limit_per_minute: int = Field(default=100, description="Rate limit por minuto")


class MLConfig(BaseModel):
    """Configuração de Machine Learning"""

    model_cache_size: int = Field(default=10, description="Tamanho do cache de modelos")
    model_update_interval: int = Field(
        default=3600, description="Intervalo de atualização em segundos"
    )
    training_batch_size: int = Field(
        default=32, description="Tamanho do batch de treinamento"
    )
    max_epochs: int = Field(default=100, description="Máximo de épocas")
    learning_rate: float = Field(default=0.001, description="Taxa de aprendizado")
    device: str = Field(default="cpu", description="Dispositivo (cpu/gpu)")


class ExternalAPIConfig(BaseModel):
    """Configuração de APIs externas"""

    timeout: int = Field(default=30, description="Timeout em segundos")
    retries: int = Field(default=3, description="Número de tentativas")
    retry_delay: int = Field(
        default=1, description="Delay entre tentativas em segundos"
    )
    rate_limit: int = Field(default=100, description="Rate limit por minuto")
    weather_api_key: Optional[str] = Field(
        default=None, description="Chave da API de clima"
    )
    maps_api_key: Optional[str] = Field(
        default=None, description="Chave da API de mapas"
    )


class NotificationConfig(BaseModel):
    """Configuração de notificações"""

    email_smtp_server: str = Field(
        default="smtp.gmail.com", description="Servidor SMTP"
    )
    email_smtp_port: int = Field(default=587, description="Porta SMTP")
    email_username: Optional[str] = Field(default=None, description="Usuário do email")
    email_password: Optional[str] = Field(default=None, description="Senha do email")
    slack_webhook_url: Optional[str] = Field(
        default=None, description="URL do webhook do Slack"
    )
    sms_provider: Optional[str] = Field(default=None, description="Provedor de SMS")


class CacheConfig(BaseModel):
    """Configuração de cache"""

    ttl: int = Field(default=3600, description="TTL em segundos")
    max_size: int = Field(default=1000, description="Tamanho máximo do cache")
    cleanup_interval: int = Field(
        default=300, description="Intervalo de limpeza em segundos"
    )


class PerformanceConfig(BaseModel):
    """Configuração de performance"""

    max_workers: int = Field(default=4, description="Máximo de workers")
    worker_timeout: int = Field(
        default=30, description="Timeout dos workers em segundos"
    )
    memory_limit: int = Field(default=1024, description="Limite de memória em MB")
    cpu_limit: float = Field(default=1.0, description="Limite de CPU")


class V16Config(BaseModel):
    """Configuração principal da versão 1.6"""

    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Ambiente de execução"
    )
    debug: bool = Field(default=False, description="Modo debug")

    # Configurações de serviços
    database: DatabaseConfig = Field(..., description="Configuração do banco de dados")
    redis: RedisConfig = Field(..., description="Configuração do Redis")
    kafka: KafkaConfig = Field(..., description="Configuração do Kafka")

    # Configurações de infraestrutura
    monitoring: MonitoringConfig = Field(
        default_factory=MonitoringConfig, description="Configuração de monitoramento"
    )
    security: SecurityConfig = Field(..., description="Configuração de segurança")

    # Configurações de funcionalidades
    ml: MLConfig = Field(default_factory=MLConfig, description="Configuração de ML")
    external_api: ExternalAPIConfig = Field(
        default_factory=ExternalAPIConfig, description="Configuração de APIs externas"
    )
    notification: NotificationConfig = Field(
        default_factory=NotificationConfig, description="Configuração de notificações"
    )
    cache: CacheConfig = Field(
        default_factory=CacheConfig, description="Configuração de cache"
    )
    performance: PerformanceConfig = Field(
        default_factory=PerformanceConfig, description="Configuração de performance"
    )

    # Configurações de microserviços
    agent_service_port: int = Field(default=8001, description="Porta do Agent Service")
    ai_service_port: int = Field(default=8002, description="Porta do AI Service")
    data_service_port: int = Field(default=8003, description="Porta do Data Service")
    analytics_service_port: int = Field(
        default=8004, description="Porta do Analytics Service"
    )
    notification_service_port: int = Field(
        default=8005, description="Porta do Notification Service"
    )

    class Config:
        env_prefix = "CITIES_AI_"
        case_sensitive = False


# Configurações padrão para diferentes ambientes
DEFAULT_CONFIGS = {
    Environment.DEVELOPMENT: {
        "database": {
            "url": "postgresql://postgres:password@localhost:5432/cities_dev",
            "pool_size": 5,
            "echo": True,
        },
        "redis": {"url": "redis://localhost:6379", "max_connections": 10},
        "kafka": {"brokers": ["localhost:9092"]},
        "security": {
            "jwt_secret": "dev-secret-key",
            "encryption_key": "dev-encryption-key",
        },
        "monitoring": {"log_level": LogLevel.DEBUG},
    },
    Environment.STAGING: {
        "database": {
            "url": "postgresql://postgres:password@staging-db:5432/cities_staging",
            "pool_size": 10,
        },
        "redis": {"url": "redis://staging-redis:6379", "max_connections": 20},
        "kafka": {"brokers": ["staging-kafka:9092"]},
        "security": {
            "jwt_secret": "staging-secret-key",
            "encryption_key": "staging-encryption-key",
        },
        "monitoring": {"log_level": LogLevel.INFO},
    },
    Environment.PRODUCTION: {
        "database": {
            "url": "postgresql://postgres:password@prod-db:5432/cities_prod",
            "pool_size": 20,
            "max_overflow": 30,
        },
        "redis": {"url": "redis://prod-redis:6379", "max_connections": 50},
        "kafka": {
            "brokers": ["prod-kafka-1:9092", "prod-kafka-2:9092", "prod-kafka-3:9092"]
        },
        "security": {
            "jwt_secret": "prod-secret-key",
            "encryption_key": "prod-encryption-key",
        },
        "monitoring": {"log_level": LogLevel.WARNING},
        "performance": {"max_workers": 8, "memory_limit": 2048, "cpu_limit": 2.0},
    },
}


def get_config(environment: Environment = Environment.DEVELOPMENT) -> V16Config:
    """Obtém configuração para o ambiente especificado"""
    config_data = DEFAULT_CONFIGS.get(
        environment, DEFAULT_CONFIGS[Environment.DEVELOPMENT]
    )

    # Cria configuração com valores padrão
    return V16Config(**config_data)


def load_config_from_env() -> V16Config:
    """Carrega configuração das variáveis de ambiente"""
    import os

    config_data = {}

    # Carrega configurações básicas
    config_data["environment"] = os.getenv("CITIES_AI_ENVIRONMENT", "development")
    config_data["debug"] = os.getenv("CITIES_AI_DEBUG", "false").lower() == "true"

    # Carrega configurações do banco
    config_data["database"] = {
        "url": os.getenv(
            "CITIES_AI_DATABASE_URL",
            "postgresql://postgres:password@localhost:5432/cities_dev",
        ),
        "pool_size": int(os.getenv("CITIES_AI_DATABASE_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("CITIES_AI_DATABASE_MAX_OVERFLOW", "20")),
        "echo": os.getenv("CITIES_AI_DATABASE_ECHO", "false").lower() == "true",
    }

    # Carrega configurações do Redis
    config_data["redis"] = {
        "url": os.getenv("CITIES_AI_REDIS_URL", "redis://localhost:6379"),
        "max_connections": int(os.getenv("CITIES_AI_REDIS_MAX_CONNECTIONS", "20")),
    }

    # Carrega configurações do Kafka
    kafka_brokers = os.getenv("CITIES_AI_KAFKA_BROKERS", "localhost:9092")
    config_data["kafka"] = {"brokers": kafka_brokers.split(",")}

    # Carrega configurações de segurança
    config_data["security"] = {
        "jwt_secret": os.getenv("CITIES_AI_JWT_SECRET", "default-secret-key"),
        "encryption_key": os.getenv(
            "CITIES_AI_ENCRYPTION_KEY", "default-encryption-key"
        ),
    }

    return V16Config(**config_data)

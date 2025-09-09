"""
Integrações Externas
Versão 1.6 - MLOps e Escalabilidade
"""

from .external_apis import ExternalAPIManager, APIType, APIConfig
from .iot_connector import IoTConnector
from .database_connector import DatabaseConnector
from .webhook_manager import WebhookManager

__all__ = [
    "ExternalAPIManager",
    "APIType",
    "APIConfig",
    "IoTConnector",
    "DatabaseConnector",
    "WebhookManager",
]

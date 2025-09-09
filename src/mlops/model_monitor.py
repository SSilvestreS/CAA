"""
Model Monitor para MLOps
versão 1.7 - MLOps e Escalabilidade
"""

import logging

logger = logging.getLogger(__name__)


class ModelMonitor:
    """Monitor de modelos ML"""

    def __init__(self):
        self.running = False

    async def start(self):
        """Inicia o monitor"""
        self.running = True
        logger.info("Model Monitor iniciado")

    async def stop(self):
        """Para o monitor"""
        self.running = False
        logger.info("Model Monitor parado")

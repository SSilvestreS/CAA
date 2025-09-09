"""
Experiment Tracker para MLOps
Versão 1.6 - MLOps e Escalabilidade
"""

import logging

logger = logging.getLogger(__name__)


class ExperimentTracker:
    """Tracker de experimentos ML"""

    def __init__(self):
        self.running = False

    async def start(self):
        """Inicia o tracker"""
        self.running = True
        logger.info("Experiment Tracker iniciado")

    async def stop(self):
        """Para o tracker"""
        self.running = False
        logger.info("Experiment Tracker parado")

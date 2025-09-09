"""
Base Optimizer - Clean Code & KISS
Versão 1.6 - Classe base para otimizadores
"""

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Resultado de uma otimização"""

    target_name: str
    before_value: float
    after_value: float
    improvement: float
    method_used: str
    execution_time: float
    success: bool
    timestamp: datetime


class BaseOptimizer(ABC):
    """Classe base para otimizadores - Clean Code & KISS"""

    def __init__(self):
        self.results = []
        self.running = False
        self.lock = threading.Lock()

    def start(self) -> None:
        """Inicia otimizador"""
        self.running = True
        logger.info(f"{self.__class__.__name__} iniciado")

    def stop(self) -> None:
        """Para otimizador"""
        self.running = False
        logger.info(f"{self.__class__.__name__} parado")

    def _record_result(
        self,
        target_name: str,
        before_value: float,
        after_value: float,
        method_used: str,
        execution_time: float,
        success: bool,
    ) -> None:
        """Registra resultado da otimização"""
        improvement = self._calculate_improvement(before_value, after_value)

        result = OptimizationResult(
            target_name=target_name,
            before_value=before_value,
            after_value=after_value,
            improvement=improvement,
            method_used=method_used,
            execution_time=execution_time,
            success=success,
            timestamp=datetime.now(),
        )

        with self.lock:
            self.results.append(result)

    def _calculate_improvement(self, before: float, after: float) -> float:
        """Calcula melhoria percentual"""
        if before == 0:
            return 0.0
        return ((before - after) / before) * 100

    def get_results(self) -> List[OptimizationResult]:
        """Obtém resultados de otimização"""
        with self.lock:
            return self.results.copy()

    def clear_results(self) -> None:
        """Limpa resultados"""
        with self.lock:
            self.results.clear()

    @abstractmethod
    def optimize(self, target: str) -> bool:
        """Executa otimização"""
        pass

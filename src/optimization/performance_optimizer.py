"""
Sistema de Otimização de Performance - Clean Code & KISS
Versão 1.6 - Refatorado para Clean Code
"""

import gc
import logging
import multiprocessing as mp
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil
from .base_optimizer import BaseOptimizer

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Tipos de otimização"""

    MEMORY = "memory"
    CPU = "cpu"
    CACHE = "cache"
    PARALLEL = "parallel"


class OptimizationLevel(Enum):
    """Níveis de otimização"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class PerformanceMetric:
    """Métrica de performance"""

    name: str
    value: float
    unit: str
    timestamp: datetime


@dataclass
class OptimizationConfig:
    """Configuração de otimização"""

    optimization_type: OptimizationType
    level: OptimizationLevel
    threshold: float
    frequency: int
    parameters: Dict[str, Any]


class SystemMonitor:
    """Monitor simples do sistema"""

    def __init__(self):
        self.metrics = {}

    def get_cpu_usage(self) -> float:
        """Obtém uso de CPU"""
        return psutil.cpu_percent()

    def get_memory_usage(self) -> float:
        """Obtém uso de memória"""
        return psutil.virtual_memory().percent

    def get_system_metrics(self) -> Dict[str, float]:
        """Obtém métricas do sistema"""
        return {
            "cpu_usage": self.get_cpu_usage(),
            "memory_usage": self.get_memory_usage(),
            "active_threads": threading.active_count(),
        }


class CacheManager:
    """Gerenciador de cache simples"""

    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.timestamps = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if key not in self.cache:
            return None

        if self._is_expired(key):
            self._remove(key)
            return None

        return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """Define valor no cache"""
        self.cache[key] = value
        self.timestamps[key] = datetime.now()

    def clear(self) -> None:
        """Limpa cache"""
        self.cache.clear()
        self.timestamps.clear()

    def _is_expired(self, key: str) -> bool:
        """Verifica se chave expirou"""
        if key not in self.timestamps:
            return True
        return (datetime.now() - self.timestamps[key]).total_seconds() > self.ttl

    def _remove(self, key: str) -> None:
        """Remove chave do cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)


class MemoryOptimizer:
    """Otimizador de memória"""

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.monitor = SystemMonitor()

    def should_optimize(self) -> bool:
        """Verifica se deve otimizar memória"""
        return self.monitor.get_memory_usage() > self.threshold * 100

    def optimize(self) -> bool:
        """Executa otimização de memória"""
        if not self.should_optimize():
            return False

        # Força garbage collection
        gc.collect()
        logger.info("Otimização de memória executada")
        return True


class CPUOptimizer:
    """Otimizador de CPU"""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.monitor = SystemMonitor()

    def should_optimize(self) -> bool:
        """Verifica se deve otimizar CPU"""
        return self.monitor.get_cpu_usage() > self.threshold * 100

    def optimize(self) -> bool:
        """Executa otimização de CPU"""
        if not self.should_optimize():
            return False

        # Pausa breve para reduzir carga
        time.sleep(0.1)
        logger.info("Otimização de CPU executada")
        return True


class PerformanceOptimizer(BaseOptimizer):
    """Otimizador principal - Clean Code & KISS"""

    def __init__(self, simulation_manager):
        super().__init__()
        self.simulation_manager = simulation_manager
        self.monitor = SystemMonitor()
        self.cache = CacheManager()
        self.memory_optimizer = MemoryOptimizer()
        self.cpu_optimizer = CPUOptimizer()

        # Thread pools
        self.thread_pool = ThreadPoolExecutor(max_workers=mp.cpu_count())
        self.process_pool = ProcessPoolExecutor(max_workers=mp.cpu_count())

    def start(self) -> None:
        """Inicia otimizador"""
        super().start()
        self._start_optimization_thread()

    def stop(self) -> None:
        """Para otimizador"""
        super().stop()
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

    def _start_optimization_thread(self) -> None:
        """Inicia thread de otimização"""
        thread = threading.Thread(target=self._optimization_loop, daemon=True)
        thread.start()

    def _optimization_loop(self) -> None:
        """Loop principal de otimização"""
        while self.running:
            try:
                self._run_optimizations()
                time.sleep(60)  # Verifica a cada minuto
            except Exception as e:
                logger.error(f"Erro no loop de otimização: {e}")
                time.sleep(30)

    def _run_optimizations(self) -> None:
        """Executa otimizações"""
        # Otimização de memória
        if self.memory_optimizer.optimize():
            self._record_optimization_result("memory", True)

        # Otimização de CPU
        if self.cpu_optimizer.optimize():
            self._record_optimization_result("cpu", True)

        # Limpeza de cache
        self._cleanup_cache()

    def _cleanup_cache(self) -> None:
        """Limpa cache expirado"""
        expired_keys = [
            key for key in self.cache.timestamps if self.cache._is_expired(key)
        ]

        for key in expired_keys:
            self.cache._remove(key)

    def _record_optimization_result(
        self, optimization_type: str, success: bool
    ) -> None:
        """Registra resultado da otimização"""
        self._record_result(
            target_name=optimization_type,
            before_value=0.0,
            after_value=0.0,
            method_used=f"{optimization_type}_optimizer",
            execution_time=0.0,
            success=success,
        )

    def get_cache(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        return self.cache.get(key)

    def set_cache(self, key: str, value: Any) -> None:
        """Define valor no cache"""
        self.cache.set(key, value)

    def clear_cache(self) -> None:
        """Limpa cache"""
        self.cache.clear()

    def get_system_metrics(self) -> Dict[str, float]:
        """Obtém métricas do sistema"""
        return self.monitor.get_system_metrics()

    def optimize(self, target: str) -> bool:
        """Executa otimização"""
        if target == "memory":
            return self.memory_optimizer.optimize()
        elif target == "cpu":
            return self.cpu_optimizer.optimize()
        return False

    def get_optimization_results(self) -> List[Any]:
        """Obtém resultados de otimização"""
        return self.get_results()

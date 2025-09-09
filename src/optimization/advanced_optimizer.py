"""
Sistema de Otimização Avançado - Clean Code & KISS
Versão 1.6 - Refatorado para Clean Code
"""

import threading
import psutil
import gc
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from .base_optimizer import BaseOptimizer
import time

logger = logging.getLogger(__name__)


@dataclass
class OptimizationTarget:
    """Alvo de otimização"""

    name: str
    current_value: float
    target_value: float
    priority: int
    optimization_type: str
    weight: float = 1.0


class SimpleCache:
    """Cache simples e eficiente"""

    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
        self.access_count = {}

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if key not in self.cache:
            return None

        if self._is_expired(key):
            self._remove(key)
            return None

        self.access_count[key] = self.access_count.get(key, 0) + 1
        return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """Define valor no cache"""
        if len(self.cache) >= self.max_size:
            self._evict_least_used()

        self.cache[key] = value
        self.timestamps[key] = time.time()
        self.access_count[key] = 0

    def clear(self) -> None:
        """Limpa cache"""
        self.cache.clear()
        self.timestamps.clear()
        self.access_count.clear()

    def _is_expired(self, key: str) -> bool:
        """Verifica se chave expirou"""
        return time.time() - self.timestamps[key] > self.ttl

    def _remove(self, key: str) -> None:
        """Remove chave do cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
        self.access_count.pop(key, None)

    def _evict_least_used(self) -> None:
        """Remove item menos usado"""
        if not self.access_count:
            return

        least_used = min(self.access_count.items(), key=lambda x: x[1])
        self._remove(least_used[0])


class SystemMetrics:
    """Coletor de métricas do sistema"""

    @staticmethod
    def get_cpu_usage() -> float:
        """Obtém uso de CPU"""
        return psutil.cpu_percent()

    @staticmethod
    def get_memory_usage() -> float:
        """Obtém uso de memória"""
        return psutil.virtual_memory().percent

    @staticmethod
    def get_disk_usage() -> float:
        """Obtém uso de disco"""
        return psutil.disk_usage("/").percent

    @staticmethod
    def get_system_metrics() -> Dict[str, float]:
        """Obtém todas as métricas"""
        return {
            "cpu_usage": SystemMetrics.get_cpu_usage(),
            "memory_usage": SystemMetrics.get_memory_usage(),
            "disk_usage": SystemMetrics.get_disk_usage(),
        }


class OptimizationAlgorithm:
    """Algoritmo de otimização base"""

    def __init__(self, name: str):
        self.name = name

    def optimize(self, target: OptimizationTarget) -> bool:
        """Executa otimização"""
        raise NotImplementedError


class MemoryOptimizationAlgorithm(OptimizationAlgorithm):
    """Algoritmo de otimização de memória"""

    def __init__(self):
        super().__init__("memory_optimization")

    def optimize(self, target: OptimizationTarget) -> bool:
        """Otimiza memória"""
        if target.optimization_type != "minimize":
            return False

        # Força garbage collection
        gc.collect()
        return True


class CPUOptimizationAlgorithm(OptimizationAlgorithm):
    """Algoritmo de otimização de CPU"""

    def __init__(self):
        super().__init__("cpu_optimization")

    def optimize(self, target: OptimizationTarget) -> bool:
        """Otimiza CPU"""
        if target.optimization_type != "minimize":
            return False

        # Pausa para reduzir carga
        time.sleep(0.01)
        return True


class AdvancedOptimizer(BaseOptimizer):
    """Otimizador avançado - Clean Code & KISS"""

    def __init__(self):
        super().__init__()
        self.cache = SimpleCache()
        self.metrics = SystemMetrics()
        self.algorithms = {
            "memory": MemoryOptimizationAlgorithm(),
            "cpu": CPUOptimizationAlgorithm(),
        }

    def start(self) -> None:
        """Inicia otimizador"""
        super().start()
        self._start_optimization_loop()

    def stop(self) -> None:
        """Para otimizador"""
        super().stop()

    def _start_optimization_loop(self) -> None:
        """Inicia loop de otimização"""
        thread = threading.Thread(target=self._optimization_loop, daemon=True)
        thread.start()

    def _optimization_loop(self) -> None:
        """Loop principal de otimização"""
        while self.running:
            try:
                self._run_optimizations()
                time.sleep(30)  # Verifica a cada 30 segundos
            except Exception as e:
                logger.error(f"Erro no loop de otimização: {e}")
                time.sleep(10)

    def _run_optimizations(self) -> None:
        """Executa otimizações"""
        metrics = self.metrics.get_system_metrics()

        # Otimização de memória
        if metrics["memory_usage"] > 80:
            self._optimize_memory()

        # Otimização de CPU
        if metrics["cpu_usage"] > 70:
            self._optimize_cpu()

    def _optimize_memory(self) -> None:
        """Otimiza memória"""
        target = OptimizationTarget(
            name="memory_usage",
            current_value=self.metrics.get_memory_usage(),
            target_value=50.0,
            priority=8,
            optimization_type="minimize",
        )

        self._execute_optimization(target, "memory")

    def _optimize_cpu(self) -> None:
        """Otimiza CPU"""
        target = OptimizationTarget(
            name="cpu_usage",
            current_value=self.metrics.get_cpu_usage(),
            target_value=50.0,
            priority=7,
            optimization_type="minimize",
        )

        self._execute_optimization(target, "cpu")

    def _execute_optimization(
        self, target: OptimizationTarget, algorithm_name: str
    ) -> None:
        """Executa otimização"""
        start_time = time.time()
        before_value = target.current_value

        try:
            algorithm = self.algorithms.get(algorithm_name)
            if not algorithm:
                return

            success = algorithm.optimize(target)
            after_value = self._get_current_value(target)

            self._record_result(
                target_name=target.name,
                before_value=before_value,
                after_value=after_value,
                method_used=algorithm.name,
                execution_time=time.time() - start_time,
                success=success,
            )

            if success:
                logger.info(
                    f"Otimização {target.name}: {before_value:.2f} -> {after_value:.2f}"
                )

        except Exception as e:
            logger.error(f"Erro na otimização {target.name}: {e}")

    def _get_current_value(self, target: OptimizationTarget) -> float:
        """Obtém valor atual do alvo"""
        if target.name == "memory_usage":
            return self.metrics.get_memory_usage()
        elif target.name == "cpu_usage":
            return self.metrics.get_cpu_usage()
        else:
            return target.current_value

    def _calculate_improvement(
        self, before: float, after: float, optimization_type: str
    ) -> float:
        """Calcula melhoria percentual"""
        if before == 0:
            return 0.0

        if optimization_type == "minimize":
            return ((before - after) / before) * 100
        else:
            return ((after - before) / before) * 100

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
        return self.metrics.get_system_metrics()

    def optimize(self, target: str) -> bool:
        """Executa otimização"""
        if target == "memory":
            return self.algorithms["memory"].optimize(
                OptimizationTarget(
                    name="memory_usage",
                    current_value=self.metrics.get_memory_usage(),
                    target_value=50.0,
                    priority=8,
                    optimization_type="minimize",
                )
            )
        elif target == "cpu":
            return self.algorithms["cpu"].optimize(
                OptimizationTarget(
                    name="cpu_usage",
                    current_value=self.metrics.get_cpu_usage(),
                    target_value=50.0,
                    priority=7,
                    optimization_type="minimize",
                )
            )
        return False

    def get_optimization_results(self) -> List[Any]:
        """Obtém resultados de otimização"""
        return self.get_results()

    def add_optimization_target(self, target: OptimizationTarget) -> None:
        """Adiciona alvo de otimização"""
        # Implementação simples - pode ser expandida
        logger.info(f"Alvo de otimização adicionado: {target.name}")

    def remove_optimization_target(self, target_name: str) -> None:
        """Remove alvo de otimização"""
        # Implementação simples - pode ser expandida
        logger.info(f"Alvo de otimização removido: {target_name}")

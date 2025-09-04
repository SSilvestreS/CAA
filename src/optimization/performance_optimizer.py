"""
Sistema de Otimização de Performance para Simulação de Cidade Inteligente
Versão 1.2 - Otimização avançada e profiling
"""

import gc
import logging
import multiprocessing as mp
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Tipos de otimização disponíveis"""

    MEMORY = "memory"
    CPU = "cpu"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    ALGORITHM = "algorithm"
    PARALLEL = "parallel"
    COMPRESSION = "compression"


class OptimizationLevel(Enum):
    """Níveis de otimização"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AGGRESSIVE = "aggressive"


@dataclass
class PerformanceMetric:
    """Métrica de performance"""

    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationConfig:
    """Configuração de otimização"""

    optimization_type: OptimizationType
    level: OptimizationLevel
    enabled: bool = True
    threshold: float = 0.8  # Threshold para ativar otimização
    frequency: int = 60  # Frequência em segundos
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Resultado de uma otimização"""

    optimization_type: OptimizationType
    level: OptimizationLevel
    start_time: datetime
    end_time: datetime
    duration: float
    improvement: float  # Melhoria em percentual
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    success: bool
    error_message: Optional[str] = None


class PerformanceProfiler:
    """Profiler de performance"""

    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.lock = threading.Lock()
        self.start_time = time.time()

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str,
        context: Dict[str, Any] = None,
    ):
        """Registra uma métrica"""
        with self.lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                context=context or {},
            )
            self.metrics.append(metric)

    def get_metric_history(self, name: str, duration_minutes: int = 60) -> List[PerformanceMetric]:
        """Retorna histórico de uma métrica"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        with self.lock:
            return [m for m in self.metrics if m.name == name and m.timestamp >= cutoff_time]

    def get_average_metric(self, name: str, duration_minutes: int = 60) -> float:
        """Retorna média de uma métrica"""
        history = self.get_metric_history(name, duration_minutes)
        if not history:
            return 0.0
        return sum(m.value for m in history) / len(history)

    def get_peak_metric(self, name: str, duration_minutes: int = 60) -> float:
        """Retorna pico de uma métrica"""
        history = self.get_metric_history(name, duration_minutes)
        if not history:
            return 0.0
        return max(m.value for m in history)

    def clear_old_metrics(self, duration_hours: int = 24):
        """Remove métricas antigas"""
        cutoff_time = datetime.now() - timedelta(hours=duration_hours)
        with self.lock:
            self.metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]


class PerformanceOptimizer:
    """Otimizador de performance principal"""

    def __init__(self, simulation_manager):
        self.simulation_manager = simulation_manager
        self.profiler = PerformanceProfiler()
        self.optimization_configs: Dict[OptimizationType, OptimizationConfig] = {}
        self.optimization_results: List[OptimizationResult] = []
        self.running = False
        self.optimization_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Thread pools para processamento paralelo
        self.thread_pool = ThreadPoolExecutor(max_workers=mp.cpu_count())
        self.process_pool = ProcessPoolExecutor(max_workers=mp.cpu_count())

        # Cache para otimizações
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_ttl = 300  # 5 minutos

        # Métricas de sistema
        self.system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_usage": 0.0,
            "active_threads": 0,
            "active_processes": 0,
        }

        self._initialize_optimization_configs()
        self._start_system_monitoring()

    def _initialize_optimization_configs(self):
        """Inicializa configurações de otimização"""

        # Otimização de memória
        self.optimization_configs[OptimizationType.MEMORY] = OptimizationConfig(
            optimization_type=OptimizationType.MEMORY,
            level=OptimizationLevel.MEDIUM,
            threshold=0.8,
            frequency=120,
            parameters={
                "gc_threshold": 0.8,
                "cache_cleanup_interval": 300,
                "memory_limit_mb": 1024,
            },
        )

        # Otimização de CPU
        self.optimization_configs[OptimizationType.CPU] = OptimizationConfig(
            optimization_type=OptimizationType.CPU,
            level=OptimizationLevel.MEDIUM,
            threshold=0.7,
            frequency=60,
            parameters={
                "max_workers": mp.cpu_count(),
                "task_batch_size": 100,
                "cpu_affinity": True,
            },
        )

        # Otimização de cache
        self.optimization_configs[OptimizationType.CACHE] = OptimizationConfig(
            optimization_type=OptimizationType.CACHE,
            level=OptimizationLevel.HIGH,
            threshold=0.6,
            frequency=30,
            parameters={
                "cache_size_limit": 1000,
                "cache_ttl": 300,
                "compression_enabled": True,
            },
        )

        # Otimização paralela
        self.optimization_configs[OptimizationType.PARALLEL] = OptimizationConfig(
            optimization_type=OptimizationType.PARALLEL,
            level=OptimizationLevel.HIGH,
            threshold=0.5,
            frequency=90,
            parameters={
                "parallel_threshold": 50,
                "chunk_size": 1000,
                "load_balancing": True,
            },
        )

        # Otimização de algoritmo
        self.optimization_configs[OptimizationType.ALGORITHM] = OptimizationConfig(
            optimization_type=OptimizationType.ALGORITHM,
            level=OptimizationLevel.AGGRESSIVE,
            threshold=0.4,
            frequency=180,
            parameters={
                "algorithm_optimization": True,
                "data_structure_optimization": True,
                "complexity_reduction": True,
            },
        )

    def _start_system_monitoring(self):
        """Inicia monitoramento do sistema"""

        def monitor_system():
            while self.running:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.system_metrics["cpu_usage"] = cpu_percent
                    self.profiler.record_metric("cpu_usage", cpu_percent, "percent")

                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.system_metrics["memory_usage"] = memory.percent
                    self.profiler.record_metric("memory_usage", memory.percent, "percent")

                    # Disk usage
                    disk = psutil.disk_usage("/")
                    disk_percent = (disk.used / disk.total) * 100
                    self.system_metrics["disk_usage"] = disk_percent
                    self.profiler.record_metric("disk_usage", disk_percent, "percent")

                    # Network usage
                    network = psutil.net_io_counters()
                    self.system_metrics["network_usage"] = network.bytes_sent + network.bytes_recv
                    self.profiler.record_metric(
                        "network_usage",
                        self.system_metrics["network_usage"],
                        "bytes",
                    )

                    # Thread and process count
                    self.system_metrics["active_threads"] = threading.active_count()
                    self.system_metrics["active_processes"] = len(psutil.pids())

                    time.sleep(10)  # Monitorar a cada 10 segundos
                except Exception as e:
                    logger.error(f"Erro no monitoramento do sistema: {e}")
                    time.sleep(10)

        self.monitoring_thread = threading.Thread(target=monitor_system, daemon=True)
        self.monitoring_thread.start()

    def start(self):
        """Inicia o otimizador de performance"""
        if self.running:
            return

        self.running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        logger.info("Otimizador de performance iniciado")

    def stop(self):
        """Para o otimizador de performance"""
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5.0)

        # Fechar thread pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

        logger.info("Otimizador de performance parado")

    def _optimization_loop(self):
        """Loop principal de otimização"""
        while self.running:
            try:
                self._check_optimization_needs()
                self._cleanup_cache()
                self._cleanup_old_metrics()
                time.sleep(30)  # Verifica a cada 30 segundos
            except Exception as e:
                logger.error(f"Erro no loop de otimização: {e}")
                time.sleep(30)

    def _check_optimization_needs(self):
        """Verifica se otimizações são necessárias"""
        for opt_type, config in self.optimization_configs.items():
            if not config.enabled:
                continue

            # Verificar se é hora de otimizar
            if self._should_optimize(opt_type, config):
                self._perform_optimization(opt_type, config)

    def _should_optimize(self, opt_type: OptimizationType, config: OptimizationConfig) -> bool:
        """Verifica se deve otimizar"""
        # Verificar threshold baseado no tipo
        if opt_type == OptimizationType.MEMORY:
            return self.system_metrics["memory_usage"] > config.threshold * 100
        elif opt_type == OptimizationType.CPU:
            return self.system_metrics["cpu_usage"] > config.threshold * 100
        elif opt_type == OptimizationType.CACHE:
            return len(self.cache) > config.parameters.get("cache_size_limit", 1000)
        elif opt_type == OptimizationType.PARALLEL:
            return self.system_metrics["active_threads"] > config.parameters.get("max_workers", 4)

        return False

    def _perform_optimization(self, opt_type: OptimizationType, config: OptimizationConfig):
        """Executa uma otimização"""
        start_time = datetime.now()
        metrics_before = self._get_current_metrics()

        try:
            if opt_type == OptimizationType.MEMORY:
                improvement = self._optimize_memory(config)
            elif opt_type == OptimizationType.CPU:
                improvement = self._optimize_cpu(config)
            elif opt_type == OptimizationType.CACHE:
                improvement = self._optimize_cache(config)
            elif opt_type == OptimizationType.PARALLEL:
                improvement = self._optimize_parallel(config)
            elif opt_type == OptimizationType.ALGORITHM:
                improvement = self._optimize_algorithm(config)
            else:
                improvement = 0.0

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            metrics_after = self._get_current_metrics()

            result = OptimizationResult(
                optimization_type=opt_type,
                level=config.level,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                improvement=improvement,
                metrics_before=metrics_before,
                metrics_after=metrics_after,
                success=True,
            )

            with self.lock:
                self.optimization_results.append(result)

            logger.info(f"Otimização {opt_type.value} concluída: {improvement:.2f}% de melhoria")

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            metrics_after = self._get_current_metrics()

            result = OptimizationResult(
                optimization_type=opt_type,
                level=config.level,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                improvement=0.0,
                metrics_before=metrics_before,
                metrics_after=metrics_after,
                success=False,
                error_message=str(e),
            )

            with self.lock:
                self.optimization_results.append(result)

            logger.error("Erro na otimização %s: %s", opt_type.value, e)

    def _get_current_metrics(self) -> Dict[str, float]:
        """Retorna métricas atuais"""
        return {
            "cpu_usage": self.system_metrics["cpu_usage"],
            "memory_usage": self.system_metrics["memory_usage"],
            "disk_usage": self.system_metrics["disk_usage"],
            "network_usage": self.system_metrics["network_usage"],
            "active_threads": self.system_metrics["active_threads"],
            "active_processes": self.system_metrics["active_processes"],
        }

    def _optimize_memory(self, config: OptimizationConfig) -> float:
        """Otimiza uso de memória"""
        memory_before = self.system_metrics["memory_usage"]

        # Garbage collection
        if memory_before > config.parameters.get("gc_threshold", 0.8) * 100:
            gc.collect()

        # Limpar cache antigo
        self._cleanup_cache()

        # Limpar métricas antigas
        self.profiler.clear_old_metrics(24)

        # Limpar referências fracas
        self._cleanup_weak_references()

        memory_after = self.system_metrics["memory_usage"]
        improvement = max(0, memory_before - memory_after)

        return improvement

    def _optimize_cpu(self, config: OptimizationConfig) -> float:
        """Otimiza uso de CPU"""
        cpu_before = self.system_metrics["cpu_usage"]

        # Ajustar número de workers
        max_workers = config.parameters.get("max_workers", mp.cpu_count())
        if self.thread_pool._max_workers != max_workers:
            self.thread_pool.shutdown(wait=True)
            self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)

        # Otimizar processamento em lote
        batch_size = config.parameters.get("task_batch_size", 100)
        self._optimize_batch_processing(batch_size)

        cpu_after = self.system_metrics["cpu_usage"]
        improvement = max(0, cpu_before - cpu_after)

        return improvement

    def _optimize_cache(self, config: OptimizationConfig) -> float:
        """Otimiza cache"""
        cache_size_before = len(self.cache)

        # Limpar cache expirado
        self._cleanup_cache()

        # Comprimir cache se habilitado
        if config.parameters.get("compression_enabled", True):
            self._compress_cache()

        cache_size_after = len(self.cache)
        improvement = max(0, cache_size_before - cache_size_after) / cache_size_before * 100

        return improvement

    def _optimize_parallel(self, config: OptimizationConfig) -> float:
        """Otimiza processamento paralelo"""
        threads_before = self.system_metrics["active_threads"]

        # Ajustar chunk size para processamento paralelo
        chunk_size = config.parameters.get("chunk_size", 1000)
        self._optimize_chunk_size(chunk_size)

        # Balanceamento de carga
        if config.parameters.get("load_balancing", True):
            self._optimize_load_balancing()

        threads_after = self.system_metrics["active_threads"]
        improvement = max(0, threads_before - threads_after)

        return improvement

    def _optimize_algorithm(self, config: OptimizationConfig) -> float:
        """Otimiza algoritmos"""
        performance_before = self._measure_algorithm_performance()

        # Otimizar estruturas de dados
        if config.parameters.get("data_structure_optimization", True):
            self._optimize_data_structures()

        # Reduzir complexidade
        if config.parameters.get("complexity_reduction", True):
            self._reduce_algorithm_complexity()

        performance_after = self._measure_algorithm_performance()
        improvement = max(0, performance_after - performance_before)

        return improvement

    def _cleanup_cache(self):
        """Limpa cache expirado"""
        current_time = datetime.now()
        expired_keys = []

        for key, timestamp in self.cache_timestamps.items():
            if (current_time - timestamp).total_seconds() > self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]

    def _cleanup_old_metrics(self):
        """Limpa métricas antigas"""
        self.profiler.clear_old_metrics(24)

    def _cleanup_weak_references(self):
        """Limpa referências fracas"""
        # Implementar limpeza de referências fracas
        pass

    def _optimize_batch_processing(self, batch_size: int):
        """Otimiza processamento em lote"""
        # Implementar otimização de processamento em lote
        pass

    def _compress_cache(self):
        """Comprime cache"""
        # Implementar compressão de cache
        pass

    def _optimize_chunk_size(self, chunk_size: int):
        """Otimiza tamanho dos chunks"""
        # Implementar otimização de chunk size
        pass

    def _optimize_load_balancing(self):
        """Otimiza balanceamento de carga"""
        # Implementar balanceamento de carga
        pass

    def _optimize_data_structures(self):
        """Otimiza estruturas de dados"""
        # Implementar otimização de estruturas de dados
        pass

    def _reduce_algorithm_complexity(self):
        """Reduz complexidade dos algoritmos"""
        # Implementar redução de complexidade
        pass

    def _measure_algorithm_performance(self) -> float:
        """Mede performance dos algoritmos"""
        # Implementar medição de performance
        return 0.0

    # Métodos públicos

    def get_cache(self, key: str) -> Any:
        """Obtém valor do cache"""
        if key in self.cache:
            if key in self.cache_timestamps:
                if (datetime.now() - self.cache_timestamps[key]).total_seconds() < self.cache_ttl:
                    return self.cache[key]
                else:
                    # Cache expirado
                    del self.cache[key]
                    del self.cache_timestamps[key]
        return None

    def set_cache(self, key: str, value: Any):
        """Define valor no cache"""
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.now()

    def clear_cache(self):
        """Limpa todo o cache"""
        self.cache.clear()
        self.cache_timestamps.clear()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance"""
        return {
            "system_metrics": self.system_metrics.copy(),
            "cache_size": len(self.cache),
            "optimization_results": len(self.optimization_results),
            "average_cpu": self.profiler.get_average_metric("cpu_usage", 60),
            "average_memory": self.profiler.get_average_metric("memory_usage", 60),
            "peak_cpu": self.profiler.get_peak_metric("cpu_usage", 60),
            "peak_memory": self.profiler.get_peak_metric("memory_usage", 60),
        }

    def get_optimization_history(self) -> List[OptimizationResult]:
        """Retorna histórico de otimizações"""
        with self.lock:
            return self.optimization_results.copy()

    def force_optimization(self, opt_type: OptimizationType):
        """Força uma otimização específica"""
        if opt_type in self.optimization_configs:
            config = self.optimization_configs[opt_type]
            self._perform_optimization(opt_type, config)

    def set_optimization_config(self, opt_type: OptimizationType, config: OptimizationConfig):
        """Define configuração de otimização"""
        self.optimization_configs[opt_type] = config

    def get_optimization_config(self, opt_type: OptimizationType) -> Optional[OptimizationConfig]:
        """Obtém configuração de otimização"""
        return self.optimization_configs.get(opt_type)

    def enable_optimization(self, opt_type: OptimizationType):
        """Habilita otimização"""
        if opt_type in self.optimization_configs:
            self.optimization_configs[opt_type].enabled = True

    def disable_optimization(self, opt_type: OptimizationType):
        """Desabilita otimização"""
        if opt_type in self.optimization_configs:
            self.optimization_configs[opt_type].enabled = False

"""
Sistema de Otimização Avançado para Performance e Escalabilidade.
Implementa algoritmos de otimização inteligente e cache distribuído.
"""

import asyncio
import threading
import time
import psutil
import gc
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationTarget:
    """Alvo de otimização"""

    name: str
    current_value: float
    target_value: float
    priority: int  # 1-10, maior = mais prioritário
    optimization_type: str  # 'minimize', 'maximize', 'maintain'
    weight: float = 1.0


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


class IntelligentCache:
    """Sistema de cache inteligente com predição de acesso"""

    def __init__(self, max_size: int = 10000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, datetime] = {}
        self.access_counts: Dict[str, int] = {}
        self.prediction_model = None

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if key not in self.cache:
            return None

        # Verifica TTL
        if (datetime.now() - self.access_times[key]).seconds > self.ttl:
            self._remove_key(key)
            return None

        # Atualiza estatísticas
        self.access_times[key] = datetime.now()
        self.access_counts[key] = self.access_counts.get(key, 0) + 1

        return self.cache[key]

    def set(self, key: str, value: Any):
        """Define valor no cache"""
        # Remove itens se cache estiver cheio
        if len(self.cache) >= self.max_size:
            self._evict_least_used()

        self.cache[key] = value
        self.access_times[key] = datetime.now()
        self.access_counts[key] = 1

    def _evict_least_used(self):
        """Remove item menos usado"""
        if not self.cache:
            return

        # Calcula score de uso (baseado em frequência e recência)
        now = datetime.now()
        scores = {}

        for key in self.cache.keys():
            recency = (now - self.access_times[key]).seconds
            frequency = self.access_counts.get(key, 1)
            scores[key] = frequency / (1 + recency)  # Score baseado em frequência/recência

        # Remove item com menor score
        least_used_key = min(scores.keys(), key=lambda k: scores[k])
        self._remove_key(least_used_key)

    def _remove_key(self, key: str):
        """Remove chave do cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
        if key in self.access_counts:
            del self.access_counts[key]

    def predict_next_access(self, key: str) -> float:
        """Prediz probabilidade de próximo acesso"""
        if key not in self.access_counts:
            return 0.0

        # Modelo simples baseado em padrões de acesso
        frequency = self.access_counts[key]
        recency = (datetime.now() - self.access_times[key]).seconds

        # Score de predição (quanto maior, mais provável de ser acessado)
        return frequency / (1 + recency * 0.1)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": self._calculate_hit_rate(),
            "avg_access_frequency": np.mean(list(self.access_counts.values())) if self.access_counts else 0,
            "most_accessed": max(self.access_counts.items(), key=lambda x: x[1])[0] if self.access_counts else None,
        }

    def _calculate_hit_rate(self) -> float:
        """Calcula taxa de acerto do cache"""
        total_accesses = sum(self.access_counts.values())
        return len(self.cache) / total_accesses if total_accesses > 0 else 0.0


class LoadBalancer:
    """Sistema de balanceamento de carga inteligente"""

    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.workers: List[Dict[str, Any]] = []
        self.task_queue = asyncio.Queue()
        self.worker_stats = {}

        # Inicializa workers
        for i in range(max_workers):
            worker = {
                "id": i,
                "busy": False,
                "current_task": None,
                "completed_tasks": 0,
                "total_time": 0.0,
                "efficiency": 1.0,
            }
            self.workers.append(worker)
            self.worker_stats[i] = []

    async def submit_task(self, task: Callable, *args, **kwargs) -> Any:
        """Submete tarefa para execução"""
        # Encontra worker menos ocupado
        available_workers = [w for w in self.workers if not w["busy"]]

        if not available_workers:
            # Todos ocupados, aguarda worker disponível
            while not available_workers:
                await asyncio.sleep(0.01)
                available_workers = [w for w in self.workers if not w["busy"]]

        # Seleciona worker com melhor eficiência
        worker = min(available_workers, key=lambda w: w["efficiency"])

        # Executa tarefa
        start_time = time.time()
        worker["busy"] = True
        worker["current_task"] = task.__name__

        try:
            if asyncio.iscoroutinefunction(task):
                result = await task(*args, **kwargs)
            else:
                result = task(*args, **kwargs)

            # Atualiza estatísticas
            execution_time = time.time() - start_time
            worker["completed_tasks"] += 1
            worker["total_time"] += execution_time
            worker["efficiency"] = worker["completed_tasks"] / (worker["total_time"] + 1)

            self.worker_stats[worker["id"]].append(
                {"task": task.__name__, "execution_time": execution_time, "timestamp": datetime.now()}
            )

            return result

        finally:
            worker["busy"] = False
            worker["current_task"] = None

    def get_worker_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos workers"""
        return {
            "total_workers": len(self.workers),
            "busy_workers": sum(1 for w in self.workers if w["busy"]),
            "idle_workers": sum(1 for w in self.workers if not w["busy"]),
            "total_tasks_completed": sum(w["completed_tasks"] for w in self.workers),
            "avg_efficiency": np.mean([w["efficiency"] for w in self.workers]),
            "worker_details": [
                {
                    "id": w["id"],
                    "busy": w["busy"],
                    "completed_tasks": w["completed_tasks"],
                    "efficiency": w["efficiency"],
                    "current_task": w["current_task"],
                }
                for w in self.workers
            ],
        }


class AdvancedOptimizer:
    """Sistema de otimização avançado"""

    def __init__(self):
        self.targets: List[OptimizationTarget] = []
        self.results: List[OptimizationResult] = []
        self.cache = IntelligentCache()
        self.load_balancer = LoadBalancer()
        self.running = False
        self.optimization_thread = None

        # Métricas do sistema
        self.system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_usage": 0.0,
            "active_threads": 0,
            "cache_hit_rate": 0.0,
        }

        # Algoritmos de otimização
        self.optimization_algorithms = {
            "memory_optimization": self._optimize_memory,
            "cpu_optimization": self._optimize_cpu,
            "cache_optimization": self._optimize_cache,
            "load_balancing": self._optimize_load_balancing,
            "garbage_collection": self._optimize_garbage_collection,
        }

    def add_target(self, target: OptimizationTarget):
        """Adiciona alvo de otimização"""
        self.targets.append(target)
        logger.info(f"Alvo de otimização adicionado: {target.name}")

    def start(self):
        """Inicia sistema de otimização"""
        if self.running:
            return

        self.running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()

        # Inicia monitoramento do sistema
        self._start_system_monitoring()

        logger.info("Sistema de otimização avançado iniciado")

    def stop(self):
        """Para sistema de otimização"""
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join()

        logger.info("Sistema de otimização parado")

    def _optimization_loop(self):
        """Loop principal de otimização"""
        while self.running:
            try:
                # Atualiza métricas do sistema
                self._update_system_metrics()

                # Identifica alvos que precisam de otimização
                targets_to_optimize = self._identify_optimization_targets()

                # Executa otimizações
                for target in targets_to_optimize:
                    self._execute_optimization(target)

                time.sleep(5)  # Verifica a cada 5 segundos

            except Exception as e:
                logger.error(f"Erro no loop de otimização: {e}")
                time.sleep(1)

    def _start_system_monitoring(self):
        """Inicia monitoramento do sistema"""

        def monitor():
            while self.running:
                try:
                    # CPU
                    self.system_metrics["cpu_usage"] = psutil.cpu_percent(interval=1)

                    # Memória
                    memory = psutil.virtual_memory()
                    self.system_metrics["memory_usage"] = memory.percent

                    # Disco
                    disk = psutil.disk_usage("/")
                    self.system_metrics["disk_usage"] = (disk.used / disk.total) * 100

                    # Rede
                    network = psutil.net_io_counters()
                    self.system_metrics["network_usage"] = network.bytes_sent + network.bytes_recv

                    # Threads
                    self.system_metrics["active_threads"] = threading.active_count()

                    # Cache
                    cache_stats = self.cache.get_stats()
                    self.system_metrics["cache_hit_rate"] = cache_stats["hit_rate"]

                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Erro no monitoramento: {e}")
                    time.sleep(5)

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def _update_system_metrics(self):
        """Atualiza métricas do sistema"""
        # Métricas são atualizadas pelo thread de monitoramento
        pass

    def _identify_optimization_targets(self) -> List[OptimizationTarget]:
        """Identifica alvos que precisam de otimização"""
        targets_to_optimize = []

        for target in self.targets:
            current_value = self._get_current_value(target)
            target.current_value = current_value

            # Verifica se precisa de otimização
            needs_optimization = False

            if target.optimization_type == "minimize":
                needs_optimization = current_value > target.target_value * 1.1
            elif target.optimization_type == "maximize":
                needs_optimization = current_value < target.target_value * 0.9
            elif target.optimization_type == "maintain":
                needs_optimization = abs(current_value - target.target_value) > target.target_value * 0.1

            if needs_optimization:
                targets_to_optimize.append(target)

        # Ordena por prioridade
        targets_to_optimize.sort(key=lambda t: t.priority, reverse=True)

        return targets_to_optimize

    def _get_current_value(self, target: OptimizationTarget) -> float:
        """Obtém valor atual do alvo"""
        if target.name == "cpu_usage":
            return self.system_metrics["cpu_usage"]
        elif target.name == "memory_usage":
            return self.system_metrics["memory_usage"]
        elif target.name == "cache_hit_rate":
            return self.system_metrics["cache_hit_rate"]
        elif target.name == "active_threads":
            return self.system_metrics["active_threads"]
        else:
            return 0.0

    def _execute_optimization(self, target: OptimizationTarget):
        """Executa otimização para um alvo"""
        start_time = time.time()
        before_value = target.current_value

        try:
            # Seleciona algoritmo de otimização
            algorithm = self._select_optimization_algorithm(target)

            if algorithm:
                # Executa otimização
                success = algorithm(target)

                # Calcula resultado
                after_value = self._get_current_value(target)
                improvement = self._calculate_improvement(before_value, after_value, target.optimization_type)

                # Registra resultado
                result = OptimizationResult(
                    target_name=target.name,
                    before_value=before_value,
                    after_value=after_value,
                    improvement=improvement,
                    method_used=algorithm.__name__,
                    execution_time=time.time() - start_time,
                    success=success,
                    timestamp=datetime.now(),
                )

                self.results.append(result)

                if success:
                    logger.info(
                        f"Otimização {target.name}: {before_value:.2f} -> {after_value:.2f} "
                        f"(melhoria: {improvement:.2f}%)"
                    )
                else:
                    logger.warning(f"Falha na otimização de {target.name}")

        except Exception as e:
            logger.error(f"Erro na otimização de {target.name}: {e}")

    def _select_optimization_algorithm(self, target: OptimizationTarget) -> Optional[Callable]:
        """Seleciona algoritmo de otimização baseado no alvo"""
        if target.name == "memory_usage":
            return self.optimization_algorithms["memory_optimization"]
        elif target.name == "cpu_usage":
            return self.optimization_algorithms["cpu_optimization"]
        elif target.name == "cache_hit_rate":
            return self.optimization_algorithms["cache_optimization"]
        elif target.name == "active_threads":
            return self.optimization_algorithms["load_balancing"]
        else:
            return None

    def _calculate_improvement(self, before: float, after: float, optimization_type: str) -> float:
        """Calcula percentual de melhoria"""
        if before == 0:
            return 0.0

        if optimization_type == "minimize":
            return ((before - after) / before) * 100
        elif optimization_type == "maximize":
            return ((after - before) / before) * 100
        else:  # maintain
            return -abs((after - before) / before) * 100

    def _optimize_memory(self, target: OptimizationTarget) -> bool:
        """Otimiza uso de memória"""
        try:
            # Garbage collection
            gc.collect()

            # Limpa cache antigo
            self.cache._evict_least_used()

            # Limpa referências fracas
            self._cleanup_weak_references()

            return True
        except Exception as e:
            logger.error(f"Erro na otimização de memória: {e}")
            return False

    def _optimize_cpu(self, target: OptimizationTarget) -> bool:
        """Otimiza uso de CPU"""
        try:
            # Ajusta número de workers baseado na carga
            if self.system_metrics["cpu_usage"] > 80:
                # Reduz workers se CPU alta
                self.load_balancer.max_workers = max(2, self.load_balancer.max_workers - 1)
            elif self.system_metrics["cpu_usage"] < 30:
                # Aumenta workers se CPU baixa
                self.load_balancer.max_workers = min(16, self.load_balancer.max_workers + 1)

            return True
        except Exception as e:
            logger.error(f"Erro na otimização de CPU: {e}")
            return False

    def _optimize_cache(self, target: OptimizationTarget) -> bool:
        """Otimiza cache"""
        try:
            # Ajusta TTL baseado na taxa de acerto
            if self.system_metrics["cache_hit_rate"] < 0.7:
                # Aumenta TTL se taxa de acerto baixa
                self.cache.ttl = min(7200, self.cache.ttl * 1.2)
            elif self.system_metrics["cache_hit_rate"] > 0.9:
                # Reduz TTL se taxa de acerto alta
                self.cache.ttl = max(300, self.cache.ttl * 0.9)

            return True
        except Exception as e:
            logger.error(f"Erro na otimização de cache: {e}")
            return False

    def _optimize_load_balancing(self, target: OptimizationTarget) -> bool:
        """Otimiza balanceamento de carga"""
        try:
            # Ajusta estratégia de balanceamento baseado na carga
            worker_stats = self.load_balancer.get_worker_stats()

            if worker_stats["avg_efficiency"] < 0.5:
                # Workers ineficientes, redistribui tarefas
                self._redistribute_tasks()

            return True
        except Exception as e:
            logger.error(f"Erro na otimização de load balancing: {e}")
            return False

    def _optimize_garbage_collection(self, target: OptimizationTarget) -> bool:
        """Otimiza garbage collection"""
        try:
            # Força garbage collection
            collected = gc.collect()
            logger.info(f"Garbage collection: {collected} objetos coletados")
            return True
        except Exception as e:
            logger.error(f"Erro na otimização de garbage collection: {e}")
            return False

    def _cleanup_weak_references(self):
        """Limpa referências fracas"""
        # Implementação simplificada
        pass

    def _redistribute_tasks(self):
        """Redistribui tarefas entre workers"""
        # Implementação simplificada
        pass

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de otimização"""
        recent_results = [r for r in self.results if (datetime.now() - r.timestamp).seconds < 3600]

        return {
            "total_targets": len(self.targets),
            "total_optimizations": len(self.results),
            "recent_optimizations": len(recent_results),
            "success_rate": sum(1 for r in recent_results if r.success) / len(recent_results) if recent_results else 0,
            "avg_improvement": np.mean([r.improvement for r in recent_results]) if recent_results else 0,
            "system_metrics": self.system_metrics.copy(),
            "cache_stats": self.cache.get_stats(),
            "load_balancer_stats": self.load_balancer.get_worker_stats(),
        }

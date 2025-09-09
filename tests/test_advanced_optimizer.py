"""
Testes para o sistema de otimização avançado.
"""

import unittest
import time
from unittest.mock import patch

# Adiciona src ao path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))  # noqa: E402

from src.optimization.advanced_optimizer import (  # noqa: E402
    AdvancedOptimizer,
    OptimizationTarget,
    OptimizationResult,
    IntelligentCache,
    LoadBalancer,
)


class TestIntelligentCache(unittest.TestCase):
    """Testes para IntelligentCache"""

    def setUp(self):
        self.cache = IntelligentCache(max_size=100, ttl=60)

    def test_basic_operations(self):
        """Testa operações básicas do cache"""
        # Testa set e get
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")

        # Testa chave inexistente
        self.assertIsNone(self.cache.get("nonexistent"))

    def test_ttl_expiration(self):
        """Testa expiração por TTL"""
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")

        # Simula expiração
        self.cache.access_times["key1"] = time.time() - 100  # 100 segundos atrás
        self.assertIsNone(self.cache.get("key1"))

    def test_capacity_limit(self):
        """Testa limite de capacidade"""
        # Adiciona mais itens que a capacidade
        for i in range(150):
            self.cache.set(f"key{i}", f"value{i}")

        # Verifica se não excede a capacidade
        self.assertLessEqual(len(self.cache), 100)

    def test_access_tracking(self):
        """Testa rastreamento de acesso"""
        self.cache.set("key1", "value1")

        # Acessa várias vezes
        for _ in range(5):
            self.cache.get("key1")

        self.assertEqual(self.cache.access_counts["key1"], 6)  # 1 set + 5 gets

    def test_prediction(self):
        """Testa predição de próximo acesso"""
        self.cache.set("key1", "value1")

        # Acessa algumas vezes
        for _ in range(3):
            self.cache.get("key1")

        prediction = self.cache.predict_next_access("key1")
        self.assertGreater(prediction, 0)

        # Chave não acessada deve ter predição baixa
        prediction2 = self.cache.predict_next_access("nonexistent")
        self.assertEqual(prediction2, 0.0)

    def test_stats(self):
        """Testa estatísticas do cache"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")

        stats = self.cache.get_stats()

        self.assertIn("size", stats)
        self.assertIn("max_size", stats)
        self.assertIn("hit_rate", stats)
        self.assertIn("avg_access_frequency", stats)

        self.assertEqual(stats["size"], 2)
        self.assertEqual(stats["max_size"], 100)


class TestLoadBalancer(unittest.TestCase):
    """Testes para LoadBalancer"""

    def setUp(self):
        self.load_balancer = LoadBalancer(max_workers=4)

    def test_initialization(self):
        """Testa inicialização do load balancer"""
        self.assertEqual(len(self.load_balancer.workers), 4)

        for worker in self.load_balancer.workers:
            self.assertFalse(worker["busy"])
            self.assertEqual(worker["completed_tasks"], 0)
            self.assertEqual(worker["efficiency"], 1.0)

    def test_worker_stats(self):
        """Testa estatísticas dos workers"""
        stats = self.load_balancer.get_worker_stats()

        self.assertIn("total_workers", stats)
        self.assertIn("busy_workers", stats)
        self.assertIn("idle_workers", stats)
        self.assertIn("total_tasks_completed", stats)
        self.assertIn("avg_efficiency", stats)
        self.assertIn("worker_details", stats)

        self.assertEqual(stats["total_workers"], 4)
        self.assertEqual(stats["busy_workers"], 0)
        self.assertEqual(stats["idle_workers"], 4)

    def test_async_task_execution(self):
        """Testa execução assíncrona de tarefas"""
        import asyncio

        async def test_task():
            await asyncio.sleep(0.1)
            return "task_result"

        # Mock do asyncio para teste
        with patch("asyncio.sleep"):
            result = asyncio.run(self.load_balancer.submit_task(test_task))
            self.assertEqual(result, "task_result")

    def test_sync_task_execution(self):
        """Testa execução síncrona de tarefas"""
        import asyncio

        def test_task():
            return "sync_result"

        result = asyncio.run(self.load_balancer.submit_task(test_task))
        self.assertEqual(result, "sync_result")


class TestOptimizationTarget(unittest.TestCase):
    """Testes para OptimizationTarget"""

    def test_initialization(self):
        """Testa inicialização do alvo de otimização"""
        target = OptimizationTarget(
            name="test_target",
            current_value=50.0,
            target_value=30.0,
            priority=5,
            optimization_type="minimize",
        )

        self.assertEqual(target.name, "test_target")
        self.assertEqual(target.current_value, 50.0)
        self.assertEqual(target.target_value, 30.0)
        self.assertEqual(target.priority, 5)
        self.assertEqual(target.optimization_type, "minimize")
        self.assertEqual(target.weight, 1.0)  # valor padrão


class TestOptimizationResult(unittest.TestCase):
    """Testes para OptimizationResult"""

    def test_initialization(self):
        """Testa inicialização do resultado de otimização"""
        result = OptimizationResult(
            target_name="test_target",
            before_value=50.0,
            after_value=30.0,
            improvement=40.0,
            method_used="test_method",
            execution_time=1.5,
            success=True,
            timestamp=time.time(),
        )

        self.assertEqual(result.target_name, "test_target")
        self.assertEqual(result.before_value, 50.0)
        self.assertEqual(result.after_value, 30.0)
        self.assertEqual(result.improvement, 40.0)
        self.assertEqual(result.method_used, "test_method")
        self.assertEqual(result.execution_time, 1.5)
        self.assertTrue(result.success)


class TestAdvancedOptimizer(unittest.TestCase):
    """Testes para AdvancedOptimizer"""

    def setUp(self):
        self.optimizer = AdvancedOptimizer()

    def test_initialization(self):
        """Testa inicialização do otimizador"""
        self.assertEqual(len(self.optimizer.targets), 0)
        self.assertEqual(len(self.optimizer.results), 0)
        self.assertFalse(self.optimizer.running)
        self.assertIsNone(self.optimizer.optimization_thread)

    def test_add_target(self):
        """Testa adição de alvo de otimização"""
        target = OptimizationTarget(
            name="cpu_usage",
            current_value=80.0,
            target_value=50.0,
            priority=8,
            optimization_type="minimize",
        )

        self.optimizer.add_target(target)
        self.assertEqual(len(self.optimizer.targets), 1)
        self.assertEqual(self.optimizer.targets[0].name, "cpu_usage")

    def test_start_stop(self):
        """Testa início e parada do otimizador"""
        # Inicia
        self.optimizer.start()
        self.assertTrue(self.optimizer.running)
        self.assertIsNotNone(self.optimizer.optimization_thread)

        # Para
        self.optimizer.stop()
        self.assertFalse(self.optimizer.running)

    def test_identify_optimization_targets(self):
        """Testa identificação de alvos que precisam de otimização"""
        # Adiciona alvo que precisa de otimização
        target = OptimizationTarget(
            name="cpu_usage",
            current_value=80.0,
            target_value=50.0,
            priority=8,
            optimization_type="minimize",
        )
        self.optimizer.add_target(target)

        # Mock do _get_current_value
        with patch.object(self.optimizer, "_get_current_value", return_value=80.0):
            targets = self.optimizer._identify_optimization_targets()
            self.assertEqual(len(targets), 1)
            self.assertEqual(targets[0].name, "cpu_usage")

    def test_get_current_value(self):
        """Testa obtenção de valor atual"""
        target = OptimizationTarget(
            name="cpu_usage",
            current_value=0.0,
            target_value=50.0,
            priority=8,
            optimization_type="minimize",
        )

        # Mock das métricas do sistema
        self.optimizer.system_metrics["cpu_usage"] = 75.0

        value = self.optimizer._get_current_value(target)
        self.assertEqual(value, 75.0)

    def test_calculate_improvement(self):
        """Testa cálculo de melhoria"""
        # Testa minimização
        improvement = self.optimizer._calculate_improvement(100.0, 80.0, "minimize")
        self.assertEqual(improvement, 20.0)  # 20% de melhoria

        # Testa maximização
        improvement = self.optimizer._calculate_improvement(50.0, 80.0, "maximize")
        self.assertEqual(improvement, 60.0)  # 60% de melhoria

        # Testa manutenção
        improvement = self.optimizer._calculate_improvement(50.0, 60.0, "maintain")
        self.assertLess(improvement, 0)  # Piora (negativo)

    def test_optimization_algorithms(self):
        """Testa algoritmos de otimização"""
        target = OptimizationTarget(
            name="memory_usage",
            current_value=80.0,
            target_value=50.0,
            priority=8,
            optimization_type="minimize",
        )

        # Testa otimização de memória
        result = self.optimizer._optimize_memory(target)
        self.assertTrue(result)

        # Testa otimização de CPU
        result = self.optimizer._optimize_cpu(target)
        self.assertTrue(result)

        # Testa otimização de cache
        result = self.optimizer._optimize_cache(target)
        self.assertTrue(result)

    def test_get_optimization_stats(self):
        """Testa obtenção de estatísticas de otimização"""
        # Adiciona alguns resultados
        result1 = OptimizationResult(
            target_name="test1",
            before_value=100.0,
            after_value=80.0,
            improvement=20.0,
            method_used="test_method",
            execution_time=1.0,
            success=True,
            timestamp=time.time(),
        )
        self.optimizer.results.append(result1)

        stats = self.optimizer.get_optimization_stats()

        self.assertIn("total_targets", stats)
        self.assertIn("total_optimizations", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("avg_improvement", stats)
        self.assertIn("system_metrics", stats)
        self.assertIn("cache_stats", stats)
        self.assertIn("load_balancer_stats", stats)

        self.assertEqual(stats["total_optimizations"], 1)
        self.assertEqual(stats["success_rate"], 1.0)
        self.assertEqual(stats["avg_improvement"], 20.0)


class TestOptimizerIntegration(unittest.TestCase):
    """Testes de integração para o otimizador"""

    def test_full_optimization_cycle(self):
        """Testa ciclo completo de otimização"""
        optimizer = AdvancedOptimizer()

        # Adiciona alvos
        cpu_target = OptimizationTarget(
            name="cpu_usage",
            current_value=80.0,
            target_value=50.0,
            priority=8,
            optimization_type="minimize",
        )
        optimizer.add_target(cpu_target)

        memory_target = OptimizationTarget(
            name="memory_usage",
            current_value=70.0,
            target_value=40.0,
            priority=7,
            optimization_type="minimize",
        )
        optimizer.add_target(memory_target)

        # Inicia otimizador
        optimizer.start()

        # Aguarda um pouco para processamento
        time.sleep(2)

        # Para otimizador
        optimizer.stop()

        # Verifica se houve processamento
        self.assertGreater(len(optimizer.results), 0)

        # Verifica estatísticas
        stats = optimizer.get_optimization_stats()
        self.assertIn("total_targets", stats)
        self.assertIn("total_optimizations", stats)


if __name__ == "__main__":
    # Configura logging para testes
    import logging

    logging.basicConfig(level=logging.WARNING)

    # Executa testes
    unittest.main(verbosity=2)

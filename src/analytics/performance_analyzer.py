"""
Analisador de Performance para Simulação de Cidade Inteligente
Versão 1.1 - Métricas avançadas e análise de eficiência
"""

import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import json
import time
from datetime import datetime


@dataclass
class PerformanceMetric:
    """Estrutura para métricas de performance"""

    name: str
    value: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentPerformance:
    """Performance de um agente específico"""

    agent_id: str
    agent_type: str
    total_actions: int
    avg_response_time: float
    success_rate: float
    energy_efficiency: float
    collaboration_score: float


class PerformanceAnalyzer:
    """Analisador de performance da simulação"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics_history = defaultdict(lambda: deque(maxlen=window_size))
        self.agent_metrics = defaultdict(list)
        self.interaction_metrics = defaultdict(list)
        self.system_metrics = defaultdict(list)
        self.start_time = None
        self.performance_summary = {}

    def start_monitoring(self):
        """Inicia o monitoramento de performance"""
        self.start_time = time.time()
        self.log_metric(
            "simulation_start", 0, {"timestamp": datetime.now().isoformat()}
        )

    def stop_monitoring(self):
        """Para o monitoramento e gera relatório final"""
        if self.start_time:
            total_duration = time.time() - self.start_time
            self.log_metric("simulation_duration", total_duration)
            self.generate_performance_report()

    def log_metric(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Registra uma métrica"""
        metric = PerformanceMetric(
            name=name, value=value, timestamp=datetime.now(), metadata=metadata
        )
        self.metrics_history[name].append(metric)

    def log_agent_action(
        self,
        agent_id: str,
        agent_type: str,
        action: str,
        duration: float,
        success: bool,
    ):
        """Registra ação de agente"""
        self.agent_metrics[agent_id].append(
            {
                "timestamp": datetime.now(),
                "agent_type": agent_type,
                "action": action,
                "duration": duration,
                "success": success,
            }
        )

        # Métricas específicas
        self.log_metric(f"agent_{agent_id}_action_duration", duration)
        self.log_metric(f"agent_{agent_id}_success_rate", 1.0 if success else 0.0)

    def log_interaction(
        self,
        agent_from: str,
        agent_to: str,
        interaction_type: str,
        duration: float,
        success: bool,
        data_transferred: int = 0,
    ):
        """Registra interação entre agentes"""
        self.interaction_metrics[f"{agent_from}_{agent_to}"].append(
            {
                "timestamp": datetime.now(),
                "interaction_type": interaction_type,
                "duration": duration,
                "success": success,
                "data_transferred": data_transferred,
            }
        )

        # Métricas de rede
        self.log_metric("interaction_duration", duration)
        self.log_metric("data_transferred", data_transferred)
        self.log_metric("interaction_success_rate", 1.0 if success else 0.0)

    def log_system_metric(
        self, metric_name: str, value: float, component: str = "system"
    ):
        """Registra métrica do sistema"""
        self.system_metrics[component].append(
            {"timestamp": datetime.now(), "metric_name": metric_name, "value": value}
        )
        self.log_metric(f"{component}_{metric_name}", value)

    def calculate_agent_performance(self, agent_id: str) -> AgentPerformance:
        """Calcula performance de um agente específico"""
        if agent_id not in self.agent_metrics:
            return AgentPerformance(
                agent_id=agent_id,
                agent_type="unknown",
                total_actions=0,
                avg_response_time=0.0,
                success_rate=0.0,
                energy_efficiency=0.0,
                collaboration_score=0.0,
            )

        actions = self.agent_metrics[agent_id]
        if not actions:
            return AgentPerformance(
                agent_id=agent_id,
                agent_type="unknown",
                total_actions=0,
                avg_response_time=0.0,
                success_rate=0.0,
                energy_efficiency=0.0,
                collaboration_score=0.0,
            )

        total_actions = len(actions)
        avg_response_time = statistics.mean([a["duration"] for a in actions])
        success_rate = sum(1 for a in actions if a["success"]) / total_actions

        # Calcular eficiência energética (baseado em duração e sucesso)
        energy_efficiency = success_rate / (avg_response_time + 0.1)

        # Calcular score de colaboração (baseado em interações)
        collaboration_count = len(
            [k for k in self.interaction_metrics.keys() if agent_id in k]
        )
        collaboration_score = min(collaboration_count / 10.0, 1.0)

        return AgentPerformance(
            agent_id=agent_id,
            agent_type=actions[0]["agent_type"],
            total_actions=total_actions,
            avg_response_time=avg_response_time,
            success_rate=success_rate,
            energy_efficiency=energy_efficiency,
            collaboration_score=collaboration_score,
        )

    def get_system_throughput(self) -> float:
        """Calcula throughput do sistema (ações por segundo)"""
        if not self.start_time:
            return 0.0

        total_duration = time.time() - self.start_time
        total_actions = sum(len(actions) for actions in self.agent_metrics.values())
        return total_actions / total_duration if total_duration > 0 else 0.0

    def get_network_efficiency(self) -> Dict[str, float]:
        """Calcula eficiência da rede de interações"""
        if not self.interaction_metrics:
            return {"efficiency": 0.0, "latency": 0.0, "throughput": 0.0}

        all_interactions = []
        for interactions in self.interaction_metrics.values():
            all_interactions.extend(interactions)

        if not all_interactions:
            return {"efficiency": 0.0, "latency": 0.0, "throughput": 0.0}

        avg_latency = statistics.mean([i["duration"] for i in all_interactions])
        success_rate = sum(1 for i in all_interactions if i["success"]) / len(
            all_interactions
        )
        total_data = sum(i["data_transferred"] for i in all_interactions)

        # Throughput em dados por segundo
        if self.start_time:
            duration = time.time() - self.start_time
            throughput = total_data / duration if duration > 0 else 0.0
        else:
            throughput = 0.0

        return {
            "efficiency": success_rate,
            "latency": avg_latency,
            "throughput": throughput,
        }

    def get_resource_utilization(self) -> Dict[str, float]:
        """Calcula utilização de recursos"""
        utilization = {}

        # CPU (baseado em tempo de processamento)
        total_processing_time = sum(
            sum(a["duration"] for a in actions)
            for actions in self.agent_metrics.values()
        )

        if self.start_time:
            total_time = time.time() - self.start_time
            utilization["cpu"] = min(total_processing_time / total_time, 1.0)
        else:
            utilization["cpu"] = 0.0

        # Memória (baseado em número de agentes e interações)
        total_agents = len(self.agent_metrics)
        total_interactions = sum(
            len(interactions) for interactions in self.interaction_metrics.values()
        )
        utilization["memory"] = min((total_agents + total_interactions) / 1000.0, 1.0)

        # Rede (baseado em transferência de dados)
        total_data = sum(
            sum(i["data_transferred"] for i in interactions)
            for interactions in self.interaction_metrics.values()
        )
        utilization["network"] = min(total_data / 1000000.0, 1.0)  # Normalizado para MB

        return utilization

    def generate_performance_report(self) -> Dict[str, Any]:
        """Gera relatório completo de performance"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "simulation_duration": (
                time.time() - self.start_time if self.start_time else 0
            ),
            "system_metrics": {
                "throughput": self.get_system_throughput(),
                "network_efficiency": self.get_network_efficiency(),
                "resource_utilization": self.get_resource_utilization(),
            },
            "agent_performance": {},
            "top_metrics": {},
            "recommendations": [],
        }

        # Performance dos agentes
        for agent_id in self.agent_metrics.keys():
            report["agent_performance"][agent_id] = self.calculate_agent_performance(
                agent_id
            ).__dict__

        # Top métricas
        for metric_name, metrics in self.metrics_history.items():
            if metrics:
                values = [m.value for m in metrics]
                report["top_metrics"][metric_name] = {
                    "avg": statistics.mean(values),
                    "max": max(values),
                    "min": min(values),
                    "count": len(values),
                }

        # Recomendações
        recommendations = self._generate_recommendations(report)
        report["recommendations"] = recommendations

        self.performance_summary = report
        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise de performance"""
        recommendations = []

        # Análise de throughput
        throughput = report["system_metrics"]["throughput"]
        if throughput < 1.0:
            recommendations.append(
                "Considerar otimização de algoritmos - throughput baixo"
            )
        elif throughput > 10.0:
            recommendations.append(
                "Sistema com alta performance - considerar aumento de complexidade"
            )

        # Análise de eficiência de rede
        network_eff = report["system_metrics"]["network_efficiency"]["efficiency"]
        if network_eff < 0.7:
            recommendations.append("Melhorar protocolos de comunicação entre agentes")

        # Análise de utilização de recursos
        cpu_util = report["system_metrics"]["resource_utilization"]["cpu"]
        if cpu_util > 0.8:
            recommendations.append(
                "Alta utilização de CPU - considerar distribuição de carga"
            )

        # Análise de performance dos agentes
        agent_perfs = report["agent_performance"]
        low_performers = [
            agent_id
            for agent_id, perf in agent_perfs.items()
            if perf["success_rate"] < 0.5
        ]
        if low_performers:
            recommendations.append(
                f"Agentes com baixa performance: {', '.join(low_performers)}"
            )

        return recommendations

    def export_metrics(self, filename: str):
        """Exporta métricas para arquivo JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.performance_summary, f, indent=2, default=str)

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Retorna métricas em tempo real"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_agents": len(self.agent_metrics),
            "total_interactions": sum(
                len(interactions) for interactions in self.interaction_metrics.values()
            ),
            "system_throughput": self.get_system_throughput(),
            "network_efficiency": self.get_network_efficiency(),
            "resource_utilization": self.get_resource_utilization(),
        }

"""
Sistema de métricas e coleta de dados de performance.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import statistics


class MetricType(Enum):
    """Tipos de métricas."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricUnit(Enum):
    """Unidades de métricas."""
    NONE = ""
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    PERCENT = "percent"
    COUNT = "count"
    RATE = "rate"


@dataclass
class MetricLabel:
    """Label de métrica."""
    name: str
    value: str


@dataclass
class MetricValue:
    """Valor de métrica com timestamp."""
    value: float
    timestamp: datetime
    labels: List[MetricLabel] = field(default_factory=list)


@dataclass
class Metric:
    """Definição de métrica."""
    name: str
    description: str
    metric_type: MetricType
    unit: MetricUnit
    labels: List[str] = field(default_factory=list)
    values: List[MetricValue] = field(default_factory=list)
    
    def add_value(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Adiciona valor à métrica."""
        metric_labels = []
        if labels:
            for name, val in labels.items():
                metric_labels.append(MetricLabel(name, val))
        
        self.values.append(MetricValue(
            value=value,
            timestamp=datetime.now(),
            labels=metric_labels
        ))
        
        # Mantém apenas últimos 1000 valores
        if len(self.values) > 1000:
            self.values = self.values[-1000:]


class Counter:
    """Métrica contador."""
    
    def __init__(self, name: str, description: str, labels: List[str] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._value = 0
        self._lock = threading.Lock()
    
    def inc(self, amount: float = 1, labels: Optional[Dict[str, str]] = None):
        """Incrementa contador."""
        with self._lock:
            self._value += amount
    
    def get_value(self) -> float:
        """Retorna valor atual."""
        with self._lock:
            return self._value
    
    def reset(self):
        """Reseta contador."""
        with self._lock:
            self._value = 0


class Gauge:
    """Métrica gauge."""
    
    def __init__(self, name: str, description: str, labels: List[str] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._value = 0
        self._lock = threading.Lock()
    
    def set(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Define valor do gauge."""
        with self._lock:
            self._value = value
    
    def inc(self, amount: float = 1, labels: Optional[Dict[str, str]] = None):
        """Incrementa gauge."""
        with self._lock:
            self._value += amount
    
    def dec(self, amount: float = 1, labels: Optional[Dict[str, str]] = None):
        """Decrementa gauge."""
        with self._lock:
            self._value -= amount
    
    def get_value(self) -> float:
        """Retorna valor atual."""
        with self._lock:
            return self._value


class Histogram:
    """Métrica histograma."""
    
    def __init__(self, name: str, description: str, buckets: List[float] = None):
        self.name = name
        self.description = description
        self.buckets = buckets or [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
        self._values = deque(maxlen=10000)  # Mantém últimos 10k valores
        self._lock = threading.Lock()
        self._count = 0
        self._sum = 0.0
    
    def observe(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Observa valor no histograma."""
        with self._lock:
            self._values.append(value)
            self._count += 1
            self._sum += value
    
    def get_stats(self) -> Dict[str, float]:
        """Retorna estatísticas do histograma."""
        with self._lock:
            if not self._values:
                return {
                    "count": 0,
                    "sum": 0.0,
                    "mean": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "p50": 0.0,
                    "p95": 0.0,
                    "p99": 0.0
                }
            
            values = list(self._values)
            return {
                "count": self._count,
                "sum": self._sum,
                "mean": self._sum / self._count,
                "min": min(values),
                "max": max(values),
                "p50": self._percentile(values, 50),
                "p95": self._percentile(values, 95),
                "p99": self._percentile(values, 99)
            }
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calcula percentil."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]


class Summary:
    """Métrica resumo."""
    
    def __init__(self, name: str, description: str, 
                 quantiles: List[float] = None, max_age: int = 600):
        self.name = name
        self.description = description
        self.quantiles = quantiles or [0.5, 0.9, 0.95, 0.99]
        self.max_age = max_age  # segundos
        self._values = deque(maxlen=10000)
        self._lock = threading.Lock()
        self._count = 0
        self._sum = 0.0
    
    def observe(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Observa valor no resumo."""
        with self._lock:
            now = time.time()
            self._values.append((value, now))
            self._count += 1
            self._sum += value
    
    def get_stats(self) -> Dict[str, float]:
        """Retorna estatísticas do resumo."""
        with self._lock:
            if not self._values:
                return {"count": 0, "sum": 0.0}
            
            # Remove valores antigos
            cutoff = time.time() - self.max_age
            recent_values = [(v, t) for v, t in self._values if t > cutoff]
            
            if not recent_values:
                return {"count": 0, "sum": 0.0}
            
            values = [v for v, t in recent_values]
            stats = {
                "count": len(values),
                "sum": sum(values)
            }
            
            # Calcula quantis
            for q in self.quantiles:
                stats[f"quantile_{q}"] = self._quantile(values, q)
            
            return stats
    
    def _quantile(self, values: List[float], quantile: float) -> float:
        """Calcula quantil."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = quantile * (len(sorted_values) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_values) - 1)
        
        if lower == upper:
            return sorted_values[lower]
        
        weight = index - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


class MetricsRegistry:
    """Registro central de métricas."""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def register_counter(self, name: str, description: str, 
                        labels: List[str] = None) -> Counter:
        """Registra métrica contador."""
        with self._lock:
            if name in self._metrics:
                return self._metrics[name]
            
            counter = Counter(name, description, labels)
            self._metrics[name] = counter
            return counter
    
    def register_gauge(self, name: str, description: str,
                      labels: List[str] = None) -> Gauge:
        """Registra métrica gauge."""
        with self._lock:
            if name in self._metrics:
                return self._metrics[name]
            
            gauge = Gauge(name, description, labels)
            self._metrics[name] = gauge
            return gauge
    
    def register_histogram(self, name: str, description: str,
                          buckets: List[float] = None) -> Histogram:
        """Registra métrica histograma."""
        with self._lock:
            if name in self._metrics:
                return self._metrics[name]
            
            histogram = Histogram(name, description, buckets)
            self._metrics[name] = histogram
            return histogram
    
    def register_summary(self, name: str, description: str,
                        quantiles: List[float] = None) -> Summary:
        """Registra métrica resumo."""
        with self._lock:
            if name in self._metrics:
                return self._metrics[name]
            
            summary = Summary(name, description, quantiles)
            self._metrics[name] = summary
            return summary
    
    def get_metric(self, name: str) -> Optional[Any]:
        """Recupera métrica por nome."""
        with self._lock:
            return self._metrics.get(name)
    
    def list_metrics(self) -> List[str]:
        """Lista todas as métricas registradas."""
        with self._lock:
            return list(self._metrics.keys())
    
    def get_all_metrics_data(self) -> Dict[str, Any]:
        """Retorna dados de todas as métricas."""
        with self._lock:
            data = {}
            for name, metric in self._metrics.items():
                if isinstance(metric, Counter):
                    data[name] = {
                        "type": "counter",
                        "value": metric.get_value()
                    }
                elif isinstance(metric, Gauge):
                    data[name] = {
                        "type": "gauge",
                        "value": metric.get_value()
                    }
                elif isinstance(metric, Histogram):
                    data[name] = {
                        "type": "histogram",
                        "stats": metric.get_stats()
                    }
                elif isinstance(metric, Summary):
                    data[name] = {
                        "type": "summary",
                        "stats": metric.get_stats()
                    }
            return data


class MetricsCollector:
    """Coletor de métricas do sistema."""
    
    def __init__(self, registry: MetricsRegistry):
        self.registry = registry
        self._setup_system_metrics()
    
    def _setup_system_metrics(self):
        """Configura métricas do sistema."""
        # Métricas de performance
        self.request_duration = self.registry.register_histogram(
            "request_duration_seconds",
            "Duração das requisições em segundos",
            [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.request_count = self.registry.register_counter(
            "requests_total",
            "Total de requisições",
            ["method", "endpoint", "status"]
        )
        
        self.active_connections = self.registry.register_gauge(
            "active_connections",
            "Conexões ativas"
        )
        
        # Métricas de simulação
        self.simulation_cycles = self.registry.register_counter(
            "simulation_cycles_total",
            "Total de ciclos de simulação"
        )
        
        self.agent_count = self.registry.register_gauge(
            "agents_total",
            "Número total de agentes",
            ["type"]
        )
        
        self.agent_actions = self.registry.register_counter(
            "agent_actions_total",
            "Total de ações de agentes",
            ["agent_type", "action_type"]
        )
        
        # Métricas de sistema
        self.memory_usage = self.registry.register_gauge(
            "memory_usage_bytes",
            "Uso de memória em bytes"
        )
        
        self.cpu_usage = self.registry.register_gauge(
            "cpu_usage_percent",
            "Uso de CPU em percentual"
        )
    
    def record_request(self, method: str, endpoint: str, 
                      duration: float, status: int):
        """Registra métrica de requisição."""
        self.request_duration.observe(duration)
        self.request_count.inc(labels={
            "method": method,
            "endpoint": endpoint,
            "status": str(status)
        })
    
    def update_agent_count(self, agent_type: str, count: int):
        """Atualiza contagem de agentes."""
        self.agent_count.set(count, labels={"type": agent_type})
    
    def record_agent_action(self, agent_type: str, action_type: str):
        """Registra ação de agente."""
        self.agent_actions.inc(labels={
            "agent_type": agent_type,
            "action_type": action_type
        })
    
    def update_system_metrics(self, memory_bytes: int, cpu_percent: float):
        """Atualiza métricas do sistema."""
        self.memory_usage.set(memory_bytes)
        self.cpu_usage.set(cpu_percent)


class MetricsExporter:
    """Exportador de métricas para diferentes formatos."""
    
    def __init__(self, registry: MetricsRegistry):
        self.registry = registry
    
    def export_prometheus(self) -> str:
        """Exporta métricas no formato Prometheus."""
        lines = []
        data = self.registry.get_all_metrics_data()
        
        for name, metric_data in data.items():
            metric_type = metric_data["type"]
            
            if metric_type == "counter":
                value = metric_data["value"]
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {value}")
            
            elif metric_type == "gauge":
                value = metric_data["value"]
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {value}")
            
            elif metric_type == "histogram":
                stats = metric_data["stats"]
                lines.append(f"# TYPE {name} histogram")
                lines.append(f"{name}_count {stats['count']}")
                lines.append(f"{name}_sum {stats['sum']}")
                
                # Adiciona buckets
                for bucket in [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, float('inf')]:
                    count = sum(1 for v in [stats['p50'], stats['p95'], stats['p99']] if v <= bucket)
                    lines.append(f"{name}_bucket{{le=\"{bucket}\"}} {count}")
                lines.append(f"{name}_bucket{{le=\"+Inf\"}} {stats['count']}")
            
            elif metric_type == "summary":
                stats = metric_data["stats"]
                lines.append(f"# TYPE {name} summary")
                lines.append(f"{name}_count {stats['count']}")
                lines.append(f"{name}_sum {stats['sum']}")
                
                for key, value in stats.items():
                    if key.startswith("quantile_"):
                        quantile = key.replace("quantile_", "")
                        lines.append(f"{name}{{quantile=\"{quantile}\"}} {value}")
        
        return "\n".join(lines)
    
    def export_json(self) -> str:
        """Exporta métricas no formato JSON."""
        data = self.registry.get_all_metrics_data()
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_csv(self) -> str:
        """Exporta métricas no formato CSV."""
        lines = ["metric_name,metric_type,value,timestamp"]
        data = self.registry.get_all_metrics_data()
        timestamp = datetime.now().isoformat()
        
        for name, metric_data in data.items():
            metric_type = metric_data["type"]
            
            if metric_type in ["counter", "gauge"]:
                value = metric_data["value"]
                lines.append(f"{name},{metric_type},{value},{timestamp}")
            
            elif metric_type in ["histogram", "summary"]:
                stats = metric_data["stats"]
                for stat_name, stat_value in stats.items():
                    lines.append(f"{name}_{stat_name},{metric_type},{stat_value},{timestamp}")
        
        return "\n".join(lines)

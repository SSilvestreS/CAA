"""
Performance Monitor
Monitors and analyzes performance of the simulation engine
"""

import time
import statistics
from typing import Dict, List, Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Performance monitoring and analysis for the simulation engine
    """
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            history_size: Number of measurements to keep in history
        """
        self.history_size = history_size
        self.update_times = deque(maxlen=history_size)
        self.memory_usage = deque(maxlen=history_size)
        self.cpu_usage = deque(maxlen=history_size)
        self.agent_counts = deque(maxlen=history_size)
        
        self.start_time = time.time()
        self.total_updates = 0
        self.last_update_time = None
        
        logger.info(f"Performance monitor initialized with history size {history_size}")
    
    def record_update(self, update_time: float, memory_mb: float, cpu_percent: float, agent_count: int):
        """Record a simulation update"""
        self.update_times.append(update_time)
        self.memory_usage.append(memory_mb)
        self.cpu_usage.append(cpu_percent)
        self.agent_counts.append(agent_count)
        
        self.total_updates += 1
        self.last_update_time = time.time()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if not self.update_times:
            return {
                'updates_per_second': 0.0,
                'avg_update_time_ms': 0.0,
                'min_update_time_ms': 0.0,
                'max_update_time_ms': 0.0,
                'memory_usage_mb': 0.0,
                'cpu_usage_percent': 0.0,
                'agent_count': 0,
                'total_updates': 0,
                'uptime_seconds': 0.0,
            }
        
        current_time = time.time()
        uptime = current_time - self.start_time
        
        return {
            'updates_per_second': self._calculate_ups(),
            'avg_update_time_ms': statistics.mean(self.update_times) * 1000,
            'min_update_time_ms': min(self.update_times) * 1000,
            'max_update_time_ms': max(self.update_times) * 1000,
            'memory_usage_mb': statistics.mean(self.memory_usage),
            'cpu_usage_percent': statistics.mean(self.cpu_usage),
            'agent_count': self.agent_counts[-1] if self.agent_counts else 0,
            'total_updates': self.total_updates,
            'uptime_seconds': uptime,
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.update_times:
            return {'error': 'No performance data available'}
        
        current_metrics = self.get_current_metrics()
        
        # Calculate percentiles
        update_times_ms = [t * 1000 for t in self.update_times]
        update_times_ms.sort()
        
        p50 = self._percentile(update_times_ms, 50)
        p95 = self._percentile(update_times_ms, 95)
        p99 = self._percentile(update_times_ms, 99)
        
        # Calculate trends
        recent_updates = list(self.update_times)[-10:] if len(self.update_times) >= 10 else list(self.update_times)
        trend = self._calculate_trend(recent_updates)
        
        return {
            'current_metrics': current_metrics,
            'percentiles': {
                'p50_ms': p50,
                'p95_ms': p95,
                'p99_ms': p99,
            },
            'trends': {
                'update_time_trend': trend,
                'performance_stable': abs(trend) < 0.1,
            },
            'scalability': {
                'max_agents_tested': max(self.agent_counts) if self.agent_counts else 0,
                'avg_agents': statistics.mean(self.agent_counts) if self.agent_counts else 0,
            },
            'efficiency': {
                'updates_per_second_per_agent': current_metrics['updates_per_second'] / max(1, current_metrics['agent_count']),
                'memory_per_agent_mb': current_metrics['memory_usage_mb'] / max(1, current_metrics['agent_count']),
            }
        }
    
    def get_benchmark_results(self) -> Dict[str, Any]:
        """Get benchmark results for different agent counts"""
        if not self.agent_counts:
            return {'error': 'No benchmark data available'}
        
        # Group by agent count ranges
        benchmarks = {}
        agent_ranges = [(0, 10), (10, 50), (50, 100), (100, 500), (500, 1000), (1000, float('inf'))]
        
        for min_agents, max_agents in agent_ranges:
            range_data = [
                (update_time, agent_count) for update_time, agent_count in zip(self.update_times, self.agent_counts)
                if min_agents <= agent_count < max_agents
            ]
            
            if range_data:
                update_times = [data[0] for data in range_data]
                agent_counts = [data[1] for data in range_data]
                
                benchmarks[f'{min_agents}-{max_agents if max_agents != float("inf") else "∞"}'] = {
                    'samples': len(range_data),
                    'avg_update_time_ms': statistics.mean(update_times) * 1000,
                    'avg_agents': statistics.mean(agent_counts),
                    'ups_per_agent': (1.0 / statistics.mean(update_times)) / statistics.mean(agent_counts),
                }
        
        return benchmarks
    
    def detect_performance_issues(self) -> List[Dict[str, Any]]:
        """Detect potential performance issues"""
        issues = []
        
        if not self.update_times:
            return issues
        
        current_metrics = self.get_current_metrics()
        
        # Check for high update times
        if current_metrics['avg_update_time_ms'] > 100.0:
            issues.append({
                'type': 'high_update_time',
                'severity': 'warning',
                'message': f"Average update time is {current_metrics['avg_update_time_ms']:.1f}ms, consider optimization",
                'value': current_metrics['avg_update_time_ms'],
                'threshold': 100.0,
            })
        
        # Check for low updates per second
        if current_metrics['updates_per_second'] < 10.0:
            issues.append({
                'type': 'low_ups',
                'severity': 'warning',
                'message': f"Updates per second is {current_metrics['updates_per_second']:.1f}, performance may be degraded",
                'value': current_metrics['updates_per_second'],
                'threshold': 10.0,
            })
        
        # Check for high memory usage
        if current_metrics['memory_usage_mb'] > 1000.0:
            issues.append({
                'type': 'high_memory',
                'severity': 'warning',
                'message': f"Memory usage is {current_metrics['memory_usage_mb']:.1f}MB, consider memory optimization",
                'value': current_metrics['memory_usage_mb'],
                'threshold': 1000.0,
            })
        
        # Check for high CPU usage
        if current_metrics['cpu_usage_percent'] > 80.0:
            issues.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'message': f"CPU usage is {current_metrics['cpu_usage_percent']:.1f}%, system may be overloaded",
                'value': current_metrics['cpu_usage_percent'],
                'threshold': 80.0,
            })
        
        # Check for performance degradation
        if len(self.update_times) >= 10:
            recent_avg = statistics.mean(list(self.update_times)[-10:])
            older_avg = statistics.mean(list(self.update_times)[-20:-10]) if len(self.update_times) >= 20 else recent_avg
            
            if recent_avg > older_avg * 1.5:
                issues.append({
                    'type': 'performance_degradation',
                    'severity': 'error',
                    'message': f"Performance degraded by {((recent_avg / older_avg) - 1) * 100:.1f}%",
                    'value': recent_avg / older_avg,
                    'threshold': 1.5,
                })
        
        return issues
    
    def get_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        current_metrics = self.get_current_metrics()
        
        # Memory recommendations
        if current_metrics['memory_usage_mb'] > 500.0:
            recommendations.append("Consider reducing agent count or optimizing memory usage")
        
        # CPU recommendations
        if current_metrics['cpu_usage_percent'] > 70.0:
            recommendations.append("Consider using Rust engine for better CPU performance")
        
        # Update time recommendations
        if current_metrics['avg_update_time_ms'] > 50.0:
            recommendations.append("Consider optimizing simulation algorithms or reducing complexity")
        
        # Agent count recommendations
        if current_metrics['agent_count'] > 1000:
            recommendations.append("Consider using spatial partitioning for better performance with many agents")
        
        # General recommendations
        if current_metrics['updates_per_second'] < 20.0:
            recommendations.append("Consider using parallel processing or Rust engine for better performance")
        
        return recommendations
    
    def _calculate_ups(self) -> float:
        """Calculate updates per second"""
        if not self.update_times:
            return 0.0
        
        avg_update_time = statistics.mean(self.update_times)
        return 1.0 / avg_update_time if avg_update_time > 0 else 0.0
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int((percentile / 100.0) * len(sorted_data))
        index = min(index, len(sorted_data) - 1)
        
        return sorted_data[index]
    
    def _calculate_trend(self, data: List[float]) -> float:
        """Calculate trend of data (positive = increasing, negative = decreasing)"""
        if len(data) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(data)
        x_sum = sum(range(n))
        y_sum = sum(data)
        xy_sum = sum(i * data[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    def reset(self):
        """Reset performance monitor"""
        self.update_times.clear()
        self.memory_usage.clear()
        self.cpu_usage.clear()
        self.agent_counts.clear()
        
        self.start_time = time.time()
        self.total_updates = 0
        self.last_update_time = None
        
        logger.info("Performance monitor reset")
    
    def export_data(self) -> Dict[str, Any]:
        """Export performance data for analysis"""
        return {
            'update_times': list(self.update_times),
            'memory_usage': list(self.memory_usage),
            'cpu_usage': list(self.cpu_usage),
            'agent_counts': list(self.agent_counts),
            'total_updates': self.total_updates,
            'start_time': self.start_time,
            'last_update_time': self.last_update_time,
        }

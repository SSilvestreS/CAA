"""
Sistema de Logging Avançado para Simulação de Cidade Inteligente
Versão 1.1 - Logs estruturados e análise de performance
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from functools import wraps

class AdvancedLogger:
    """Sistema de logging avançado com métricas de performance"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._setup_loggers()
        self.performance_metrics = {}
    
    def _setup_loggers(self):
        """Configura os loggers para diferentes componentes"""
        
        # Logger principal da simulação
        self.simulation_logger = logging.getLogger('simulation')
        self.simulation_logger.setLevel(logging.INFO)
        
        # Logger de agentes
        self.agents_logger = logging.getLogger('agents')
        self.agents_logger.setLevel(logging.DEBUG)
        
        # Logger de performance
        self.performance_logger = logging.getLogger('performance')
        self.performance_logger.setLevel(logging.INFO)
        
        # Logger de eventos
        self.events_logger = logging.getLogger('events')
        self.events_logger.setLevel(logging.INFO)
        
        # Configurar handlers para cada logger
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura os handlers de logging"""
        
        # Formatter estruturado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para arquivo principal
        main_handler = logging.FileHandler(
            self.log_dir / f"simulation_{datetime.now().strftime('%Y%m%d')}.log"
        )
        main_handler.setFormatter(formatter)
        
        # Handler para performance
        perf_handler = logging.FileHandler(
            self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
        )
        perf_handler.setFormatter(formatter)
        
        # Handler para eventos
        events_handler = logging.FileHandler(
            self.log_dir / f"events_{datetime.now().strftime('%Y%m%d')}.log"
        )
        events_handler.setFormatter(formatter)
        
        # Handler para console (apenas erros)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        
        # Aplicar handlers
        self.simulation_logger.addHandler(main_handler)
        self.simulation_logger.addHandler(console_handler)
        
        self.performance_logger.addHandler(perf_handler)
        self.events_logger.addHandler(events_handler)
    
    def log_simulation_start(self, config: Dict[str, Any]):
        """Log do início da simulação"""
        self.simulation_logger.info(
            f"Simulação iniciada com configuração: {json.dumps(config, indent=2)}"
        )
    
    def log_simulation_end(self, duration: float, metrics: Dict[str, Any]):
        """Log do fim da simulação"""
        self.simulation_logger.info(
            f"Simulação finalizada em {duration:.2f}s. "
            f"Métricas finais: {json.dumps(metrics, indent=2)}"
        )
    
    def log_agent_action(self, agent_id: str, agent_type: str, action: str, 
                        data: Optional[Dict] = None):
        """Log de ação de agente"""
        log_data = {
            'agent_id': agent_id,
            'agent_type': agent_type,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.agents_logger.debug(json.dumps(log_data))
    
    def log_event(self, event_type: str, description: str, 
                  agent_id: Optional[str] = None, data: Optional[Dict] = None):
        """Log de evento da simulação"""
        log_data = {
            'event_type': event_type,
            'description': description,
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.events_logger.info(json.dumps(log_data))
    
    def log_interaction(self, agent_from: str, agent_to: str, 
                       interaction_type: str, result: str, 
                       data: Optional[Dict] = None):
        """Log de interação entre agentes"""
        log_data = {
            'agent_from': agent_from,
            'agent_to': agent_to,
            'interaction_type': interaction_type,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.agents_logger.info(json.dumps(log_data))
    
    def log_performance_metric(self, metric_name: str, value: float, 
                              metadata: Optional[Dict] = None):
        """Log de métrica de performance"""
        log_data = {
            'metric_name': metric_name,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata
        }
        self.performance_logger.info(json.dumps(log_data))
        
        # Armazenar para análise
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []
        self.performance_metrics[metric_name].append({
            'value': value,
            'timestamp': datetime.now(),
            'metadata': metadata
        })
    
    def performance_timer(self, operation_name: str):
        """Decorator para medir tempo de execução"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                
                self.log_performance_metric(
                    f"{operation_name}_duration",
                    duration,
                    {'function': func.__name__}
                )
                return result
            return wrapper
        return decorator
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas de performance"""
        summary = {}
        for metric_name, values in self.performance_metrics.items():
            if values:
                metric_values = [v['value'] for v in values]
                summary[metric_name] = {
                    'count': len(metric_values),
                    'min': min(metric_values),
                    'max': max(metric_values),
                    'avg': sum(metric_values) / len(metric_values),
                    'latest': metric_values[-1]
                }
        return summary
    
    def export_logs(self, output_file: str):
        """Exporta logs para arquivo JSON"""
        logs_data = {
            'performance_metrics': self.performance_metrics,
            'performance_summary': self.get_performance_summary(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(logs_data, f, indent=2, default=str)
    
    def clear_old_logs(self, days_to_keep: int = 7):
        """Remove logs antigos"""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
                self.simulation_logger.info(f"Log antigo removido: {log_file}")

# Instância global do logger
advanced_logger = AdvancedLogger()

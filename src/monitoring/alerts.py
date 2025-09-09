"""
Sistema de alertas e notificações baseado em métricas.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque


class AlertSeverity(Enum):
    """Níveis de severidade de alertas."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Status do alerta."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class AlertRule:
    """Regra de alerta."""

    name: str
    description: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "==", "!="
    threshold: float
    severity: AlertSeverity
    duration: int = 0  # segundos para trigger
    enabled: bool = True
    labels: Dict[str, str] = field(default_factory=dict)

    def evaluate(self, value: float) -> bool:
        """Avalia se valor atende à condição."""
        if not self.enabled:
            return False

        if self.condition == ">":
            return value > self.threshold
        elif self.condition == "<":
            return value < self.threshold
        elif self.condition == ">=":
            return value >= self.threshold
        elif self.condition == "<=":
            return value <= self.threshold
        elif self.condition == "==":
            return value == self.threshold
        elif self.condition == "!=":
            return value != self.threshold

        return False


@dataclass
class Alert:
    """Alerta ativo."""

    alert_id: str
    rule_name: str
    metric_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    value: float
    threshold: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converte alerta para dicionário."""
        return {
            "alert_id": self.alert_id,
            "rule_name": self.rule_name,
            "metric_name": self.metric_name,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "triggered_at": self.triggered_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "labels": self.labels,
        }


class AlertManager:
    """Gerenciador de alertas."""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_handlers: List[Callable] = []
        self._lock = threading.Lock()
        self._running = False
        self._evaluation_thread: Optional[threading.Thread] = None
        self._evaluation_interval = 10  # segundos
        self._metric_values: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

    def add_rule(self, rule: AlertRule) -> bool:
        """Adiciona regra de alerta."""
        with self._lock:
            if rule.name in self.rules:
                return False

            self.rules[rule.name] = rule
            return True

    def remove_rule(self, rule_name: str) -> bool:
        """Remove regra de alerta."""
        with self._lock:
            if rule_name not in self.rules:
                return False

            del self.rules[rule_name]

            # Resolve alertas ativos desta regra
            for alert_id, alert in list(self.active_alerts.items()):
                if alert.rule_name == rule_name:
                    self._resolve_alert(alert_id, "Regra removida")

            return True

    def update_metric_value(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """Atualiza valor de métrica."""
        if timestamp is None:
            timestamp = datetime.now()

        with self._lock:
            self._metric_values[metric_name].append((value, timestamp))

    def start_evaluation(self):
        """Inicia avaliação de alertas."""
        if self._running:
            return

        self._running = True
        self._evaluation_thread = threading.Thread(target=self._evaluation_loop)
        self._evaluation_thread.daemon = True
        self._evaluation_thread.start()

    def stop_evaluation(self):
        """Para avaliação de alertas."""
        self._running = False
        if self._evaluation_thread:
            self._evaluation_thread.join()

    def _evaluation_loop(self):
        """Loop de avaliação de alertas."""
        while self._running:
            try:
                self._evaluate_all_rules()
                time.sleep(self._evaluation_interval)
            except Exception as e:
                print(f"Erro na avaliação de alertas: {e}")

    def _evaluate_all_rules(self):
        """Avalia todas as regras de alerta."""
        with self._lock:
            for rule_name, rule in self.rules.items():
                if not rule.enabled:
                    continue

                # Obtém valores recentes da métrica
                values = self._metric_values.get(rule.metric_name, deque())
                if not values:
                    continue

                # Verifica se há valores suficientes para duração
                if rule.duration > 0:
                    cutoff = datetime.now() - timedelta(seconds=rule.duration)
                    recent_values = [(v, t) for v, t in values if t >= cutoff]
                    if len(recent_values) < 2:  # Precisa de pelo menos 2 valores
                        continue

                    # Verifica se todos os valores recentes atendem à condição
                    all_triggered = all(rule.evaluate(v) for v, t in recent_values)
                    if not all_triggered:
                        continue

                    current_value = recent_values[-1][0]
                else:
                    current_value = values[-1][0]
                    if not rule.evaluate(current_value):
                        continue

                # Verifica se alerta já está ativo
                existing_alert = self._find_active_alert(rule_name)
                if existing_alert:
                    continue

                # Cria novo alerta
                self._create_alert(rule, current_value)

    def _find_active_alert(self, rule_name: str) -> Optional[Alert]:
        """Encontra alerta ativo para regra."""
        for alert in self.active_alerts.values():
            if alert.rule_name == rule_name and alert.status == AlertStatus.ACTIVE:
                return alert
        return None

    def _create_alert(self, rule: AlertRule, value: float):
        """Cria novo alerta."""
        alert_id = f"{rule.name}_{int(time.time())}"

        alert = Alert(
            alert_id=alert_id,
            rule_name=rule.name,
            metric_name=rule.metric_name,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            message=f"Métrica {rule.metric_name} {rule.condition} {rule.threshold} (valor atual: {value})",
            value=value,
            threshold=rule.threshold,
            triggered_at=datetime.now(),
            labels=rule.labels.copy(),
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        # Envia notificações
        self._send_notifications(alert)

    def _resolve_alert(self, alert_id: str, reason: str = "Condição não atendida"):
        """Resolve alerta."""
        if alert_id not in self.active_alerts:
            return

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()

        del self.active_alerts[alert_id]

    def _send_notifications(self, alert: Alert):
        """Envia notificações do alerta."""
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Erro ao enviar notificação: {e}")

    def add_notification_handler(self, handler: Callable):
        """Adiciona handler de notificação."""
        self.notification_handlers.append(handler)

    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Reconhece alerta."""
        with self._lock:
            if alert_id not in self.active_alerts:
                return False

            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = user
            alert.acknowledged_at = datetime.now()

            return True

    def suppress_alert(self, alert_id: str, user: str, reason: str) -> bool:
        """Suprime alerta."""
        with self._lock:
            if alert_id not in self.active_alerts:
                return False

            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.SUPPRESSED
            alert.acknowledged_by = user
            alert.acknowledged_at = datetime.now()

            return True

    def get_active_alerts(self) -> List[Alert]:
        """Retorna alertas ativos."""
        with self._lock:
            return [alert for alert in self.active_alerts.values() if alert.status == AlertStatus.ACTIVE]

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Retorna histórico de alertas."""
        with self._lock:
            return self.alert_history[-limit:]

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Retorna alertas por severidade."""
        with self._lock:
            return [
                alert
                for alert in self.active_alerts.values()
                if alert.severity == severity and alert.status == AlertStatus.ACTIVE
            ]


class NotificationChannel:
    """Canal de notificação base."""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    def send(self, alert: Alert) -> bool:
        """Envia notificação."""
        raise NotImplementedError


class ConsoleNotificationChannel(NotificationChannel):
    """Canal de notificação para console."""

    def __init__(self):
        super().__init__("console")

    def send(self, alert: Alert) -> bool:
        """Envia notificação para console."""
        if not self.enabled:
            return False

        print(f"[{alert.severity.value.upper()}] {alert.message}")
        print(f"  Regra: {alert.rule_name}")
        print(f"  Valor: {alert.value} (limite: {alert.threshold})")
        print(f"  Timestamp: {alert.triggered_at}")
        print("-" * 50)

        return True


class FileNotificationChannel(NotificationChannel):
    """Canal de notificação para arquivo."""

    def __init__(self, filename: str = "alerts.log"):
        super().__init__("file")
        self.filename = filename

    def send(self, alert: Alert) -> bool:
        """Envia notificação para arquivo."""
        if not self.enabled:
            return False

        try:
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(f"{alert.triggered_at.isoformat()} [{alert.severity.value}] {alert.message}\n")
            return True
        except Exception as e:
            print(f"Erro ao escrever no arquivo: {e}")
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Canal de notificação para webhook."""

    def __init__(self, webhook_url: str):
        super().__init__("webhook")
        self.webhook_url = webhook_url

    def send(self, alert: Alert) -> bool:
        """Envia notificação para webhook."""
        if not self.enabled:
            return False

        try:
            import requests

            payload = {
                "text": f"🚨 Alerta: {alert.message}",
                "attachments": [
                    {
                        "color": self._get_color(alert.severity),
                        "fields": [
                            {"title": "Regra", "value": alert.rule_name, "short": True},
                            {"title": "Severidade", "value": alert.severity.value, "short": True},
                            {"title": "Valor", "value": str(alert.value), "short": True},
                            {"title": "Limite", "value": str(alert.threshold), "short": True},
                        ],
                    }
                ],
            }

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200

        except Exception as e:
            print(f"Erro ao enviar webhook: {e}")
            return False

    def _get_color(self, severity: AlertSeverity) -> str:
        """Retorna cor baseada na severidade."""
        colors = {
            AlertSeverity.INFO: "good",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.ERROR: "danger",
            AlertSeverity.CRITICAL: "#8B0000",
        }
        return colors.get(severity, "good")


class AlertDashboard:
    """Dashboard de alertas."""

    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para dashboard."""
        active_alerts = self.alert_manager.get_active_alerts()

        # Agrupa por severidade
        severity_counts = {}
        for alert in active_alerts:
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Alerta mais recente
        most_recent = None
        if active_alerts:
            most_recent = max(active_alerts, key=lambda a: a.triggered_at)

        return {
            "total_active": len(active_alerts),
            "severity_distribution": severity_counts,
            "most_recent": most_recent.to_dict() if most_recent else None,
            "alerts": [alert.to_dict() for alert in active_alerts],
        }

    def generate_summary_report(self) -> str:
        """Gera relatório resumido."""
        data = self.get_dashboard_data()

        report = """
=== RELATÓRIO DE ALERTAS ===
Total de alertas ativos: {data['total_active']}

Distribuição por severidade:
"""

        for severity, count in data["severity_distribution"].items():
            report += f"  {severity.upper()}: {count}\n"

        if data["most_recent"]:
            # alert = data["most_recent"]
            report += """
Alerta mais recente:
  Regra: {alert['rule_name']}
  Severidade: {alert['severity']}
  Mensagem: {alert['message']}
  Timestamp: {alert['triggered_at']}
"""

        return report

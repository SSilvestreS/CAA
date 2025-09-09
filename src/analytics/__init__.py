"""
Analytics Avançado
versão 1.7 - MLOps e Escalabilidade
"""

from .dashboard_manager import DashboardManager, DashboardType, WidgetType, Widget
from .report_generator import ReportGenerator
from .alert_system import AlertSystem
from .metrics_analyzer import MetricsAnalyzer

__all__ = [
    "DashboardManager",
    "DashboardType",
    "WidgetType",
    "Widget",
    "ReportGenerator",
    "AlertSystem",
    "MetricsAnalyzer",
]

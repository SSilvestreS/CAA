"""
Gerenciador de Dashboards
versão 1.7 - MLOps e Escalabilidade
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DashboardType(str, Enum):
    """Tipos de dashboard"""

    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    CUSTOM = "custom"


class WidgetType(str, Enum):
    """Tipos de widgets"""

    CHART = "chart"
    METRIC = "metric"
    TABLE = "table"
    MAP = "map"
    ALERT = "alert"
    TEXT = "text"


class RefreshInterval(str, Enum):
    """Intervalos de atualização"""

    REAL_TIME = "real_time"
    MINUTE = "minute"
    FIVE_MINUTES = "five_minutes"
    HOUR = "hour"
    DAY = "day"


@dataclass
class WidgetData:
    """Dados de um widget"""

    widget_id: str
    data: Any
    timestamp: datetime
    metadata: Dict[str, Any]


class Widget(BaseModel):
    """Widget do dashboard"""

    id: str
    title: str
    widget_type: WidgetType
    position: Dict[str, int] = Field(default_factory=dict)  # x, y, width, height
    config: Dict[str, Any] = Field(default_factory=dict)
    data_source: str = ""
    refresh_interval: RefreshInterval = RefreshInterval.MINUTE
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Dashboard(BaseModel):
    """Dashboard"""

    id: str
    name: str
    description: str = ""
    dashboard_type: DashboardType
    widgets: List[Widget] = Field(default_factory=list)
    layout: Dict[str, Any] = Field(default_factory=dict)
    refresh_interval: RefreshInterval = RefreshInterval.MINUTE
    is_public: bool = False
    created_by: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DashboardManager:
    """Gerenciador de dashboards"""

    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
        self.widget_data: Dict[str, WidgetData] = {}
        self._running = False
        self._refresh_tasks: Dict[str, asyncio.Task] = {}

    async def start(self):
        """Inicia o gerenciador"""
        self._running = True
        logger.info("Dashboard Manager iniciado")

        # Inicia refresh tasks
        asyncio.create_task(self._refresh_loop())

    async def stop(self):
        """Para o gerenciador"""
        self._running = False

        # Cancela todas as tasks
        for task in self._refresh_tasks.values():
            task.cancel()

        logger.info("Dashboard Manager parado")

    async def create_dashboard(
        self,
        name: str,
        description: str = "",
        dashboard_type: DashboardType = DashboardType.CUSTOM,
        created_by: str = "",
    ) -> Dashboard:
        """Cria um novo dashboard"""
        dashboard_id = f"dash_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        dashboard = Dashboard(
            id=dashboard_id,
            name=name,
            description=description,
            dashboard_type=dashboard_type,
            created_by=created_by,
        )

        self.dashboards[dashboard_id] = dashboard
        logger.info(f"Dashboard criado: {dashboard_id}")

        return dashboard

    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Obtém um dashboard"""
        return self.dashboards.get(dashboard_id)

    async def list_dashboards(
        self,
        dashboard_type: Optional[DashboardType] = None,
        created_by: Optional[str] = None,
    ) -> List[Dashboard]:
        """Lista dashboards com filtros"""
        filtered_dashboards = list(self.dashboards.values())

        if dashboard_type:
            filtered_dashboards = [
                d for d in filtered_dashboards if d.dashboard_type == dashboard_type
            ]

        if created_by:
            filtered_dashboards = [
                d for d in filtered_dashboards if d.created_by == created_by
            ]

        return filtered_dashboards

    async def update_dashboard(
        self, dashboard_id: str, updates: Dict[str, Any]
    ) -> Optional[Dashboard]:
        """Atualiza um dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None

        for key, value in updates.items():
            if hasattr(dashboard, key) and key not in ["id", "created_at"]:
                setattr(dashboard, key, value)

        dashboard.updated_at = datetime.now()
        logger.info(f"Dashboard atualizado: {dashboard_id}")

        return dashboard

    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Remove um dashboard"""
        if dashboard_id in self.dashboards:
            del self.dashboards[dashboard_id]
            logger.info(f"Dashboard removido: {dashboard_id}")
            return True
        return False

    async def add_widget(self, dashboard_id: str, widget: Widget) -> bool:
        """Adiciona um widget ao dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return False

        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.now()

        # Inicia refresh task para o widget
        if widget.enabled:
            await self._start_widget_refresh(dashboard_id, widget.id)

        logger.info(f"Widget adicionado: {widget.id} ao dashboard {dashboard_id}")
        return True

    async def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove um widget do dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return False

        # Remove widget
        dashboard.widgets = [w for w in dashboard.widgets if w.id != widget_id]
        dashboard.updated_at = datetime.now()

        # Para refresh task
        task_key = f"{dashboard_id}_{widget_id}"
        if task_key in self._refresh_tasks:
            self._refresh_tasks[task_key].cancel()
            del self._refresh_tasks[task_key]

        logger.info(f"Widget removido: {widget_id} do dashboard {dashboard_id}")
        return True

    async def update_widget(
        self, dashboard_id: str, widget_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Atualiza um widget"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return False

        # Encontra o widget
        for widget in dashboard.widgets:
            if widget.id == widget_id:
                for key, value in updates.items():
                    if hasattr(widget, key) and key not in ["id", "created_at"]:
                        setattr(widget, key, value)

                widget.updated_at = datetime.now()
                dashboard.updated_at = datetime.now()

                # Reinicia refresh task se necessário
                if widget.enabled:
                    await self._start_widget_refresh(dashboard_id, widget_id)

                logger.info(f"Widget atualizado: {widget_id}")
                return True

        return False

    async def get_widget_data(
        self, dashboard_id: str, widget_id: str
    ) -> Optional[WidgetData]:
        """Obtém dados de um widget"""
        data_key = f"{dashboard_id}_{widget_id}"
        return self.widget_data.get(data_key)

    async def _start_widget_refresh(self, dashboard_id: str, widget_id: str):
        """Inicia refresh task para um widget"""
        task_key = f"{dashboard_id}_{widget_id}"

        # Cancela task existente
        if task_key in self._refresh_tasks:
            self._refresh_tasks[task_key].cancel()

        # Cria nova task
        self._refresh_tasks[task_key] = asyncio.create_task(
            self._widget_refresh_loop(dashboard_id, widget_id)
        )

    async def _widget_refresh_loop(self, dashboard_id: str, widget_id: str):
        """Loop de refresh para um widget"""
        while self._running:
            try:
                dashboard = self.dashboards.get(dashboard_id)
                if not dashboard:
                    break

                widget = None
                for w in dashboard.widgets:
                    if w.id == widget_id:
                        widget = w
                        break

                if not widget or not widget.enabled:
                    break

                # Atualiza dados do widget
                await self._refresh_widget_data(dashboard_id, widget_id, widget)

                # Calcula intervalo de refresh
                refresh_seconds = self._get_refresh_interval_seconds(
                    widget.refresh_interval
                )
                await asyncio.sleep(refresh_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no refresh do widget {widget_id}: {e}")
                await asyncio.sleep(5)

    async def _refresh_widget_data(
        self, dashboard_id: str, widget_id: str, widget: Widget
    ):
        """Atualiza dados de um widget"""
        try:
            # Simula coleta de dados (implementar lógica real)
            data = await self._collect_widget_data(widget)

            widget_data = WidgetData(
                widget_id=widget_id,
                data=data,
                timestamp=datetime.now(),
                metadata={"source": widget.data_source},
            )

            data_key = f"{dashboard_id}_{widget_id}"
            self.widget_data[data_key] = widget_data

        except Exception as e:
            logger.error(f"Erro ao atualizar dados do widget {widget_id}: {e}")

    async def _collect_widget_data(self, widget: Widget) -> Any:
        """Coleta dados para um widget"""
        # Implementar lógica de coleta de dados baseada no tipo
        if widget.widget_type == WidgetType.METRIC:
            return {
                "value": np.random.randint(0, 100),
                "trend": np.random.choice(["up", "down", "stable"]),
                "change": np.random.uniform(-10, 10),
            }
        elif widget.widget_type == WidgetType.CHART:
            # Gera dados de exemplo para gráfico
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=30), end=datetime.now(), freq="D"
            )
            values = np.random.randn(len(dates)).cumsum() + 100

            return {
                "x": dates.tolist(),
                "y": values.tolist(),
                "type": "scatter",
                "mode": "lines",
            }
        elif widget.widget_type == WidgetType.TABLE:
            return {
                "columns": ["Nome", "Valor", "Status"],
                "rows": [
                    ["Item 1", np.random.randint(0, 100), "Ativo"],
                    ["Item 2", np.random.randint(0, 100), "Inativo"],
                    ["Item 3", np.random.randint(0, 100), "Ativo"],
                ],
            }
        else:
            return {"message": "Dados não disponíveis"}

    def _get_refresh_interval_seconds(self, interval: RefreshInterval) -> int:
        """Converte intervalo de refresh para segundos"""
        intervals = {
            RefreshInterval.REAL_TIME: 1,
            RefreshInterval.MINUTE: 60,
            RefreshInterval.FIVE_MINUTES: 300,
            RefreshInterval.HOUR: 3600,
            RefreshInterval.DAY: 86400,
        }
        return intervals.get(interval, 60)

    async def _refresh_loop(self):
        """Loop principal de refresh"""
        while self._running:
            try:
                # Atualiza todos os dashboards
                for dashboard in self.dashboards.values():
                    for widget in dashboard.widgets:
                        if widget.enabled:
                            await self._refresh_widget_data(
                                dashboard.id, widget.id, widget
                            )

                await asyncio.sleep(60)  # Refresh geral a cada minuto

            except Exception as e:
                logger.error(f"Erro no refresh loop: {e}")
                await asyncio.sleep(5)

    async def export_dashboard(
        self, dashboard_id: str, format: str = "json"
    ) -> Optional[Dict[str, Any]]:
        """Exporta um dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None

        if format == "json":
            return dashboard.dict()
        else:
            logger.warning(f"Formato de exportação não suportado: {format}")
            return None

    async def import_dashboard(
        self, dashboard_data: Dict[str, Any], new_name: Optional[str] = None
    ) -> Optional[Dashboard]:
        """Importa um dashboard"""
        try:
            # Cria novo dashboard
            dashboard = Dashboard(**dashboard_data)

            if new_name:
                dashboard.name = new_name

            # Gera novo ID
            dashboard.id = f"dash_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dashboard.created_at = datetime.now()
            dashboard.updated_at = datetime.now()

            self.dashboards[dashboard.id] = dashboard
            logger.info(f"Dashboard importado: {dashboard.id}")

            return dashboard

        except Exception as e:
            logger.error(f"Erro ao importar dashboard: {e}")
            return None

    async def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Obtém analytics dos dashboards"""
        total_dashboards = len(self.dashboards)
        total_widgets = sum(len(d.widgets) for d in self.dashboards.values())

        # Conta por tipo
        by_type = {}
        for dashboard in self.dashboards.values():
            dashboard_type = dashboard.dashboard_type.value
            by_type[dashboard_type] = by_type.get(dashboard_type, 0) + 1

        # Conta widgets por tipo
        widgets_by_type = {}
        for dashboard in self.dashboards.values():
            for widget in dashboard.widgets:
                widget_type = widget.widget_type.value
                widgets_by_type[widget_type] = widgets_by_type.get(widget_type, 0) + 1

        return {
            "total_dashboards": total_dashboards,
            "total_widgets": total_widgets,
            "dashboards_by_type": by_type,
            "widgets_by_type": widgets_by_type,
            "avg_widgets_per_dashboard": (
                total_widgets / total_dashboards if total_dashboards > 0 else 0
            ),
        }

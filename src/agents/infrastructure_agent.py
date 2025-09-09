"""
Agente Infraestrutura - Controla sistemas críticos da cidade.
Gerencia energia, trânsito, saneamento, saúde e outros serviços essenciais.
"""

import random
from datetime import datetime, timedelta
import numpy as np
from .base_agent import BaseAgent, AgentMessage


class InfrastructureAgent(BaseAgent):
    """
    Agente que controla sistemas de infraestrutura crítica da cidade.
    Coordena decisões em tempo real e usa simulações preditivas.
    """

    def __init__(self, name: str, infrastructure_type: str, position: tuple = (0, 0), **kwargs):
        super().__init__(name, position, **kwargs)

        # Tipo de infraestrutura
        self.infrastructure_type = infrastructure_type  # 'energy', 'transport', 'water', 'healthcare', etc.

        # Capacidade e operação
        self.capacity = random.uniform(1000, 10000)  # Capacidade total
        self.current_load = 0  # Carga atual
        self.efficiency = random.uniform(0.7, 0.95)  # Eficiência operacional
        self.maintenance_level = random.uniform(0.5, 0.9)  # Nível de manutenção

        # Recursos e custos
        self.operating_cost = random.uniform(1000, 10000)  # Custo operacional diário
        self.maintenance_cost = random.uniform(500, 5000)  # Custo de manutenção
        self.energy_consumption = random.uniform(100, 1000)  # Consumo de energia

        # Estado dos sistemas
        self.system_status = {
            "operational": True,
            "load_percentage": 0.0,
            "efficiency_rating": self.efficiency,
            "maintenance_needed": False,
            "last_maintenance": datetime.now() - timedelta(days=random.randint(1, 30)),
        }

        # Previsões e otimizações
        self.demand_forecast = []
        self.load_history = []
        self.optimization_algorithms = {
            "load_balancing": True,
            "predictive_maintenance": True,
            "energy_optimization": True,
            "capacity_planning": True,
        }

        # Alertas e emergências
        self.alerts = []
        self.emergency_protocols = {
            "overload": {"threshold": 0.9, "response": "reduce_load"},
            "failure": {"threshold": 0.1, "response": "emergency_repair"},
            "maintenance": {"threshold": 0.3, "response": "schedule_maintenance"},
        }

        # Conectividade com outros sistemas
        self.connected_systems = []
        self.dependencies = []
        self.customers = []

        # Métricas de performance
        self.uptime = 0.99  # Tempo de funcionamento
        self.service_quality = 0.8  # Qualidade do serviço
        self.customer_satisfaction = 0.7  # Satisfação dos clientes

    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toma decisões operacionais baseadas em carga, previsões e otimizações.
        """
        # Analisa situação atual
        current_situation = await self._analyze_system_status(context)

        # Identifica problemas e oportunidades
        issues = await self._identify_system_issues(current_situation)

        # Toma decisões operacionais
        decisions = []

        # Decisões de carga
        load_decisions = await self._make_load_management_decisions(current_situation, issues)
        decisions.extend(load_decisions)

        # Decisões de manutenção
        maintenance_decisions = await self._make_maintenance_decisions(current_situation, issues)
        decisions.extend(maintenance_decisions)

        # Decisões de otimização
        optimization_decisions = await self._make_optimization_decisions(current_situation)
        decisions.extend(optimization_decisions)

        # Decisões de emergência
        emergency_decisions = await self._make_emergency_decisions(issues)
        decisions.extend(emergency_decisions)

        return {
            "decisions": decisions,
            "system_status": current_situation,
            "issues_identified": issues,
            "timestamp": datetime.now(),
        }

    async def _analyze_system_status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa status atual do sistema"""
        # Calcula carga atual
        current_load = self.current_load
        load_percentage = current_load / self.capacity if self.capacity > 0 else 0

        # Calcula eficiência atual
        current_efficiency = self.efficiency * self.maintenance_level

        # Calcula demanda prevista
        predicted_demand = await self._predict_demand(context)

        # Calcula capacidade disponível
        available_capacity = self.capacity - current_load

        # Calcula custos operacionais
        operational_costs = self._calculate_operational_costs()

        return {
            "current_load": current_load,
            "load_percentage": load_percentage,
            "capacity": self.capacity,
            "available_capacity": available_capacity,
            "efficiency": current_efficiency,
            "predicted_demand": predicted_demand,
            "operational_costs": operational_costs,
            "system_health": self._calculate_system_health(),
            "maintenance_status": self._assess_maintenance_needs(),
        }

    async def _predict_demand(self, context: Dict[str, Any]) -> float:
        """Prediz demanda futura usando IA"""
        # Usa histórico de carga para previsão
        if len(self.load_history) < 5:
            return self.current_load * 1.1  # Previsão conservadora

        # Análise de tendência simples
        recent_loads = self.load_history[-5:]
        trend = np.polyfit(range(len(recent_loads)), recent_loads, 1)[0]

        # Considera fatores externos
        time_factor = self._get_time_factor()
        weather_factor = context.get("weather_impact", 1.0)
        event_factor = context.get("special_events", 1.0)

        predicted_demand = self.current_load + trend + (time_factor * 0.1)
        predicted_demand *= weather_factor * event_factor

        return max(0, min(predicted_demand, self.capacity * 1.2))

    def _get_time_factor(self) -> float:
        """Retorna fator baseado no horário"""
        current_hour = datetime.now().hour

        # Picos de demanda em horários específicos
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:  # Horários de pico
            return 1.5
        elif 22 <= current_hour or current_hour <= 6:  # Madrugada
            return 0.5
        else:
            return 1.0

    def _calculate_operational_costs(self) -> float:
        """Calcula custos operacionais atuais"""
        base_cost = self.operating_cost

        # Ajusta baseado na carga
        load_factor = self.current_load / self.capacity if self.capacity > 0 else 0
        cost_multiplier = 1 + (load_factor * 0.5)  # Custos aumentam com carga

        # Ajusta baseado na eficiência
        efficiency_factor = 1 / self.efficiency  # Menor eficiência = maior custo

        return base_cost * cost_multiplier * efficiency_factor

    def _calculate_system_health(self) -> float:
        """Calcula saúde geral do sistema"""
        factors = [self.efficiency, self.maintenance_level, self.uptime, self.service_quality]

        return np.mean(factors)

    def _assess_maintenance_needs(self) -> Dict[str, Any]:
        """Avalia necessidades de manutenção"""
        days_since_maintenance = (datetime.now() - self.system_status["last_maintenance"]).days

        maintenance_urgency = min(1.0, days_since_maintenance / 30)  # Urgência baseada em dias

        return {
            "urgency": maintenance_urgency,
            "days_since_last": days_since_maintenance,
            "recommended_action": "schedule_maintenance" if maintenance_urgency > 0.7 else "monitor",
        }

    async def _identify_system_issues(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica problemas no sistema"""
        issues = []

        # Problema de sobrecarga
        if situation["load_percentage"] > 0.9:
            issues.append({"type": "overload", "severity": situation["load_percentage"], "priority": "critical"})

        # Problema de baixa eficiência
        if situation["efficiency"] < 0.6:
            issues.append({"type": "low_efficiency", "severity": 1 - situation["efficiency"], "priority": "high"})

        # Problema de manutenção
        maintenance_status = situation["maintenance_status"]
        if maintenance_status["urgency"] > 0.8:
            issues.append(
                {"type": "maintenance_required", "severity": maintenance_status["urgency"], "priority": "high"}
            )

        # Problema de capacidade
        if situation["predicted_demand"] > situation["capacity"]:
            issues.append(
                {
                    "type": "capacity_shortage",
                    "severity": (situation["predicted_demand"] - situation["capacity"]) / situation["capacity"],
                    "priority": "medium",
                }
            )

        return issues

    async def _make_load_management_decisions(
        self, situation: Dict[str, Any], issues: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Toma decisões de gerenciamento de carga"""
        decisions = []

        # Decisão de balanceamento de carga
        if situation["load_percentage"] > 0.8:
            decisions.append(
                {
                    "action": "load_balancing",
                    "type": "distribute_load",
                    "target_load": situation["capacity"] * 0.7,
                    "expected_impact": "reduce_overload",
                }
            )

        # Decisão de aumento de capacidade
        if situation["predicted_demand"] > situation["capacity"] * 0.9:
            decisions.append(
                {
                    "action": "capacity_increase",
                    "type": "activate_backup",
                    "additional_capacity": situation["capacity"] * 0.2,
                    "cost": self.operating_cost * 0.5,
                }
            )

        # Decisão de redução de demanda
        if situation["load_percentage"] > 0.95:
            decisions.append(
                {
                    "action": "demand_reduction",
                    "type": "load_shedding",
                    "reduction_percentage": 0.1,
                    "affected_customers": int(len(self.customers) * 0.1),
                }
            )

        return decisions

    async def _make_maintenance_decisions(self, situation: Dict[str, Any], issues: List[Dict]) -> List[Dict[str, Any]]:
        """Toma decisões de manutenção"""
        decisions = []

        maintenance_issues = [issue for issue in issues if issue["type"] == "maintenance_required"]

        for issue in maintenance_issues:
            if issue["severity"] > 0.8:
                decisions.append(
                    {
                        "action": "emergency_maintenance",
                        "type": "immediate_repair",
                        "cost": self.maintenance_cost * 2,
                        "duration": 2,  # horas
                        "expected_improvement": 0.3,
                    }
                )
            elif issue["severity"] > 0.6:
                decisions.append(
                    {
                        "action": "scheduled_maintenance",
                        "type": "preventive_repair",
                        "cost": self.maintenance_cost,
                        "duration": 8,  # horas
                        "expected_improvement": 0.2,
                    }
                )

        return decisions

    async def _make_optimization_decisions(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Toma decisões de otimização"""
        decisions = []

        # Otimização de energia
        if self.optimization_algorithms["energy_optimization"]:
            energy_savings = await self._optimize_energy_consumption(situation)
            if energy_savings > 0.05:  # 5% de economia
                decisions.append(
                    {
                        "action": "energy_optimization",
                        "type": "efficiency_improvement",
                        "expected_savings": energy_savings,
                        "cost": self.operating_cost * 0.1,
                    }
                )

        # Otimização de capacidade
        if self.optimization_algorithms["capacity_planning"]:
            capacity_optimization = await self._optimize_capacity_utilization(situation)
            if capacity_optimization["improvement"] > 0.1:
                decisions.append(
                    {
                        "action": "capacity_optimization",
                        "type": "utilization_improvement",
                        "expected_improvement": capacity_optimization["improvement"],
                        "cost": self.operating_cost * 0.05,
                    }
                )

        return decisions

    async def _optimize_energy_consumption(self, situation: Dict[str, Any]) -> float:
        """Otimiza consumo de energia"""
        # Simula otimização baseada em carga e eficiência
        # Potencial de economia baseado na eficiência atual
        efficiency_improvement = (1 - situation["efficiency"]) * 0.3

        return efficiency_improvement

    async def _optimize_capacity_utilization(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Otimiza utilização de capacidade"""
        current_utilization = situation["load_percentage"]

        # Calcula potencial de melhoria
        if current_utilization < 0.5:
            improvement = 0.2  # Pode aumentar utilização
        elif current_utilization > 0.8:
            improvement = -0.1  # Precisa reduzir utilização
        else:
            improvement = 0.05  # Pequena melhoria

        return {
            "improvement": improvement,
            "current_utilization": current_utilization,
            "target_utilization": current_utilization + improvement,
        }

    async def _make_emergency_decisions(self, issues: List[Dict]) -> List[Dict[str, Any]]:
        """Toma decisões de emergência"""
        decisions = []

        critical_issues = [issue for issue in issues if issue["priority"] == "critical"]

        for issue in critical_issues:
            if issue["type"] == "overload":
                decisions.append(
                    {
                        "action": "emergency_response",
                        "type": "load_emergency",
                        "response": "immediate_load_reduction",
                        "severity": issue["severity"],
                        "affected_systems": self.connected_systems,
                    }
                )

            elif issue["type"] == "system_failure":
                decisions.append(
                    {
                        "action": "emergency_response",
                        "type": "system_failure",
                        "response": "activate_backup_systems",
                        "severity": issue["severity"],
                        "estimated_repair_time": 4,  # horas
                    }
                )

        return decisions

    async def update_state(self, delta_time: float) -> None:
        """Atualiza estado da infraestrutura a cada ciclo"""
        # Atualiza carga baseada na demanda
        self._update_load(delta_time)

        # Atualiza eficiência baseada na manutenção
        self._update_efficiency(delta_time)

        # Atualiza métricas de performance
        self._update_performance_metrics(delta_time)

        # Atualiza histórico
        self.load_history.append(self.current_load)
        if len(self.load_history) > 100:  # Mantém apenas últimos 100 registros
            self.load_history = self.load_history[-50:]

        # Atualiza timestamp
        self.state.last_update = datetime.now()

    def _update_load(self, delta_time: float) -> None:
        """Atualiza carga do sistema"""
        # Simula variação de carga baseada em fatores externos
        load_variation = random.uniform(-0.1, 0.1) * delta_time
        self.current_load = max(0, min(self.capacity, self.current_load + load_variation))

        # Atualiza porcentagem de carga
        self.system_status["load_percentage"] = self.current_load / self.capacity if self.capacity > 0 else 0

    def _update_efficiency(self, delta_time: float) -> None:
        """Atualiza eficiência do sistema"""
        # Eficiência degrada com o tempo sem manutenção
        days_since_maintenance = (datetime.now() - self.system_status["last_maintenance"]).days
        efficiency_degradation = min(0.1, days_since_maintenance * 0.001)

        self.efficiency = max(0.3, self.efficiency - efficiency_degradation * delta_time)
        self.system_status["efficiency_rating"] = self.efficiency

    def _update_performance_metrics(self, delta_time: float) -> None:
        """Atualiza métricas de performance"""
        # Atualiza uptime
        if self.system_status["operational"]:
            self.uptime = min(1.0, self.uptime + 0.001 * delta_time)
        else:
            self.uptime = max(0.0, self.uptime - 0.01 * delta_time)

        # Atualiza qualidade do serviço
        service_quality_factors = [self.efficiency, self.maintenance_level, self.uptime]
        target_quality = np.mean(service_quality_factors)

        quality_change = (target_quality - self.service_quality) * 0.1 * delta_time
        self.service_quality = max(0, min(1, self.service_quality + quality_change))

        # Atualiza satisfação do cliente
        satisfaction_factors = [
            self.service_quality,
            1 - self.system_status["load_percentage"],  # Menos carga = mais satisfação
            self.uptime,
        ]
        target_satisfaction = np.mean(satisfaction_factors)

        satisfaction_change = (target_satisfaction - self.customer_satisfaction) * 0.05 * delta_time
        self.customer_satisfaction = max(0, min(1, self.customer_satisfaction + satisfaction_change))

    async def _handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Processa mensagens específicas da infraestrutura"""
        if message.message_type == "service_request":
            return await self._handle_service_request(message.content)
        elif message.message_type == "emergency_alert":
            return await self._handle_emergency_alert(message.content)
        elif message.message_type == "maintenance_request":
            return await self._handle_maintenance_request(message.content)

        return await super()._handle_message(message)

    async def _handle_service_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa solicitação de serviço"""
        service_type = request.get("service_type")
        quantity = request.get("quantity", 1)
        priority = request.get("priority", "normal")

        # Verifica capacidade disponível
        available_capacity = self.capacity - self.current_load

        if available_capacity >= quantity:
            # Pode atender a solicitação
            self.current_load += quantity

            return {
                "action": "service_provided",
                "service_type": service_type,
                "quantity": quantity,
                "response_time": 1 / self.efficiency,
                "quality": self.service_quality,
            }
        else:
            # Não pode atender completamente
            if priority == "high":
                # Prioridade alta - tenta atender parcialmente
                partial_quantity = min(quantity, available_capacity)
                self.current_load += partial_quantity

                return {
                    "action": "partial_service",
                    "service_type": service_type,
                    "quantity_provided": partial_quantity,
                    "quantity_requested": quantity,
                    "response_time": 1 / self.efficiency,
                }
            else:
                # Prioridade normal - agenda para depois
                return {
                    "action": "service_queued",
                    "service_type": service_type,
                    "quantity": quantity,
                    "estimated_wait_time": 1 / self.efficiency,
                }

    async def _handle_emergency_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Processa alerta de emergência"""
        alert_type = alert.get("type")
        severity = alert.get("severity", 0.5)

        # Resposta baseada no tipo de alerta
        if alert_type == "power_outage":
            return await self._handle_power_outage(severity)
        elif alert_type == "system_failure":
            return await self._handle_system_failure(severity)
        elif alert_type == "natural_disaster":
            return await self._handle_natural_disaster(severity)

        return {"action": "emergency_acknowledged", "alert_type": alert_type, "response_time": 1 / self.efficiency}

    async def _handle_power_outage(self, severity: float) -> Dict[str, Any]:
        """Lida com queda de energia"""
        if severity > 0.7:
            # Falha crítica - ativa sistemas de backup
            return {
                "action": "activate_backup_power",
                "backup_capacity": self.capacity * 0.3,
                "estimated_duration": 2,  # horas
                "affected_services": self.connected_systems,
            }
        else:
            # Falha menor - reduz carga
            return {
                "action": "reduce_power_consumption",
                "reduction_percentage": severity * 0.5,
                "affected_services": self.connected_systems[:2],  # Apenas alguns serviços
            }

    async def _handle_system_failure(self, severity: float) -> Dict[str, Any]:
        """Lida com falha do sistema"""
        # Marca sistema como não operacional
        self.system_status["operational"] = False

        return {
            "action": "system_failure_response",
            "severity": severity,
            "estimated_repair_time": severity * 8,  # horas
            "backup_activation": severity > 0.5,
            "affected_customers": len(self.customers),
        }

    async def _handle_natural_disaster(self, severity: float) -> Dict[str, Any]:
        """Lida com desastre natural"""
        # Reduz capacidade baseada na severidade
        capacity_reduction = severity * 0.5
        self.capacity *= 1 - capacity_reduction

        return {
            "action": "disaster_response",
            "severity": severity,
            "capacity_reduction": capacity_reduction,
            "emergency_protocols_activated": True,
            "estimated_recovery_time": severity * 24,  # horas
        }

    async def _handle_maintenance_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa solicitação de manutenção"""
        maintenance_type = request.get("type")
        urgency = request.get("urgency", "normal")

        if urgency == "urgent":
            # Manutenção urgente
            self.system_status["maintenance_needed"] = True

            return {
                "action": "urgent_maintenance_scheduled",
                "maintenance_type": maintenance_type,
                "estimated_duration": 4,  # horas
                "cost": self.maintenance_cost * 1.5,
            }
        else:
            # Manutenção normal
            return {
                "action": "maintenance_scheduled",
                "maintenance_type": maintenance_type,
                "estimated_duration": 8,  # horas
                "cost": self.maintenance_cost,
            }

    def get_infrastructure_metrics(self) -> Dict[str, Any]:
        """Retorna métricas da infraestrutura"""
        return {
            "capacity": self.capacity,
            "current_load": self.current_load,
            "load_percentage": self.system_status["load_percentage"],
            "efficiency": self.efficiency,
            "uptime": self.uptime,
            "service_quality": self.service_quality,
            "customer_satisfaction": self.customer_satisfaction,
            "operational_cost": self.operating_cost,
            "maintenance_level": self.maintenance_level,
            "system_health": self._calculate_system_health(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converte infraestrutura para dicionário incluindo dados específicos"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "infrastructure_type": self.infrastructure_type,
                "capacity": self.capacity,
                "current_load": self.current_load,
                "system_status": self.system_status.copy(),
                "infrastructure_metrics": self.get_infrastructure_metrics(),
            }
        )
        return base_dict

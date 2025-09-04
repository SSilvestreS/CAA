"""
Agente Empresa - Representa empresas que fornecem produtos e serviços.
Usa IA para precificação dinâmica, previsão de demanda e logística.
"""

import asyncio
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from .base_agent import BaseAgent, AgentMessage


class BusinessAgent(BaseAgent):
    """
    Agente que representa uma empresa na cidade.
    Fornece produtos/serviços com precificação dinâmica e logística inteligente.
    """

    def __init__(self, name: str, business_type: str, position: tuple = (0, 0), **kwargs):
        super().__init__(name, position, **kwargs)

        # Características da empresa
        self.business_type = business_type  # 'energy', 'food', 'transport', 'healthcare', etc.
        self.size = random.choice(["small", "medium", "large"])
        self.capital = random.uniform(10000, 1000000)  # Capital inicial
        self.employees = random.randint(5, 500)

        # Capacidade e produção
        self.production_capacity = random.uniform(100, 10000)
        self.current_production = 0
        self.inventory = {}
        self.supply_chain = []

        # Preços e mercado
        self.base_price = random.uniform(10, 1000)
        self.current_price = self.base_price
        self.price_history = []
        self.demand_history = []
        self.competitors = []

        # Estratégia de negócio
        self.strategy = {
            "pricing": random.choice(["cost_plus", "market_based", "dynamic"]),
            "expansion": random.uniform(0, 1),
            "innovation": random.uniform(0, 1),
            "cooperation": random.uniform(0, 1),
        }

        # Métricas de performance
        self.revenue = 0
        self.profit_margin = random.uniform(0.1, 0.4)
        self.customer_satisfaction = 0.5
        self.market_share = random.uniform(0.01, 0.3)

        # IA para previsão e otimização
        self.demand_forecast = []
        self.price_optimization_model = None
        self.logistics_optimization = None

        # Relacionamentos
        self.suppliers = []
        self.customers = []
        self.partnerships = []

    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toma decisões estratégicas baseadas em mercado, concorrência e IA.
        """
        market_context = context.get("market", {})
        competitor_actions = context.get("competitor_actions", [])

        # Analisa situação atual
        current_situation = await self._analyze_market_situation(market_context)

        # Toma decisões baseadas na estratégia
        decisions = []

        # Decisão de preço
        pricing_decision = await self._make_pricing_decision(current_situation, competitor_actions)
        decisions.append(pricing_decision)

        # Decisão de produção
        production_decision = await self._make_production_decision(current_situation)
        decisions.append(production_decision)

        # Decisão de investimento
        investment_decision = await self._make_investment_decision(current_situation)
        decisions.append(investment_decision)

        # Decisão de marketing/expansão
        marketing_decision = await self._make_marketing_decision(current_situation)
        decisions.append(marketing_decision)

        return {"decisions": decisions, "situation_analysis": current_situation, "timestamp": datetime.now()}

    async def _analyze_market_situation(self, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa situação atual do mercado"""
        # Calcula demanda atual
        current_demand = market_context.get("demand", 0)
        demand_trend = self._calculate_demand_trend()

        # Analisa concorrência
        competitive_pressure = self._calculate_competitive_pressure()

        # Avalia capacidade de produção
        capacity_utilization = self.current_production / self.production_capacity

        # Calcula saúde financeira
        financial_health = self._calculate_financial_health()

        return {
            "current_demand": current_demand,
            "demand_trend": demand_trend,
            "competitive_pressure": competitive_pressure,
            "capacity_utilization": capacity_utilization,
            "financial_health": financial_health,
            "market_share": self.market_share,
            "customer_satisfaction": self.customer_satisfaction,
        }

    def _calculate_demand_trend(self) -> float:
        """Calcula tendência de demanda baseada no histórico"""
        if len(self.demand_history) < 3:
            return 0

        recent_demand = self.demand_history[-3:]
        trend = np.polyfit(range(len(recent_demand)), recent_demand, 1)[0]
        return trend

    def _calculate_competitive_pressure(self) -> float:
        """Calcula pressão competitiva baseada em concorrentes"""
        if not self.competitors:
            return 0

        # Calcula diferença de preços com concorrentes
        competitor_prices = [comp.current_price for comp in self.competitors]
        avg_competitor_price = np.mean(competitor_prices)
        price_difference = (self.current_price - avg_competitor_price) / avg_competitor_price

        return abs(price_difference)

    def _calculate_financial_health(self) -> float:
        """Calcula saúde financeira da empresa"""
        # Considera capital, receita e margem de lucro
        capital_ratio = min(1.0, self.capital / 100000)  # Normaliza para 0-1
        revenue_ratio = min(1.0, self.revenue / 1000000)  # Normaliza para 0-1
        margin_ratio = self.profit_margin

        return (capital_ratio + revenue_ratio + margin_ratio) / 3

    async def _make_pricing_decision(self, situation: Dict[str, Any], competitor_actions: List[Dict]) -> Dict[str, Any]:
        """Toma decisão de preço baseada em estratégia e IA"""
        current_price = self.current_price
        new_price = current_price

        if self.strategy["pricing"] == "dynamic":
            # Precificação dinâmica baseada em IA
            new_price = await self._dynamic_pricing(situation, competitor_actions)
        elif self.strategy["pricing"] == "market_based":
            # Precificação baseada no mercado
            new_price = await self._market_based_pricing(situation)
        else:  # cost_plus
            # Precificação baseada em custos
            new_price = await self._cost_plus_pricing(situation)

        # Aplica limites de preço
        min_price = self.base_price * 0.5
        max_price = self.base_price * 2.0
        new_price = max(min_price, min(max_price, new_price))

        return {
            "action": "price_adjustment",
            "old_price": current_price,
            "new_price": new_price,
            "change_percentage": (new_price - current_price) / current_price,
            "strategy": self.strategy["pricing"],
        }

    async def _dynamic_pricing(self, situation: Dict[str, Any], competitor_actions: List[Dict]) -> float:
        """Precificação dinâmica usando IA"""
        # Fatores que influenciam o preço
        demand_factor = situation["current_demand"] / 100  # Normaliza demanda
        competition_factor = 1 - situation["competitive_pressure"]
        capacity_factor = situation["capacity_utilization"]

        # Ajusta preço baseado nos fatores
        price_multiplier = 1.0

        # Aumenta preço se demanda alta e capacidade baixa
        if demand_factor > 0.7 and capacity_factor > 0.8:
            price_multiplier += 0.2

        # Diminui preço se competição alta
        if situation["competitive_pressure"] > 0.3:
            price_multiplier -= 0.1

        # Considera ações dos concorrentes
        for action in competitor_actions:
            if action.get("action") == "price_adjustment":
                competitor_change = action.get("change_percentage", 0)
                if competitor_change < -0.1:  # Concorrente baixou preço
                    price_multiplier -= 0.05

        return self.current_price * price_multiplier

    async def _market_based_pricing(self, situation: Dict[str, Any]) -> float:
        """Precificação baseada no mercado"""
        # Preço baseado na demanda e satisfação do cliente
        demand_factor = situation["current_demand"] / 100
        satisfaction_factor = situation["customer_satisfaction"]

        # Ajusta preço baseado na demanda
        if demand_factor > 0.8:
            return self.current_price * 1.1
        elif demand_factor < 0.3:
            return self.current_price * 0.9
        else:
            return self.current_price

    async def _cost_plus_pricing(self, situation: Dict[str, Any]) -> float:
        """Precificação baseada em custos + margem"""
        # Calcula custos de produção
        production_cost = self._calculate_production_cost()

        # Aplica margem de lucro desejada
        target_margin = self.profit_margin + 0.1  # Margem ligeiramente maior
        return production_cost * (1 + target_margin)

    def _calculate_production_cost(self) -> float:
        """Calcula custo de produção"""
        # Custo base por unidade
        base_cost = self.base_price * 0.6  # Assume 60% do preço é custo

        # Ajusta baseado na capacidade de produção
        capacity_factor = self.current_production / self.production_capacity
        if capacity_factor > 0.8:  # Produção alta = custos menores por unidade
            base_cost *= 0.9
        elif capacity_factor < 0.3:  # Produção baixa = custos maiores por unidade
            base_cost *= 1.1

        return base_cost

    async def _make_production_decision(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Decide sobre níveis de produção"""
        current_demand = situation["current_demand"]
        capacity_utilization = situation["capacity_utilization"]

        # Calcula produção ideal baseada na demanda
        target_production = min(current_demand, self.production_capacity)

        # Ajusta baseado na estratégia
        if self.strategy["expansion"] > 0.7:
            # Estratégia agressiva - produz mais
            target_production = min(target_production * 1.2, self.production_capacity)
        elif self.strategy["expansion"] < 0.3:
            # Estratégia conservadora - produz menos
            target_production *= 0.8

        # Calcula custo de ajuste de produção
        production_change = target_production - self.current_production
        adjustment_cost = abs(production_change) * 0.1  # Custo de ajuste

        return {
            "action": "production_adjustment",
            "current_production": self.current_production,
            "target_production": target_production,
            "change": production_change,
            "adjustment_cost": adjustment_cost,
        }

    async def _make_investment_decision(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Decide sobre investimentos"""
        financial_health = situation["financial_health"]
        market_share = situation["market_share"]

        investment_opportunities = []

        # Investimento em capacidade
        if situation["capacity_utilization"] > 0.9 and financial_health > 0.6:
            investment_opportunities.append(
                {"type": "capacity_expansion", "cost": self.capital * 0.2, "expected_return": 0.15, "priority": "high"}
            )

        # Investimento em inovação
        if self.strategy["innovation"] > 0.6 and financial_health > 0.5:
            investment_opportunities.append(
                {"type": "innovation", "cost": self.capital * 0.1, "expected_return": 0.2, "priority": "medium"}
            )

        # Investimento em marketing
        if market_share < 0.1 and financial_health > 0.4:
            investment_opportunities.append(
                {"type": "marketing", "cost": self.capital * 0.05, "expected_return": 0.1, "priority": "medium"}
            )

        return {
            "action": "investment_analysis",
            "opportunities": investment_opportunities,
            "recommended_investment": (
                max(investment_opportunities, key=lambda x: x["expected_return"]) if investment_opportunities else None
            ),
        }

    async def _make_marketing_decision(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Decide sobre estratégias de marketing"""
        customer_satisfaction = situation["customer_satisfaction"]
        market_share = situation["market_share"]

        marketing_actions = []

        # Marketing para satisfação baixa
        if customer_satisfaction < 0.4:
            marketing_actions.append(
                {"type": "customer_retention", "cost": self.capital * 0.03, "target": "existing_customers"}
            )

        # Marketing para expansão
        if market_share < 0.2 and self.strategy["expansion"] > 0.5:
            marketing_actions.append(
                {"type": "market_expansion", "cost": self.capital * 0.05, "target": "new_customers"}
            )

        # Marketing competitivo
        if situation["competitive_pressure"] > 0.5:
            marketing_actions.append(
                {"type": "competitive_positioning", "cost": self.capital * 0.02, "target": "market_share"}
            )

        return {
            "action": "marketing_strategy",
            "campaigns": marketing_actions,
            "total_budget": sum(action["cost"] for action in marketing_actions),
        }

    async def update_state(self, delta_time: float) -> None:
        """Atualiza estado da empresa a cada ciclo"""
        # Atualiza produção
        if self.current_production > 0:
            # Produz bens/serviços
            production_rate = self.current_production * delta_time
            if self.business_type not in self.inventory:
                self.inventory[self.business_type] = 0
            self.inventory[self.business_type] += production_rate

        # Atualiza receita baseada em vendas
        sales = self._calculate_sales(delta_time)
        self.revenue += sales

        # Atualiza capital
        costs = self._calculate_operating_costs(delta_time)
        self.capital += sales - costs

        # Atualiza satisfação do cliente
        self._update_customer_satisfaction(delta_time)

        # Atualiza participação de mercado
        self._update_market_share(delta_time)

        # Atualiza timestamp
        self.state.last_update = datetime.now()

    def _calculate_sales(self, delta_time: float) -> float:
        """Calcula vendas baseadas em demanda e preço"""
        # Simula vendas baseadas na demanda e satisfação
        base_sales = self.current_production * self.current_price * delta_time
        satisfaction_multiplier = self.customer_satisfaction
        return base_sales * satisfaction_multiplier

    def _calculate_operating_costs(self, delta_time: float) -> float:
        """Calcula custos operacionais"""
        # Custos fixos
        fixed_costs = self.employees * 100 * delta_time  # Custo por funcionário

        # Custos variáveis baseados na produção
        variable_costs = self.current_production * self.base_price * 0.6 * delta_time

        return fixed_costs + variable_costs

    def _update_customer_satisfaction(self, delta_time: float) -> None:
        """Atualiza satisfação do cliente"""
        # Fatores que afetam satisfação
        price_factor = 1 - (self.current_price - self.base_price) / self.base_price
        quality_factor = min(1.0, self.current_production / self.production_capacity)

        # Atualiza satisfação gradualmente
        target_satisfaction = (price_factor + quality_factor) / 2
        satisfaction_change = (target_satisfaction - self.customer_satisfaction) * 0.1 * delta_time
        self.customer_satisfaction = max(0, min(1, self.customer_satisfaction + satisfaction_change))

    def _update_market_share(self, delta_time: float) -> None:
        """Atualiza participação de mercado"""
        # Baseado na performance relativa
        performance_factor = (self.customer_satisfaction + self.profit_margin) / 2

        if performance_factor > 0.7:
            self.market_share = min(1.0, self.market_share + 0.01 * delta_time)
        elif performance_factor < 0.3:
            self.market_share = max(0, self.market_share - 0.01 * delta_time)

    async def _handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Processa mensagens específicas da empresa"""
        if message.message_type == "purchase_request":
            return await self._handle_purchase_request(message.content)
        elif message.message_type == "partnership_proposal":
            return await self._handle_partnership_proposal(message.content)
        elif message.message_type == "regulation_change":
            return await self._handle_regulation_change(message.content)

        return await super()._handle_message(message)

    async def _handle_purchase_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa solicitação de compra"""
        quantity = request.get("quantity", 1)
        max_price = request.get("max_price", self.current_price)

        # Verifica se pode atender
        available = self.inventory.get(self.business_type, 0)

        if available >= quantity and max_price >= self.current_price:
            # Aceita a compra
            total_cost = quantity * self.current_price
            return {
                "action": "accept_purchase",
                "quantity": quantity,
                "price": self.current_price,
                "total_cost": total_cost,
            }
        else:
            # Negocia ou recusa
            if available < quantity:
                return {"action": "partial_fulfillment", "available_quantity": available, "price": self.current_price}
            else:
                return {"action": "price_too_low", "minimum_price": self.current_price}

    async def _handle_partnership_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Processa proposta de parceria"""
        partner_type = proposal.get("partner_type")
        benefits = proposal.get("benefits", {})

        # Avalia proposta baseada na estratégia
        if self.strategy["cooperation"] > 0.6:
            return {"action": "accept_partnership", "terms": benefits}
        else:
            return {"action": "decline_partnership", "reason": "low_cooperation_strategy"}

    async def _handle_regulation_change(self, regulation: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mudança regulatória"""
        regulation_type = regulation.get("type")
        impact = regulation.get("impact", 0)

        # Ajusta operações baseado na regulamentação
        if regulation_type == "price_cap" and impact < 0:
            # Limite de preço
            max_price = regulation.get("max_price", self.current_price)
            if self.current_price > max_price:
                self.current_price = max_price

        elif regulation_type == "production_quota" and impact < 0:
            # Quota de produção
            max_production = regulation.get("max_production", self.production_capacity)
            self.production_capacity = min(self.production_capacity, max_production)

        return {"action": "regulation_compliance", "adjustments_made": True, "impact_assessment": impact}

    def get_business_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de negócio"""
        return {
            "revenue": self.revenue,
            "capital": self.capital,
            "profit_margin": self.profit_margin,
            "market_share": self.market_share,
            "customer_satisfaction": self.customer_satisfaction,
            "capacity_utilization": self.current_production / self.production_capacity,
            "employee_count": self.employees,
            "business_type": self.business_type,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converte empresa para dicionário incluindo dados específicos"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "business_type": self.business_type,
                "size": self.size,
                "capital": self.capital,
                "employees": self.employees,
                "current_price": self.current_price,
                "business_metrics": self.get_business_metrics(),
                "strategy": self.strategy.copy(),
            }
        )
        return base_dict

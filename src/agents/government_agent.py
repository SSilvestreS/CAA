"""
Agente Governo - Representa órgãos públicos e governo.
Define regras, impostos, fiscalização e políticas públicas.
"""

import asyncio
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from .base_agent import BaseAgent, AgentMessage


class GovernmentAgent(BaseAgent):
    """
    Agente que representa o governo da cidade.
    Define regras, políticas públicas, fiscalização e mantém equilíbrio social.
    """
    
    def __init__(self, name: str, position: tuple = (0, 0), **kwargs):
        super().__init__(name, position, **kwargs)
        
        # Características do governo
        self.government_type = random.choice(['democratic', 'authoritarian', 'technocratic'])
        self.efficiency = random.uniform(0.3, 0.9)  # Eficiência governamental
        self.corruption_level = random.uniform(0.0, 0.3)  # Nível de corrupção
        
        # Recursos e orçamento
        self.budget = random.uniform(1000000, 10000000)  # Orçamento anual
        self.tax_revenue = 0
        self.expenses = 0
        
        # Políticas e regulamentações
        self.policies = {
            'tax_rate': random.uniform(0.1, 0.4),  # Taxa de impostos
            'minimum_wage': random.uniform(1000, 3000),
            'environmental_regulations': random.uniform(0.1, 0.9),
            'social_welfare': random.uniform(0.1, 0.8),
            'infrastructure_investment': random.uniform(0.1, 0.7),
            'public_services': random.uniform(0.2, 0.9)
        }
        
        # Serviços públicos
        self.public_services = {
            'healthcare': random.uniform(0.3, 0.9),
            'education': random.uniform(0.3, 0.9),
            'transportation': random.uniform(0.2, 0.8),
            'security': random.uniform(0.4, 0.9),
            'utilities': random.uniform(0.5, 0.9)
        }
        
        # Métricas de governança
        self.citizen_satisfaction = 0.5
        self.economic_health = 0.5
        self.social_stability = 0.5
        self.environmental_health = 0.5
        
        # Histórico de decisões
        self.policy_history = []
        self.regulation_history = []
        self.crisis_responses = []
        
        # IA para políticas
        self.policy_optimization_model = None
        self.impact_assessment_model = None
        
        # Relacionamentos
        self.citizens = []
        self.businesses = []
        self.infrastructure_agents = []
        
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toma decisões governamentais baseadas em métricas sociais e econômicas.
        """
        # Analisa situação atual
        current_situation = await self._analyze_city_situation(context)
        
        # Identifica problemas prioritários
        priority_issues = await self._identify_priority_issues(current_situation)
        
        # Toma decisões baseadas nos problemas identificados
        decisions = []
        
        # Decisões de política
        policy_decisions = await self._make_policy_decisions(priority_issues, current_situation)
        decisions.extend(policy_decisions)
        
        # Decisões de regulamentação
        regulation_decisions = await self._make_regulation_decisions(priority_issues, current_situation)
        decisions.extend(regulation_decisions)
        
        # Decisões de investimento
        investment_decisions = await self._make_investment_decisions(current_situation)
        decisions.extend(investment_decisions)
        
        # Decisões de fiscalização
        enforcement_decisions = await self._make_enforcement_decisions(current_situation)
        decisions.extend(enforcement_decisions)
        
        return {
            'decisions': decisions,
            'situation_analysis': current_situation,
            'priority_issues': priority_issues,
            'timestamp': datetime.now()
        }
    
    async def _analyze_city_situation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa situação geral da cidade"""
        # Coleta dados dos agentes
        citizen_data = context.get('citizens', [])
        business_data = context.get('businesses', [])
        infrastructure_data = context.get('infrastructure', [])
        
        # Calcula métricas agregadas
        avg_citizen_satisfaction = np.mean([c.get('satisfaction', 0.5) for c in citizen_data])
        avg_business_health = np.mean([b.get('business_metrics', {}).get('profit_margin', 0.2) for b in business_data])
        
        # Calcula indicadores econômicos
        total_tax_revenue = sum([b.get('business_metrics', {}).get('revenue', 0) * self.policies['tax_rate'] for b in business_data])
        unemployment_rate = self._calculate_unemployment_rate(citizen_data)
        
        # Calcula indicadores sociais
        social_inequality = self._calculate_social_inequality(citizen_data)
        crime_rate = self._calculate_crime_rate(citizen_data)
        
        # Calcula indicadores ambientais
        environmental_impact = self._calculate_environmental_impact(business_data, infrastructure_data)
        
        return {
            'citizen_satisfaction': avg_citizen_satisfaction,
            'economic_health': avg_business_health,
            'tax_revenue': total_tax_revenue,
            'unemployment_rate': unemployment_rate,
            'social_inequality': social_inequality,
            'crime_rate': crime_rate,
            'environmental_impact': environmental_impact,
            'budget_balance': self.budget - self.expenses
        }
    
    def _calculate_unemployment_rate(self, citizen_data: List[Dict]) -> float:
        """Calcula taxa de desemprego"""
        if not citizen_data:
            return 0.1  # Taxa padrão
        
        unemployed = sum(1 for c in citizen_data if c.get('income', 0) < 1000)
        return unemployed / len(citizen_data)
    
    def _calculate_social_inequality(self, citizen_data: List[Dict]) -> float:
        """Calcula índice de desigualdade social"""
        if not citizen_data:
            return 0.5
        
        incomes = [c.get('income', 1000) for c in citizen_data]
        if len(incomes) < 2:
            return 0.5
        
        # Calcula coeficiente de Gini simplificado
        incomes.sort()
        n = len(incomes)
        cumsum = np.cumsum(incomes)
        return (n + 1 - 2 * sum((n + 1 - i) * y for i, y in enumerate(cumsum, 1))) / (n * sum(incomes))
    
    def _calculate_crime_rate(self, citizen_data: List[Dict]) -> float:
        """Calcula taxa de criminalidade"""
        if not citizen_data:
            return 0.1
        
        # Baseado em stress, satisfação e desigualdade social
        high_stress_citizens = sum(1 for c in citizen_data if c.get('stress_level', 0) > 0.7)
        low_satisfaction_citizens = sum(1 for c in citizen_data if c.get('satisfaction', 0.5) < 0.3)
        
        crime_factors = (high_stress_citizens + low_satisfaction_citizens) / (2 * len(citizen_data))
        return min(1.0, crime_factors * 0.5)  # Normaliza para 0-1
    
    def _calculate_environmental_impact(self, business_data: List[Dict], 
                                      infrastructure_data: List[Dict]) -> float:
        """Calcula impacto ambiental"""
        # Baseado em produção industrial e uso de energia
        total_production = sum(b.get('business_metrics', {}).get('current_production', 0) for b in business_data)
        energy_consumption = sum(i.get('energy_consumption', 0) for i in infrastructure_data)
        
        # Normaliza e combina fatores
        production_impact = min(1.0, total_production / 10000)
        energy_impact = min(1.0, energy_consumption / 5000)
        
        return (production_impact + energy_impact) / 2
    
    async def _identify_priority_issues(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica problemas prioritários baseados na situação atual"""
        issues = []
        
        # Problemas de satisfação cidadã
        if situation['citizen_satisfaction'] < 0.4:
            issues.append({
                'type': 'citizen_dissatisfaction',
                'severity': 1 - situation['citizen_satisfaction'],
                'priority': 'high'
            })
        
        # Problemas econômicos
        if situation['unemployment_rate'] > 0.15:
            issues.append({
                'type': 'high_unemployment',
                'severity': situation['unemployment_rate'],
                'priority': 'high'
            })
        
        # Problemas de desigualdade
        if situation['social_inequality'] > 0.7:
            issues.append({
                'type': 'social_inequality',
                'severity': situation['social_inequality'],
                'priority': 'medium'
            })
        
        # Problemas de criminalidade
        if situation['crime_rate'] > 0.3:
            issues.append({
                'type': 'high_crime',
                'severity': situation['crime_rate'],
                'priority': 'high'
            })
        
        # Problemas ambientais
        if situation['environmental_impact'] > 0.7:
            issues.append({
                'type': 'environmental_degradation',
                'severity': situation['environmental_impact'],
                'priority': 'medium'
            })
        
        # Problemas orçamentários
        if situation['budget_balance'] < 0:
            issues.append({
                'type': 'budget_deficit',
                'severity': abs(situation['budget_balance']) / self.budget,
                'priority': 'high'
            })
        
        # Ordena por prioridade e severidade
        issues.sort(key=lambda x: (x['priority'] == 'high', x['severity']), reverse=True)
        return issues
    
    async def _make_policy_decisions(self, priority_issues: List[Dict], 
                                   situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Toma decisões de política baseadas nos problemas identificados"""
        decisions = []
        
        for issue in priority_issues[:3]:  # Foca nos 3 problemas mais importantes
            if issue['type'] == 'citizen_dissatisfaction':
                decision = await self._address_citizen_dissatisfaction(issue, situation)
                decisions.append(decision)
            
            elif issue['type'] == 'high_unemployment':
                decision = await self._address_unemployment(issue, situation)
                decisions.append(decision)
            
            elif issue['type'] == 'social_inequality':
                decision = await self._address_social_inequality(issue, situation)
                decisions.append(decision)
            
            elif issue['type'] == 'high_crime':
                decision = await self._address_crime(issue, situation)
                decisions.append(decision)
            
            elif issue['type'] == 'environmental_degradation':
                decision = await self._address_environmental_issues(issue, situation)
                decisions.append(decision)
        
        return decisions
    
    async def _address_citizen_dissatisfaction(self, issue: Dict, situation: Dict) -> Dict[str, Any]:
        """Endereça insatisfação cidadã"""
        # Aumenta investimento em serviços públicos
        service_increase = min(0.1, issue['severity'] * 0.2)
        
        for service in self.public_services:
            self.public_services[service] = min(1.0, self.public_services[service] + service_increase)
        
        cost = self.budget * service_increase * 0.1
        
        return {
            'action': 'improve_public_services',
            'service_increase': service_increase,
            'cost': cost,
            'expected_impact': service_increase * 0.8
        }
    
    async def _address_unemployment(self, issue: Dict, situation: Dict) -> Dict[str, Any]:
        """Endereça desemprego alto"""
        # Cria programa de emprego público
        job_creation_cost = self.budget * 0.05
        jobs_created = int(issue['severity'] * 100)
        
        return {
            'action': 'create_public_jobs',
            'jobs_created': jobs_created,
            'cost': job_creation_cost,
            'expected_impact': issue['severity'] * 0.6
        }
    
    async def _address_social_inequality(self, issue: Dict, situation: Dict) -> Dict[str, Any]:
        """Endereça desigualdade social"""
        # Implementa programa de redistribuição de renda
        redistribution_rate = min(0.1, issue['severity'] * 0.15)
        self.policies['social_welfare'] = min(1.0, self.policies['social_welfare'] + redistribution_rate)
        
        cost = self.budget * redistribution_rate * 0.2
        
        return {
            'action': 'increase_social_welfare',
            'redistribution_rate': redistribution_rate,
            'cost': cost,
            'expected_impact': redistribution_rate * 0.7
        }
    
    async def _address_crime(self, issue: Dict, situation: Dict) -> Dict[str, Any]:
        """Endereça criminalidade alta"""
        # Aumenta investimento em segurança
        security_increase = min(0.2, issue['severity'] * 0.3)
        self.public_services['security'] = min(1.0, self.public_services['security'] + security_increase)
        
        cost = self.budget * security_increase * 0.15
        
        return {
            'action': 'increase_security',
            'security_increase': security_increase,
            'cost': cost,
            'expected_impact': security_increase * 0.9
        }
    
    async def _address_environmental_issues(self, issue: Dict, situation: Dict) -> Dict[str, Any]:
        """Endereça problemas ambientais"""
        # Aumenta regulamentações ambientais
        regulation_increase = min(0.2, issue['severity'] * 0.25)
        self.policies['environmental_regulations'] = min(1.0, 
                                                       self.policies['environmental_regulations'] + regulation_increase)
        
        return {
            'action': 'strengthen_environmental_regulations',
            'regulation_increase': regulation_increase,
            'cost': 0,  # Regulamentação não tem custo direto
            'expected_impact': regulation_increase * 0.6
        }
    
    async def _make_regulation_decisions(self, priority_issues: List[Dict], 
                                       situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Toma decisões de regulamentação"""
        decisions = []
        
        # Regulamentação de preços se inflação alta
        if situation.get('inflation_rate', 0) > 0.1:
            decisions.append({
                'action': 'price_regulation',
                'type': 'price_cap',
                'max_increase': 0.05,
                'affected_sectors': ['food', 'housing', 'utilities']
            })
        
        # Regulamentação ambiental se impacto alto
        if situation['environmental_impact'] > 0.6:
            decisions.append({
                'action': 'environmental_regulation',
                'type': 'emission_limits',
                'reduction_target': 0.2,
                'affected_sectors': ['energy', 'manufacturing']
            })
        
        return decisions
    
    async def _make_investment_decisions(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Toma decisões de investimento público"""
        decisions = []
        
        # Investimento em infraestrutura se orçamento permite
        if situation['budget_balance'] > self.budget * 0.1:
            infrastructure_investment = self.budget * 0.05
            decisions.append({
                'action': 'infrastructure_investment',
                'amount': infrastructure_investment,
                'target': 'transportation',
                'expected_return': 0.1
            })
        
        # Investimento em educação se desigualdade alta
        if situation['social_inequality'] > 0.6:
            education_investment = self.budget * 0.03
            decisions.append({
                'action': 'education_investment',
                'amount': education_investment,
                'target': 'public_education',
                'expected_return': 0.15
            })
        
        return decisions
    
    async def _make_enforcement_decisions(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Toma decisões de fiscalização"""
        decisions = []
        
        # Fiscalização de impostos se receita baixa
        if situation['tax_revenue'] < self.budget * 0.3:
            decisions.append({
                'action': 'tax_enforcement',
                'type': 'audit_companies',
                'target_companies': 10,
                'expected_revenue': self.budget * 0.02
            })
        
        # Fiscalização ambiental se regulamentações altas
        if self.policies['environmental_regulations'] > 0.7:
            decisions.append({
                'action': 'environmental_enforcement',
                'type': 'compliance_check',
                'target_companies': 15,
                'expected_impact': 0.1
            })
        
        return decisions
    
    async def update_state(self, delta_time: float) -> None:
        """Atualiza estado do governo a cada ciclo"""
        # Atualiza receita de impostos
        self.tax_revenue = self._calculate_tax_revenue()
        
        # Atualiza despesas
        self.expenses = self._calculate_expenses()
        
        # Atualiza orçamento
        self.budget += (self.tax_revenue - self.expenses) * delta_time
        
        # Atualiza métricas de governança
        self._update_governance_metrics(delta_time)
        
        # Atualiza timestamp
        self.state.last_update = datetime.now()
    
    def _calculate_tax_revenue(self) -> float:
        """Calcula receita de impostos"""
        # Baseado na receita das empresas e renda dos cidadãos
        business_tax = 0  # Será calculado baseado nos dados das empresas
        citizen_tax = 0   # Será calculado baseado na renda dos cidadãos
        
        return (business_tax + citizen_tax) * self.policies['tax_rate']
    
    def _calculate_expenses(self) -> float:
        """Calcula despesas governamentais"""
        # Despesas com serviços públicos
        service_costs = sum(self.public_services.values()) * 10000
        
        # Despesas administrativas
        admin_costs = self.budget * 0.1
        
        # Despesas com programas sociais
        social_costs = self.policies['social_welfare'] * self.budget * 0.2
        
        return service_costs + admin_costs + social_costs
    
    def _update_governance_metrics(self, delta_time: float) -> None:
        """Atualiza métricas de governança"""
        # Atualiza satisfação cidadã baseada em serviços públicos
        service_quality = np.mean(list(self.public_services.values()))
        target_satisfaction = service_quality * (1 - self.corruption_level)
        
        satisfaction_change = (target_satisfaction - self.citizen_satisfaction) * 0.1 * delta_time
        self.citizen_satisfaction = max(0, min(1, self.citizen_satisfaction + satisfaction_change))
        
        # Atualiza estabilidade social
        stability_factors = [
            1 - self.corruption_level,
            self.citizen_satisfaction,
            self.policies['social_welfare']
        ]
        target_stability = np.mean(stability_factors)
        
        stability_change = (target_stability - self.social_stability) * 0.05 * delta_time
        self.social_stability = max(0, min(1, self.social_stability + stability_change))
    
    async def _handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Processa mensagens específicas do governo"""
        if message.message_type == 'complaint':
            return await self._handle_complaint(message.content)
        elif message.message_type == 'lobby_request':
            return await self._handle_lobby_request(message.content)
        elif message.message_type == 'emergency_report':
            return await self._handle_emergency_report(message.content)
        
        return await super()._handle_message(message)
    
    async def _handle_complaint(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """Processa reclamação de cidadão"""
        complaint_type = complaint.get('type')
        severity = complaint.get('severity', 0.5)
        
        # Resposta baseada na eficiência governamental
        response_time = 1 / self.efficiency  # Eficiência alta = resposta rápida
        
        if severity > 0.7 and self.efficiency > 0.6:
            return {
                'action': 'immediate_investigation',
                'response_time': response_time,
                'priority': 'high'
            }
        else:
            return {
                'action': 'standard_investigation',
                'response_time': response_time * 2,
                'priority': 'medium'
            }
    
    async def _handle_lobby_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa solicitação de lobby de empresa"""
        request_type = request.get('type')
        company_influence = request.get('influence', 0.5)
        
        # Considera corrupção e influência
        success_probability = company_influence * (1 + self.corruption_level)
        
        if success_probability > 0.6:
            return {
                'action': 'consider_request',
                'success_probability': success_probability,
                'decision_delay': 1 / self.efficiency
            }
        else:
            return {
                'action': 'decline_request',
                'reason': 'insufficient_influence'
            }
    
    async def _handle_emergency_report(self, emergency: Dict[str, Any]) -> Dict[str, Any]:
        """Processa relatório de emergência"""
        emergency_type = emergency.get('type')
        severity = emergency.get('severity', 0.5)
        
        # Resposta baseada na eficiência e tipo de emergência
        if emergency_type in ['natural_disaster', 'pandemic', 'terrorism']:
            response_level = 'national'
        else:
            response_level = 'local'
        
        return {
            'action': 'emergency_response',
            'response_level': response_level,
            'resources_allocated': severity * self.budget * 0.1,
            'response_time': 1 / self.efficiency
        }
    
    def get_governance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de governança"""
        return {
            'citizen_satisfaction': self.citizen_satisfaction,
            'economic_health': self.economic_health,
            'social_stability': self.social_stability,
            'environmental_health': self.environmental_health,
            'budget_balance': self.budget - self.expenses,
            'efficiency': self.efficiency,
            'corruption_level': self.corruption_level,
            'tax_rate': self.policies['tax_rate']
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte governo para dicionário incluindo dados específicos"""
        base_dict = super().to_dict()
        base_dict.update({
            'government_type': self.government_type,
            'budget': self.budget,
            'policies': self.policies.copy(),
            'public_services': self.public_services.copy(),
            'governance_metrics': self.get_governance_metrics()
        })
        return base_dict

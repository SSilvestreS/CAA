"""
Agente Cidadão - Representa um cidadão da cidade inteligente.
Possui personalidade, rotina, necessidades e capacidade de aprendizado.
"""

import asyncio
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from .base_agent import BaseAgent, AgentMessage


class CitizenAgent(BaseAgent):
    """
    Agente que representa um cidadão da cidade.
    Possui necessidades básicas, rotina diária e capacidade de aprendizado.
    """
    
    def __init__(self, name: str, position: tuple = (0, 0), **kwargs):
        super().__init__(name, position, **kwargs)
        
        # Características específicas do cidadão
        self.age = random.randint(18, 80)
        self.income = random.uniform(1000, 10000)  # Renda mensal
        self.education_level = random.uniform(0, 1)  # Nível educacional
        
        # Necessidades básicas
        self.needs = {
            'food': random.uniform(0.3, 0.8),
            'transport': random.uniform(0.2, 0.7),
            'healthcare': random.uniform(0.1, 0.6),
            'entertainment': random.uniform(0.1, 0.5),
            'housing': random.uniform(0.4, 0.9),
            'energy': random.uniform(0.3, 0.7)
        }
        
        # Rotina diária (horários de atividades)
        self.daily_routine = self._generate_routine()
        self.current_activity = 'sleeping'
        self.activity_start_time = datetime.now()
        
        # Estado emocional e social
        self.stress_level = random.uniform(0, 0.5)
        self.social_connections = []
        self.complaints = []
        self.suggestions = []
        
        # Histórico de decisões para aprendizado
        self.decision_history = []
        self.learning_rate = 0.1
        
    def _generate_routine(self) -> Dict[str, tuple]:
        """Gera uma rotina diária baseada na personalidade"""
        routine = {}
        base_hour = 6  # Hora base para começar o dia
        
        # Horário de dormir (baseado na personalidade)
        sleep_time = base_hour + random.randint(0, 2)
        wake_time = sleep_time + random.randint(6, 10)
        
        routine['sleep'] = (sleep_time, wake_time)
        routine['work'] = (wake_time + 1, wake_time + 9)
        routine['leisure'] = (wake_time + 9, sleep_time - 1)
        routine['shopping'] = (wake_time + 9, wake_time + 11)
        
        return routine
    
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toma decisões baseadas em necessidades, personalidade e contexto.
        Usa aprendizado por reforço para melhorar decisões ao longo do tempo.
        """
        current_time = datetime.now().hour
        decision_context = {
            'time': current_time,
            'needs': self.needs,
            'resources': self.state.resources,
            'personality': self.personality,
            'stress': self.stress_level,
            'context': context
        }
        
        # Determina atividade baseada na rotina
        activity = self._determine_activity(current_time)
        
        # Toma decisões baseadas na atividade atual
        if activity == 'working':
            decision = await self._make_work_decision(decision_context)
        elif activity == 'shopping':
            decision = await self._make_shopping_decision(decision_context)
        elif activity == 'leisure':
            decision = await self._make_leisure_decision(decision_context)
        else:
            decision = await self._make_basic_decision(decision_context)
        
        # Aprende com a decisão
        self._learn_from_decision(decision, decision_context)
        
        return decision
    
    def _determine_activity(self, current_hour: int) -> str:
        """Determina a atividade atual baseada na rotina"""
        for activity, (start, end) in self.daily_routine.items():
            if start <= current_hour < end:
                return activity
        return 'sleeping'
    
    async def _make_work_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decisões relacionadas ao trabalho"""
        # Simula produtividade baseada em stress e energia
        productivity = (self.state.energy * 0.6 + 
                       (1 - self.stress_level) * 0.4)
        
        # Decisão de trabalhar mais ou menos
        if productivity > 0.7 and self.personality['risk_tolerance'] > 0.5:
            return {
                'action': 'work_overtime',
                'duration': random.randint(1, 3),
                'expected_income': self.income * 0.1 * productivity
            }
        else:
            return {
                'action': 'work_normal',
                'duration': 8,
                'expected_income': self.income * 0.1 * productivity
            }
    
    async def _make_shopping_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decisões de compra baseadas em necessidades e orçamento"""
        # Prioriza necessidades mais urgentes
        urgent_needs = {k: v for k, v in self.needs.items() 
                       if v > 0.7 and k in ['food', 'healthcare', 'housing']}
        
        if urgent_needs:
            need = max(urgent_needs, key=urgent_needs.get)
            budget = min(self.income * 0.1, self.state.resources.get('money', 0))
            
            return {
                'action': 'purchase',
                'item': need,
                'budget': budget,
                'priority': 'high'
            }
        
        # Compra por prazer/entretenimento
        if self.personality['social_orientation'] > 0.6:
            return {
                'action': 'social_purchase',
                'budget': self.income * 0.05,
                'priority': 'low'
            }
        
        return {'action': 'no_purchase'}
    
    async def _make_leisure_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decisões de lazer e entretenimento"""
        if self.stress_level > 0.7:
            return {
                'action': 'stress_relief',
                'activity': 'exercise' if self.personality['innovation'] > 0.5 else 'relaxation',
                'duration': random.randint(1, 3)
            }
        
        if self.personality['social_orientation'] > 0.6:
            return {
                'action': 'social_activity',
                'activity': 'meet_friends',
                'duration': random.randint(2, 4)
            }
        
        return {
            'action': 'personal_leisure',
            'activity': 'hobby',
            'duration': random.randint(1, 2)
        }
    
    async def _make_basic_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decisões básicas quando não há atividade específica"""
        # Verifica necessidades críticas
        critical_needs = {k: v for k, v in self.needs.items() if v > 0.9}
        
        if critical_needs:
            return {
                'action': 'address_critical_need',
                'need': max(critical_needs, key=critical_needs.get),
                'priority': 'critical'
            }
        
        return {'action': 'rest'}
    
    def _learn_from_decision(self, decision: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Aprende com decisões passadas usando reforço"""
        # Armazena decisão no histórico
        self.decision_history.append({
            'decision': decision,
            'context': context,
            'timestamp': datetime.now(),
            'outcome': None  # Será preenchido posteriormente
        })
        
        # Limita histórico para evitar uso excessivo de memória
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-50:]
    
    async def update_state(self, delta_time: float) -> None:
        """Atualiza estado do cidadão a cada ciclo"""
        # Atualiza necessidades (aumentam com o tempo)
        for need in self.needs:
            self.needs[need] = min(1.0, self.needs[need] + 0.01 * delta_time)
        
        # Atualiza energia baseada na atividade
        if self.current_activity == 'sleeping':
            self.update_energy(0.1 * delta_time)
        elif self.current_activity == 'working':
            self.update_energy(-0.05 * delta_time)
        else:
            self.update_energy(-0.02 * delta_time)
        
        # Atualiza stress baseado em necessidades não atendidas
        unmet_needs = sum(1 for need in self.needs.values() if need > 0.8)
        stress_change = unmet_needs * 0.1 * delta_time
        self.stress_level = min(1.0, self.stress_level + stress_change)
        
        # Atualiza satisfação baseada em necessidades atendidas
        satisfied_needs = sum(1 for need in self.needs.values() if need < 0.3)
        satisfaction_change = satisfied_needs * 0.05 * delta_time
        self.update_satisfaction(satisfaction_change)
        
        # Atualiza timestamp
        self.state.last_update = datetime.now()
    
    async def _handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Processa mensagens específicas do cidadão"""
        if message.message_type == 'service_offer':
            # Avalia oferta de serviço
            return await self._evaluate_service_offer(message.content)
        elif message.message_type == 'policy_announcement':
            # Reage a anúncios de política
            return await self._react_to_policy(message.content)
        elif message.message_type == 'emergency_alert':
            # Reage a alertas de emergência
            return await self._react_to_emergency(message.content)
        
        return await super()._handle_message(message)
    
    async def _evaluate_service_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia oferta de serviço baseada em necessidades e orçamento"""
        service_type = offer.get('service_type')
        price = offer.get('price', 0)
        
        if service_type in self.needs:
            need_level = self.needs[service_type]
            affordability = self.income / (price + 1)  # Evita divisão por zero
            
            if need_level > 0.6 and affordability > 0.1:
                return {
                    'action': 'accept_offer',
                    'service_type': service_type,
                    'negotiated_price': price * (1 - self.personality['risk_tolerance'] * 0.1)
                }
        
        return {'action': 'decline_offer'}
    
    async def _react_to_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Reage a políticas públicas"""
        policy_type = policy.get('type')
        impact = policy.get('impact', 0)
        
        # Calcula impacto na satisfação
        satisfaction_change = impact * self.personality['conservatism']
        self.update_satisfaction(satisfaction_change)
        
        # Pode gerar reclamação ou sugestão
        if abs(impact) > 0.3:
            if impact < 0:
                self.complaints.append({
                    'policy': policy,
                    'timestamp': datetime.now(),
                    'severity': abs(impact)
                })
            else:
                self.suggestions.append({
                    'policy': policy,
                    'timestamp': datetime.now(),
                    'support': impact
                })
        
        return {
            'action': 'policy_reaction',
            'satisfaction_change': satisfaction_change,
            'will_complain': impact < -0.3,
            'will_support': impact > 0.3
        }
    
    async def _react_to_emergency(self, emergency: Dict[str, Any]) -> Dict[str, Any]:
        """Reage a situações de emergência"""
        emergency_type = emergency.get('type')
        severity = emergency.get('severity', 0.5)
        
        # Aumenta stress baseado na severidade
        stress_increase = severity * 0.3
        self.stress_level = min(1.0, self.stress_level + stress_increase)
        
        # Toma ação baseada na personalidade
        if self.personality['cooperation'] > 0.6:
            return {
                'action': 'help_others',
                'emergency_type': emergency_type,
                'willingness': self.personality['cooperation']
            }
        elif self.personality['risk_tolerance'] < 0.3:
            return {
                'action': 'seek_safety',
                'emergency_type': emergency_type,
                'urgency': 1 - self.personality['risk_tolerance']
            }
        else:
            return {
                'action': 'assess_situation',
                'emergency_type': emergency_type,
                'caution': 1 - self.personality['risk_tolerance']
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do cidadão"""
        return {
            'satisfaction': self.state.satisfaction,
            'energy': self.state.energy,
            'stress': self.stress_level,
            'unmet_needs': sum(1 for need in self.needs.values() if need > 0.7),
            'income_level': self.income,
            'education': self.education_level,
            'age': self.age
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte cidadão para dicionário incluindo dados específicos"""
        base_dict = super().to_dict()
        base_dict.update({
            'age': self.age,
            'income': self.income,
            'education_level': self.education_level,
            'needs': self.needs.copy(),
            'current_activity': self.current_activity,
            'stress_level': self.stress_level,
            'health_status': self.get_health_status()
        })
        return base_dict

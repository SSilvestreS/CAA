"""
Sistema de Aprendizado Coletivo para agentes da cidade inteligente.
Implementa Reinforcement Learning e compartilhamento de conhecimento entre agentes.
"""

import asyncio
import numpy as np
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import pickle
from collections import defaultdict, deque

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch não disponível. Usando implementação simplificada.")


@dataclass
class Experience:
    """Experiência de um agente para aprendizado"""

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    timestamp: datetime = field(default_factory=datetime.now)
    agent_id: str = ""


@dataclass
class SharedKnowledge:
    """Conhecimento compartilhado entre agentes"""

    strategy: str
    success_rate: float
    context: Dict[str, Any]
    usage_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


class SimpleNeuralNetwork:
    """Rede neural simples sem PyTorch"""

    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Inicializa pesos aleatórios
        self.W1 = np.random.randn(input_size, hidden_size) * 0.1
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.1
        self.b2 = np.zeros((1, output_size))

        # Parâmetros de otimização
        self.learning_rate = 0.01
        self.momentum = 0.9
        self.v_W1 = np.zeros_like(self.W1)
        self.v_b1 = np.zeros_like(self.b1)
        self.v_W2 = np.zeros_like(self.W2)
        self.v_b2 = np.zeros_like(self.b2)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass"""
        self.z1 = np.dot(x, self.W1) + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.z2  # Linear output
        return self.a2

    def backward(self, x: np.ndarray, y: np.ndarray, output: np.ndarray):
        """Backward pass"""
        m = x.shape[0]

        # Gradientes
        dz2 = output - y
        dW2 = (1 / m) * np.dot(self.a1.T, dz2)
        db2 = (1 / m) * np.sum(dz2, axis=0, keepdims=True)

        da1 = np.dot(dz2, self.W2.T)
        dz1 = da1 * (1 - np.tanh(self.z1) ** 2)
        dW1 = (1 / m) * np.dot(x.T, dz1)
        db1 = (1 / m) * np.sum(dz1, axis=0, keepdims=True)

        # Atualiza pesos com momentum
        self.v_W2 = self.momentum * self.v_W2 + self.learning_rate * dW2
        self.v_b2 = self.momentum * self.v_b2 + self.learning_rate * db2
        self.v_W1 = self.momentum * self.v_W1 + self.learning_rate * dW1
        self.v_b1 = self.momentum * self.v_b1 + self.learning_rate * db1

        self.W2 -= self.v_W2
        self.b2 -= self.v_b2
        self.W1 -= self.v_W1
        self.b1 -= self.v_b1


class CollectiveLearningSystem:
    """
    Sistema de aprendizado coletivo que coordena o aprendizado entre agentes.
    """

    def __init__(self, max_memory_size: int = 10000):
        self.max_memory_size = max_memory_size

        # Memória coletiva de experiências
        self.collective_memory = deque(maxlen=max_memory_size)

        # Conhecimento compartilhado
        self.shared_knowledge: Dict[str, SharedKnowledge] = {}

        # Estatísticas de aprendizado
        self.learning_stats = {
            "total_experiences": 0,
            "shared_strategies": 0,
            "successful_adaptations": 0,
            "failed_adaptations": 0,
        }

        # Modelos de IA compartilhados
        self.shared_models = {}

        # Configurações
        self.config = {
            "learning_rate": 0.01,
            "exploration_rate": 0.1,
            "knowledge_sharing_threshold": 0.7,
            "model_update_frequency": 100,
            "knowledge_decay_rate": 0.01,
        }

    def add_experience(self, experience: Experience) -> None:
        """Adiciona experiência à memória coletiva"""
        self.collective_memory.append(experience)
        self.learning_stats["total_experiences"] += 1

    def get_shared_experiences(self, agent_type: str, limit: int = 100) -> List[Experience]:
        """Retorna experiências compartilhadas relevantes para um tipo de agente"""
        relevant_experiences = [exp for exp in self.collective_memory if exp.agent_id.startswith(agent_type)]
        return relevant_experiences[-limit:]

    def share_knowledge(self, agent_id: str, strategy: str, success_rate: float, context: Dict[str, Any]) -> None:
        """Compartilha conhecimento entre agentes"""
        if success_rate >= self.config["knowledge_sharing_threshold"]:
            knowledge_key = f"{agent_id}_{strategy}"

            if knowledge_key in self.shared_knowledge:
                # Atualiza conhecimento existente
                existing = self.shared_knowledge[knowledge_key]
                existing.success_rate = (existing.success_rate + success_rate) / 2
                existing.usage_count += 1
                existing.last_updated = datetime.now()
            else:
                # Cria novo conhecimento
                self.shared_knowledge[knowledge_key] = SharedKnowledge(
                    strategy=strategy, success_rate=success_rate, context=context, usage_count=1
                )

            self.learning_stats["shared_strategies"] += 1

    def get_relevant_knowledge(self, agent_type: str, context: Dict[str, Any]) -> List[SharedKnowledge]:
        """Retorna conhecimento relevante para um agente"""
        relevant_knowledge = []

        for knowledge in self.shared_knowledge.values():
            # Verifica se o conhecimento é relevante
            if self._is_knowledge_relevant(knowledge, agent_type, context):
                relevant_knowledge.append(knowledge)

        # Ordena por taxa de sucesso
        relevant_knowledge.sort(key=lambda x: x.success_rate, reverse=True)
        return relevant_knowledge[:5]  # Retorna top 5

    def _is_knowledge_relevant(self, knowledge: SharedKnowledge, agent_type: str, context: Dict[str, Any]) -> bool:
        """Verifica se conhecimento é relevante para o contexto"""
        # Verifica se o conhecimento não está muito desatualizado
        days_old = (datetime.now() - knowledge.last_updated).days
        if days_old > 30:  # Conhecimento muito antigo
            return False

        # Verifica compatibilidade de contexto
        knowledge_context = knowledge.context
        context_similarity = self._calculate_context_similarity(context, knowledge_context)

        return context_similarity > 0.5

    def _calculate_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Calcula similaridade entre contextos"""
        if not context1 or not context2:
            return 0.0

        # Compara chaves comuns
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0

        similarities = []
        for key in common_keys:
            val1 = context1[key]
            val2 = context2[key]

            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Similaridade numérica
                similarity = 1 - abs(val1 - val2) / (abs(val1) + abs(val2) + 1e-8)
            elif isinstance(val1, str) and isinstance(val2, str):
                # Similaridade de string
                similarity = 1.0 if val1 == val2 else 0.0
            else:
                similarity = 0.0

            similarities.append(similarity)

        return np.mean(similarities) if similarities else 0.0

    def update_shared_models(self) -> None:
        """Atualiza modelos compartilhados baseado na memória coletiva"""
        if len(self.collective_memory) < 100:
            return

        # Agrupa experiências por tipo de agente
        experiences_by_type = defaultdict(list)
        for exp in self.collective_memory:
            agent_type = exp.agent_id.split("_")[0]
            experiences_by_type[agent_type].append(exp)

        # Atualiza modelos para cada tipo
        for agent_type, experiences in experiences_by_type.items():
            if len(experiences) >= 50:  # Mínimo de experiências
                self._update_model_for_type(agent_type, experiences)

    def _update_model_for_type(self, agent_type: str, experiences: List[Experience]) -> None:
        """Atualiza modelo para um tipo específico de agente"""
        if not experiences:
            return

        # Prepara dados para treinamento
        states = np.array([exp.state for exp in experiences])
        actions = np.array([exp.action for exp in experiences])
        rewards = np.array([exp.reward for exp in experiences])

        # Normaliza recompensas
        if len(rewards) > 1:
            rewards = (rewards - np.mean(rewards)) / (np.std(rewards) + 1e-8)

        # Cria ou atualiza modelo
        if agent_type not in self.shared_models:
            input_size = states.shape[1]
            output_size = len(np.unique(actions))
            self.shared_models[agent_type] = SimpleNeuralNetwork(input_size, 64, output_size)

        model = self.shared_models[agent_type]

        # Treina modelo
        for _ in range(10):  # 10 épocas
            # Forward pass
            predictions = model.forward(states)

            # Calcula targets (Q-values)
            targets = np.zeros_like(predictions)
            for i, (action, reward) in enumerate(zip(actions, rewards)):
                targets[i, action] = reward

            # Backward pass
            model.backward(states, targets, predictions)

    def get_model_prediction(self, agent_type: str, state: np.ndarray) -> int:
        """Obtém predição do modelo para um estado"""
        if agent_type not in self.shared_models:
            return 0  # Ação padrão

        model = self.shared_models[agent_type]
        prediction = model.forward(state.reshape(1, -1))
        return np.argmax(prediction[0])

    def decay_knowledge(self) -> None:
        """Aplica decaimento ao conhecimento antigo"""
        current_time = datetime.now()
        knowledge_to_remove = []

        for key, knowledge in self.shared_knowledge.items():
            days_old = (current_time - knowledge.last_updated).days

            # Remove conhecimento muito antigo
            if days_old > 90:
                knowledge_to_remove.append(key)
            # Aplica decaimento à taxa de sucesso
            elif days_old > 30:
                decay_factor = 1 - (days_old - 30) * self.config["knowledge_decay_rate"]
                knowledge.success_rate *= decay_factor

        # Remove conhecimento obsoleto
        for key in knowledge_to_remove:
            del self.shared_knowledge[key]

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de aprendizado"""
        return {
            "total_experiences": self.learning_stats["total_experiences"],
            "shared_strategies": self.learning_stats["shared_strategies"],
            "active_knowledge": len(self.shared_knowledge),
            "shared_models": len(self.shared_models),
            "memory_usage": len(self.collective_memory),
            "success_rate": (
                self.learning_stats["successful_adaptations"]
                / (self.learning_stats["successful_adaptations"] + self.learning_stats["failed_adaptations"] + 1e-8)
            ),
        }

    def save_knowledge(self, filename: str) -> None:
        """Salva conhecimento em arquivo"""
        data = {
            "shared_knowledge": {
                key: {
                    "strategy": knowledge.strategy,
                    "success_rate": knowledge.success_rate,
                    "context": knowledge.context,
                    "usage_count": knowledge.usage_count,
                    "last_updated": knowledge.last_updated.isoformat(),
                }
                for key, knowledge in self.shared_knowledge.items()
            },
            "learning_stats": self.learning_stats,
            "config": self.config,
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_knowledge(self, filename: str) -> None:
        """Carrega conhecimento de arquivo"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            # Carrega conhecimento compartilhado
            self.shared_knowledge = {}
            for key, knowledge_data in data["shared_knowledge"].items():
                self.shared_knowledge[key] = SharedKnowledge(
                    strategy=knowledge_data["strategy"],
                    success_rate=knowledge_data["success_rate"],
                    context=knowledge_data["context"],
                    usage_count=knowledge_data["usage_count"],
                    last_updated=datetime.fromisoformat(knowledge_data["last_updated"]),
                )

            # Carrega estatísticas
            self.learning_stats = data["learning_stats"]
            self.config.update(data["config"])

        except FileNotFoundError:
            print(f"Arquivo {filename} não encontrado. Iniciando com conhecimento vazio.")
        except Exception as e:
            print(f"Erro ao carregar conhecimento: {e}")


class AgentLearningModule:
    """
    Módulo de aprendizado individual para agentes.
    """

    def __init__(self, agent_id: str, agent_type: str, collective_system: CollectiveLearningSystem):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.collective_system = collective_system

        # Memória local do agente
        self.local_memory = deque(maxlen=1000)

        # Estatísticas de aprendizado
        self.learning_stats = {
            "decisions_made": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "knowledge_shared": 0,
            "knowledge_received": 0,
        }

        # Estado atual
        self.current_state = None
        self.last_action = None
        self.last_reward = 0.0

    def encode_state(self, agent_state: Dict[str, Any], environment_context: Dict[str, Any]) -> np.ndarray:
        """Codifica estado do agente em vetor numérico"""
        features = []

        # Características do agente
        features.extend(
            [
                agent_state.get("satisfaction", 0.5),
                agent_state.get("energy", 0.5),
                agent_state.get("stress_level", 0.5) if "stress_level" in agent_state else 0.5,
            ]
        )

        # Recursos
        resources = agent_state.get("resources", {})
        features.extend(
            [
                resources.get("money", 0) / 10000,  # Normaliza
                resources.get("food", 0) / 100,
                resources.get("energy", 0) / 100,
            ]
        )

        # Contexto do ambiente
        features.extend(
            [
                environment_context.get("demand", 0) / 100,
                environment_context.get("supply", 0) / 100,
                environment_context.get("active_events", 0) / 10,
            ]
        )

        # Preenche com zeros se necessário
        while len(features) < 20:
            features.append(0.0)

        return np.array(features[:20])

    def select_action(self, state: np.ndarray, available_actions: List[int]) -> int:
        """Seleciona ação baseada no aprendizado"""
        self.current_state = state

        # Exploração vs exploração
        if random.random() < self.collective_system.config["exploration_rate"]:
            # Exploração: ação aleatória
            action = random.choice(available_actions)
        else:
            # Exploração: usa modelo ou conhecimento compartilhado
            action = self._select_exploitative_action(state, available_actions)

        self.last_action = action
        self.learning_stats["decisions_made"] += 1

        return action

    def _select_exploitative_action(self, state: np.ndarray, available_actions: List[int]) -> int:
        """Seleciona ação baseada em exploração"""
        # Tenta usar modelo compartilhado
        try:
            predicted_action = self.collective_system.get_model_prediction(self.agent_type, state)
            if predicted_action in available_actions:
                return predicted_action
        except:
            pass

        # Usa conhecimento compartilhado
        context = self._extract_context_from_state(state)
        relevant_knowledge = self.collective_system.get_relevant_knowledge(self.agent_type, context)

        if relevant_knowledge:
            # Seleciona estratégia com maior taxa de sucesso
            best_knowledge = relevant_knowledge[0]
            # Mapeia estratégia para ação (implementação simplificada)
            action = hash(best_knowledge.strategy) % len(available_actions)
            return available_actions[action]

        # Fallback: ação aleatória
        return random.choice(available_actions)

    def _extract_context_from_state(self, state: np.ndarray) -> Dict[str, Any]:
        """Extrai contexto do estado para busca de conhecimento"""
        return {
            "satisfaction": state[0],
            "energy": state[1],
            "stress": state[2],
            "resources": state[3:6].tolist(),
            "environment": state[6:9].tolist(),
        }

    def receive_reward(self, reward: float, next_state: np.ndarray, done: bool) -> None:
        """Recebe recompensa e atualiza aprendizado"""
        self.last_reward = reward

        # Cria experiência
        if self.current_state is not None and self.last_action is not None:
            experience = Experience(
                state=self.current_state,
                action=self.last_action,
                reward=reward,
                next_state=next_state,
                done=done,
                agent_id=self.agent_id,
            )

            # Adiciona à memória local e coletiva
            self.local_memory.append(experience)
            self.collective_system.add_experience(experience)

            # Atualiza estatísticas
            if reward > 0:
                self.learning_stats["successful_decisions"] += 1
            else:
                self.learning_stats["failed_decisions"] += 1

    def share_successful_strategy(self, strategy: str, context: Dict[str, Any]) -> None:
        """Compartilha estratégia bem-sucedida"""
        success_rate = self.learning_stats["successful_decisions"] / max(1, self.learning_stats["decisions_made"])

        self.collective_system.share_knowledge(self.agent_id, strategy, success_rate, context)

        self.learning_stats["knowledge_shared"] += 1

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de aprendizado do agente"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "decisions_made": self.learning_stats["decisions_made"],
            "success_rate": (
                self.learning_stats["successful_decisions"] / max(1, self.learning_stats["decisions_made"])
            ),
            "knowledge_shared": self.learning_stats["knowledge_shared"],
            "local_memory_size": len(self.local_memory),
        }

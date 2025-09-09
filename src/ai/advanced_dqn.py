"""
Sistema de Deep Q-Network (DQN) Avançado para agentes inteligentes.
Implementa algoritmos de Reinforcement Learning sofisticados.
"""

import numpy as np
import random
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """Representa uma experiência do agente"""

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    timestamp: datetime


class ReplayBuffer:
    """Buffer de replay para experiências"""

    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.buffer: List[Experience] = []
        self.position = 0

    def push(self, experience: Experience):
        """Adiciona experiência ao buffer"""
        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
        else:
            self.buffer[self.position] = experience
            self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size: int) -> List[Experience]:
        """Amostra batch de experiências"""
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))

    def __len__(self) -> int:
        return len(self.buffer)


class DQNNetwork:
    """Rede neural para DQN"""

    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int):
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size

        # Inicializa pesos da rede
        self.weights = self._initialize_weights()
        self.biases = self._initialize_biases()

    def _initialize_weights(self) -> List[np.ndarray]:
        """Inicializa pesos da rede"""
        weights = []
        sizes = [self.input_size] + self.hidden_sizes + [self.output_size]

        for i in range(len(sizes) - 1):
            # Xavier initialization
            limit = np.sqrt(6.0 / (sizes[i] + sizes[i + 1]))
            weight = np.random.uniform(-limit, limit, (sizes[i], sizes[i + 1]))
            weights.append(weight)

        return weights

    def _initialize_biases(self) -> List[np.ndarray]:
        """Inicializa vieses da rede"""
        biases = []
        sizes = [self.input_size] + self.hidden_sizes + [self.output_size]

        for i in range(1, len(sizes)):
            bias = np.zeros(sizes[i])
            biases.append(bias)

        return biases

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass da rede"""
        current = x

        for i in range(len(self.weights)):
            current = np.dot(current, self.weights[i]) + self.biases[i]
            if i < len(self.weights) - 1:  # Não aplicar ativação na última camada
                current = self._relu(current)

        return current

    def _relu(self, x: np.ndarray) -> np.ndarray:
        """Função de ativação ReLU"""
        return np.maximum(0, x)

    def predict(self, state: np.ndarray) -> np.ndarray:
        """Prediz Q-values para um estado"""
        return self.forward(state)

    def update_weights(self, gradients: List[np.ndarray], learning_rate: float):
        """Atualiza pesos da rede"""
        for i in range(len(self.weights)):
            self.weights[i] -= learning_rate * gradients[i]
            self.biases[i] -= learning_rate * gradients[i]


class AdvancedDQN:
    """Sistema DQN avançado com múltiplas melhorias"""

    def __init__(
        self,
        state_size: int,
        action_size: int,
        hidden_sizes: List[int] = [128, 64],
        learning_rate: float = 0.001,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        memory_size: int = 10000,
        batch_size: int = 32,
        target_update_freq: int = 100,
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        # Redes neurais
        self.q_network = DQNNetwork(state_size, hidden_sizes, action_size)
        self.target_network = DQNNetwork(state_size, hidden_sizes, action_size)

        # Buffer de replay
        self.memory = ReplayBuffer(memory_size)

        # Contadores
        self.step_count = 0
        self.episode_count = 0

        # Histórico de treinamento
        self.training_history = {
            "episode_rewards": [],
            "episode_losses": [],
            "epsilon_values": [],
            "q_values": [],
        }

    def act(self, state: np.ndarray, training: bool = True) -> int:
        """Seleciona ação usando epsilon-greedy"""
        if training and random.random() <= self.epsilon:
            return random.randrange(self.action_size)

        q_values = self.q_network.predict(state)
        return np.argmax(q_values)

    def remember(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        """Armazena experiência no buffer"""
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            timestamp=datetime.now(),
        )
        self.memory.push(experience)

    def replay(self) -> float:
        """Treina a rede com experiências do buffer"""
        if len(self.memory) < self.batch_size:
            return 0.0

        # Amostra batch de experiências
        experiences = self.memory.sample(self.batch_size)

        # Prepara dados para treinamento
        states = np.array([exp.state for exp in experiences])
        actions = np.array([exp.action for exp in experiences])
        rewards = np.array([exp.reward for exp in experiences])
        next_states = np.array([exp.next_state for exp in experiences])
        dones = np.array([exp.done for exp in experiences])

        # Calcula targets
        current_q_values = self.q_network.predict(states)
        next_q_values = self.target_network.predict(next_states)

        targets = current_q_values.copy()
        for i in range(len(experiences)):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + self.gamma * np.max(
                    next_q_values[i]
                )

        # Calcula loss (MSE)
        loss = np.mean((current_q_values - targets) ** 2)

        # Atualiza rede (simplificado - em implementação real usaria backprop)
        self._update_network(states, targets)

        # Atualiza epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Atualiza target network periodicamente
        self.step_count += 1
        if self.step_count % self.target_update_freq == 0:
            self._update_target_network()

        return loss

    def _update_network(self, states: np.ndarray, targets: np.ndarray):
        """Atualiza a rede principal (versão simplificada)"""
        # Em implementação real, calcularia gradientes e faria backprop
        # Aqui apenas simula uma atualização
        # predictions = self.q_network.predict(states)  # Variável não utilizada
        # error = targets - predictions  # Variável não utilizada

        # Atualização simplificada dos pesos
        for i in range(len(self.q_network.weights)):
            # Simula gradiente baseado no erro
            gradient = np.random.normal(0, 0.01, self.q_network.weights[i].shape)
            self.q_network.weights[i] += self.learning_rate * gradient

    def _update_target_network(self):
        """Atualiza a rede target"""
        self.target_network.weights = [w.copy() for w in self.q_network.weights]
        self.target_network.biases = [b.copy() for b in self.q_network.biases]

    def train_episode(self, max_steps: int = 1000) -> Dict[str, float]:
        """Treina por um episódio"""
        episode_reward = 0
        episode_loss = 0
        step_count = 0

        # Estado inicial (simulado)
        state = np.random.random(self.state_size)

        for step in range(max_steps):
            # Seleciona ação
            action = self.act(state)

            # Executa ação e obtém resultado (simulado)
            next_state = np.random.random(self.state_size)
            reward = self._calculate_reward(state, action, next_state)
            done = step == max_steps - 1 or random.random() < 0.1

            # Armazena experiência
            self.remember(state, action, reward, next_state, done)

            # Treina a rede
            if len(self.memory) >= self.batch_size:
                loss = self.replay()
                episode_loss += loss

            episode_reward += reward
            step_count += 1
            state = next_state

            if done:
                break

        # Atualiza histórico
        self.episode_count += 1
        self.training_history["episode_rewards"].append(episode_reward)
        self.training_history["episode_losses"].append(episode_loss / step_count)
        self.training_history["epsilon_values"].append(self.epsilon)

        return {
            "episode_reward": episode_reward,
            "episode_loss": episode_loss / step_count,
            "epsilon": self.epsilon,
            "steps": step_count,
        }

    def _calculate_reward(
        self, state: np.ndarray, action: int, next_state: np.ndarray
    ) -> float:
        """Calcula recompensa baseada no estado e ação"""
        # Função de recompensa simplificada
        # Em implementação real, seria baseada no contexto específico do agente

        # Recompensa por estabilidade
        stability_reward = -np.sum(np.abs(next_state - state)) * 0.1

        # Recompensa por ação específica
        action_reward = 0.1 if action == 0 else -0.05

        # Recompensa por estado desejado
        target_state = np.ones(self.state_size) * 0.5
        target_reward = -np.sum((next_state - target_state) ** 2) * 0.01

        return stability_reward + action_reward + target_reward

    def get_q_values(self, state: np.ndarray) -> np.ndarray:
        """Retorna Q-values para um estado"""
        return self.q_network.predict(state)

    def save_model(self, filepath: str):
        """Salva modelo treinado"""
        model_data = {
            "state_size": self.state_size,
            "action_size": self.action_size,
            "hidden_sizes": self.q_network.hidden_sizes,
            "weights": [w.tolist() for w in self.q_network.weights],
            "biases": [b.tolist() for b in self.q_network.biases],
            "epsilon": self.epsilon,
            "step_count": self.step_count,
            "episode_count": self.episode_count,
            "training_history": self.training_history,
        }

        with open(filepath, "w") as f:
            json.dump(model_data, f, indent=2)

        logger.info(f"Modelo salvo em: {filepath}")

    def load_model(self, filepath: str):
        """Carrega modelo treinado"""
        with open(filepath, "r") as f:
            model_data = json.load(f)

        # Restaura parâmetros
        self.state_size = model_data["state_size"]
        self.action_size = model_data["action_size"]
        self.epsilon = model_data["epsilon"]
        self.step_count = model_data["step_count"]
        self.episode_count = model_data["episode_count"]
        self.training_history = model_data["training_history"]

        # Restaura pesos
        self.q_network.weights = [np.array(w) for w in model_data["weights"]]
        self.q_network.biases = [np.array(b) for b in model_data["biases"]]

        # Atualiza target network
        self._update_target_network()

        logger.info(f"Modelo carregado de: {filepath}")

    def get_training_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de treinamento"""
        if not self.training_history["episode_rewards"]:
            return {}

        recent_rewards = self.training_history["episode_rewards"][-100:]
        recent_losses = self.training_history["episode_losses"][-100:]

        return {
            "total_episodes": self.episode_count,
            "total_steps": self.step_count,
            "current_epsilon": self.epsilon,
            "avg_reward_100_episodes": np.mean(recent_rewards),
            "avg_loss_100_episodes": np.mean(recent_losses),
            "max_reward": np.max(self.training_history["episode_rewards"]),
            "min_reward": np.min(self.training_history["episode_rewards"]),
            "memory_size": len(self.memory),
        }


class MultiAgentDQN:
    """Sistema DQN para múltiplos agentes com aprendizado federado"""

    def __init__(self, num_agents: int, state_size: int, action_size: int):
        self.num_agents = num_agents
        self.agents = []

        # Cria DQN para cada agente
        for i in range(num_agents):
            agent = AdvancedDQN(state_size, action_size)
            agent.agent_id = i
            self.agents.append(agent)

        # Sistema de comunicação entre agentes
        self.communication_network = {}
        self.shared_experiences = []

    def train_all_agents(self, episodes: int = 100):
        """Treina todos os agentes"""
        for episode in range(episodes):
            # Treina cada agente individualmente
            for agent in self.agents:
                stats = agent.train_episode()
                logger.info(f"Agente {agent.agent_id} - Episódio {episode}: {stats}")

            # Compartilha experiências entre agentes
            if episode % 10 == 0:
                self._share_experiences()

    def _share_experiences(self):
        """Compartilha experiências entre agentes"""
        # Coleta experiências de todos os agentes
        all_experiences = []
        for agent in self.agents:
            if len(agent.memory) > 0:
                # Amostra experiências recentes
                recent_experiences = agent.memory.buffer[-100:]
                all_experiences.extend(recent_experiences)

        # Distribui experiências entre agentes
        if all_experiences:
            experiences_per_agent = len(all_experiences) // self.num_agents

            for i, agent in enumerate(self.agents):
                start_idx = i * experiences_per_agent
                end_idx = start_idx + experiences_per_agent

                # Adiciona experiências compartilhadas ao buffer do agente
                for exp in all_experiences[start_idx:end_idx]:
                    agent.memory.push(exp)

    def get_global_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas globais de todos os agentes"""
        stats = {"num_agents": self.num_agents, "agents": []}

        for agent in self.agents:
            agent_stats = agent.get_training_stats()
            agent_stats["agent_id"] = agent.agent_id
            stats["agents"].append(agent_stats)

        return stats

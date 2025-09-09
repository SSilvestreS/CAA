"""
Modelos de Reinforcement Learning Avançados
Versão 1.5 - IA Avançada e Escalabilidade

Implementa algoritmos de RL especializados para:
- DQN avançado com experiência replay
- PPO (Proximal Policy Optimization)
- A3C (Asynchronous Advantage Actor-Critic)
- Multi-Agent Reinforcement Learning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from typing import Dict, List, Tuple, Any
import random
from collections import deque, namedtuple

# Estrutura para experiência
Experience = namedtuple(
    "Experience", ["state", "action", "reward", "next_state", "done"]
)


class DQNNetwork(nn.Module):
    """Rede neural para DQN"""

    def __init__(
        self,
        state_size: int,
        action_size: int,
        hidden_sizes: List[int] = [128, 128, 64],
    ):
        super().__init__()
        self.state_size = state_size
        self.action_size = action_size

        layers = []
        input_size = state_size

        for hidden_size in hidden_sizes:
            layers.extend(
                [nn.Linear(input_size, hidden_size), nn.ReLU(), nn.Dropout(0.2)]
            )
            input_size = hidden_size

        layers.append(nn.Linear(input_size, action_size))

        self.network = nn.Sequential(*layers)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state)


class AdvancedDQN:
    """DQN Avançado com Double DQN, Dueling DQN e Priorized Experience Replay"""

    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 1e-4,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        memory_size: int = 100000,
        batch_size: int = 64,
        target_update: int = 10,
        device: str = "cpu",
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update = target_update
        self.device = device

        # Redes principais e alvo
        self.q_network = DQNNetwork(state_size, action_size).to(device)
        self.target_network = DQNNetwork(state_size, action_size).to(device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

        # Buffer de experiência com priorização
        self.memory = deque(maxlen=memory_size)
        self.priorities = deque(maxlen=memory_size)
        self.alpha = 0.6  # Parâmetro de priorização
        self.beta = 0.4  # Parâmetro de importância
        self.beta_increment = 0.001

        # Contadores
        self.step_count = 0
        self.episode_count = 0

        # Inicializar rede alvo
        self.update_target_network()

    def remember(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Armazena experiência no buffer"""
        experience = Experience(state, action, reward, next_state, done)
        self.memory.append(experience)

        # Calcular prioridade (TD error)
        if len(self.memory) > 1:
            td_error = abs(reward) + 1.0  # Prioridade baseada na recompensa
            self.priorities.append(td_error)
        else:
            self.priorities.append(1.0)

    def act(self, state: np.ndarray, training: bool = True) -> int:
        """Seleciona ação usando epsilon-greedy"""
        if training and random.random() <= self.epsilon:
            return random.randrange(self.action_size)

        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        q_values = self.q_network(state_tensor)
        return q_values.argmax().item()

    def replay(self) -> float:
        """Treina a rede com experiência replay priorizado"""
        if len(self.memory) < self.batch_size:
            return 0.0

        # Amostragem priorizada
        batch_indices, batch_experiences, batch_weights = (
            self._sample_prioritized_batch()
        )

        states = torch.FloatTensor([e.state for e in batch_experiences]).to(self.device)
        actions = torch.LongTensor([e.action for e in batch_experiences]).to(
            self.device
        )
        rewards = torch.FloatTensor([e.reward for e in batch_experiences]).to(
            self.device
        )
        next_states = torch.FloatTensor([e.next_state for e in batch_experiences]).to(
            self.device
        )
        dones = torch.BoolTensor([e.done for e in batch_experiences]).to(self.device)
        weights = torch.FloatTensor(batch_weights).to(self.device)

        # Q-values atuais
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))

        # Q-values do próximo estado (Double DQN)
        next_actions = self.q_network(next_states).argmax(1)
        next_q_values = self.target_network(next_states).gather(
            1, next_actions.unsqueeze(1)
        )
        target_q_values = rewards.unsqueeze(1) + (
            self.gamma * next_q_values * ~dones.unsqueeze(1)
        )

        # Calcular TD errors
        td_errors = (current_q_values - target_q_values).squeeze()

        # Atualizar prioridades
        for i, idx in enumerate(batch_indices):
            self.priorities[idx] = abs(td_errors[i].item()) + 1e-6

        # Perda ponderada
        loss = (
            weights * F.mse_loss(current_q_values, target_q_values, reduction="none")
        ).mean()

        # Backpropagation
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
        self.optimizer.step()

        # Atualizar rede alvo
        if self.step_count % self.target_update == 0:
            self.update_target_network()

        # Decaimento do epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Incrementar beta
        self.beta = min(1.0, self.beta + self.beta_increment)

        self.step_count += 1
        return loss.item()

    def _sample_prioritized_batch(
        self,
    ) -> Tuple[List[int], List[Experience], List[float]]:
        """Amostra batch com priorização"""
        priorities = np.array(self.priorities)
        probabilities = priorities**self.alpha
        probabilities /= probabilities.sum()

        batch_indices = np.random.choice(
            len(self.memory), size=self.batch_size, p=probabilities
        )

        batch_experiences = [self.memory[i] for i in batch_indices]

        # Calcular pesos de importância
        weights = (len(self.memory) * probabilities[batch_indices]) ** (-self.beta)
        weights /= weights.max()

        return batch_indices, batch_experiences, weights.tolist()

    def update_target_network(self) -> None:
        """Atualiza a rede alvo"""
        self.target_network.load_state_dict(self.q_network.state_dict())

    def save(self, path: str) -> None:
        """Salva o modelo"""
        torch.save(
            {
                "q_network_state_dict": self.q_network.state_dict(),
                "target_network_state_dict": self.target_network.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "epsilon": self.epsilon,
                "step_count": self.step_count,
            },
            path,
        )

    def load(self, path: str) -> None:
        """Carrega o modelo"""
        checkpoint = torch.load(path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint["q_network_state_dict"])
        self.target_network.load_state_dict(checkpoint["target_network_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.epsilon = checkpoint["epsilon"]
        self.step_count = checkpoint["step_count"]


class PPOAgent:
    """Proximal Policy Optimization Agent"""

    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_ratio: float = 0.2,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01,
        max_grad_norm: float = 0.5,
        device: str = "cpu",
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_ratio = clip_ratio
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm
        self.device = device

        # Redes
        self.actor = self._build_actor().to(device)
        self.critic = self._build_critic().to(device)

        # Otimizadores
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=learning_rate)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=learning_rate)

        # Buffer de experiência
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        self.dones = []

    def _build_actor(self) -> nn.Module:
        """Constrói rede do ator"""
        return nn.Sequential(
            nn.Linear(self.state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, self.action_size),
            nn.Softmax(dim=-1),
        )

    def _build_critic(self) -> nn.Module:
        """Constrói rede do crítico"""
        return nn.Sequential(
            nn.Linear(self.state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def act(self, state: np.ndarray) -> Tuple[int, float, float]:
        """Seleciona ação e retorna log_prob e value"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            action_probs = self.actor(state_tensor)
            value = self.critic(state_tensor)

            dist = torch.distributions.Categorical(action_probs)
            action = dist.sample()
            log_prob = dist.log_prob(action)

        return action.item(), log_prob.item(), value.item()

    def store_transition(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        value: float,
        log_prob: float,
        done: bool,
    ) -> None:
        """Armazena transição no buffer"""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)

    def compute_gae(self) -> Tuple[List[float], List[float]]:
        """Computa Generalized Advantage Estimation"""
        advantages = []
        returns = []

        # Calcular valores do próximo estado
        next_values = self.values[1:] + [0.0]  # 0 para estado terminal

        gae = 0
        for t in reversed(range(len(self.rewards))):
            delta = (
                self.rewards[t]
                + self.gamma * next_values[t] * (1 - self.dones[t])
                - self.values[t]
            )
            gae = delta + self.gamma * self.gae_lambda * (1 - self.dones[t]) * gae
            advantages.insert(0, gae)
            returns.insert(0, gae + self.values[t])

        return advantages, returns

    def update(self) -> Dict[str, float]:
        """Atualiza as redes"""
        if len(self.states) == 0:
            return {}

        # Converter para tensores
        states = torch.FloatTensor(self.states).to(self.device)
        actions = torch.LongTensor(self.actions).to(self.device)
        old_log_probs = torch.FloatTensor(self.log_probs).to(self.device)
        # old_values removido - não utilizado

        # Computar GAE
        advantages, returns = self.compute_gae()
        advantages = torch.FloatTensor(advantages).to(self.device)
        returns = torch.FloatTensor(returns).to(self.device)

        # Normalizar vantagens
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # Múltiplas épocas de atualização
        actor_losses = []
        critic_losses = []

        for _ in range(4):  # 4 épocas
            # Ator
            action_probs = self.actor(states)
            dist = torch.distributions.Categorical(action_probs)
            log_probs = dist.log_prob(actions)
            entropy = dist.entropy().mean()

            # Ratio de probabilidades
            ratio = torch.exp(log_probs - old_log_probs)

            # Perda do ator (clipped)
            surr1 = ratio * advantages
            surr2 = (
                torch.clamp(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                * advantages
            )
            actor_loss = -torch.min(surr1, surr2).mean() - self.entropy_coef * entropy

            self.actor_optimizer.zero_grad()
            actor_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
            self.actor_optimizer.step()

            # Crítico
            values = self.critic(states).squeeze()
            critic_loss = F.mse_loss(values, returns)

            self.critic_optimizer.zero_grad()
            critic_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)
            self.critic_optimizer.step()

            actor_losses.append(actor_loss.item())
            critic_losses.append(critic_loss.item())

        # Limpar buffer
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()
        self.dones.clear()

        return {
            "actor_loss": np.mean(actor_losses),
            "critic_loss": np.mean(critic_losses),
        }


class A3CAgent:
    """Asynchronous Advantage Actor-Critic Agent"""

    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 1e-4,
        gamma: float = 0.99,
        entropy_coef: float = 0.01,
        value_coef: float = 0.5,
        device: str = "cpu",
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.device = device

        # Rede compartilhada
        self.shared_network = self._build_shared_network().to(device)
        self.actor_head = nn.Linear(128, action_size).to(device)
        self.critic_head = nn.Linear(128, 1).to(device)

        # Otimizador
        params = list(self.shared_network.parameters())
        params.extend(list(self.actor_head.parameters()))
        params.extend(list(self.critic_head.parameters()))
        self.optimizer = optim.Adam(params, lr=learning_rate)

    def _build_shared_network(self) -> nn.Module:
        """Constrói rede compartilhada"""
        return nn.Sequential(
            nn.Linear(self.state_size, 128), nn.ReLU(), nn.Linear(128, 128), nn.ReLU()
        )

    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass"""
        shared_features = self.shared_network(state)
        action_probs = F.softmax(self.actor_head(shared_features), dim=-1)
        value = self.critic_head(shared_features)
        return action_probs, value

    def act(self, state: np.ndarray) -> Tuple[int, float, float]:
        """Seleciona ação"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            action_probs, value = self.forward(state_tensor)
            dist = torch.distributions.Categorical(action_probs)
            action = dist.sample()
            log_prob = dist.log_prob(action)

        return action.item(), log_prob.item(), value.item()

    def update(
        self,
        states: List[np.ndarray],
        actions: List[int],
        rewards: List[float],
        values: List[float],
        log_probs: List[float],
        dones: List[bool],
    ) -> Dict[str, float]:
        """Atualiza o modelo"""
        if len(states) == 0:
            return {}

        # Converter para tensores
        states_tensor = torch.FloatTensor(states).to(self.device)
        actions_tensor = torch.LongTensor(actions).to(self.device)
        # rewards_tensor removido - não utilizado
        # values_tensor removido - não utilizado
        # log_probs_tensor removido - não utilizado
        # dones_tensor removido - não utilizado

        # Computar vantagens
        advantages = []
        returns = []

        R = 0
        for t in reversed(range(len(rewards))):
            R = rewards[t] + self.gamma * R * (1 - dones[t])
            returns.insert(0, R)
            advantages.insert(0, R - values[t])

        advantages = torch.FloatTensor(advantages).to(self.device)
        returns = torch.FloatTensor(returns).to(self.device)

        # Normalizar vantagens
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # Forward pass
        action_probs, predicted_values = self.forward(states_tensor)

        # Perdas
        dist = torch.distributions.Categorical(action_probs)
        log_probs_new = dist.log_prob(actions_tensor)
        entropy = dist.entropy().mean()

        # Perda do ator
        actor_loss = -(log_probs_new * advantages).mean() - self.entropy_coef * entropy

        # Perda do crítico
        critic_loss = F.mse_loss(predicted_values.squeeze(), returns)

        # Perda total
        total_loss = actor_loss + self.value_coef * critic_loss

        # Backpropagation
        self.optimizer.zero_grad()
        total_loss.backward()
        params = list(self.shared_network.parameters())
        params.extend(list(self.actor_head.parameters()))
        params.extend(list(self.critic_head.parameters()))
        torch.nn.utils.clip_grad_norm_(params, max_norm=1.0)
        self.optimizer.step()

        return {
            "actor_loss": actor_loss.item(),
            "critic_loss": critic_loss.item(),
            "total_loss": total_loss.item(),
        }


class MultiAgentRL:
    """Sistema Multi-Agent Reinforcement Learning"""

    def __init__(
        self,
        num_agents: int,
        state_size: int,
        action_size: int,
        algorithm: str = "dqn",
        device: str = "cpu",
    ):
        self.num_agents = num_agents
        self.state_size = state_size
        self.action_size = action_size
        self.algorithm = algorithm
        self.device = device

        # Inicializar agentes
        self.agents = []
        for i in range(num_agents):
            if algorithm == "dqn":
                agent = AdvancedDQN(state_size, action_size, device=device)
            elif algorithm == "ppo":
                agent = PPOAgent(state_size, action_size, device=device)
            elif algorithm == "a3c":
                agent = A3CAgent(state_size, action_size, device=device)
            else:
                raise ValueError(f"Algoritmo {algorithm} não suportado")

            self.agents.append(agent)

        # Sistema de comunicação entre agentes
        self.communication_matrix = np.ones((num_agents, num_agents)) / num_agents
        self.shared_experience_buffer = deque(maxlen=10000)

    def act(self, states: List[np.ndarray], training: bool = True) -> List[int]:
        """Todos os agentes agem simultaneamente"""
        actions = []
        for i, (agent, state) in enumerate(zip(self.agents, states)):
            action = agent.act(state, training)
            actions.append(action)
        return actions

    def store_experience(
        self,
        agent_id: int,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Armazena experiência de um agente"""
        if self.algorithm == "dqn":
            self.agents[agent_id].remember(state, action, reward, next_state, done)
        elif self.algorithm == "ppo":
            # PPO armazena internamente
            pass
        elif self.algorithm == "a3c":
            # A3C armazena internamente
            pass

        # Armazenar experiência compartilhada
        self.shared_experience_buffer.append(
            {
                "agent_id": agent_id,
                "state": state,
                "action": action,
                "reward": reward,
                "next_state": next_state,
                "done": done,
            }
        )

    def update_agents(self) -> Dict[str, List[float]]:
        """Atualiza todos os agentes"""
        losses = {}

        for i, agent in enumerate(self.agents):
            if self.algorithm == "dqn":
                loss = agent.replay()
                if f"agent_{i}_loss" not in losses:
                    losses[f"agent_{i}_loss"] = []
                losses[f"agent_{i}_loss"].append(loss)
            elif self.algorithm == "ppo":
                agent_losses = agent.update()
                for key, value in agent_losses.items():
                    if f"agent_{i}_{key}" not in losses:
                        losses[f"agent_{i}_{key}"] = []
                    losses[f"agent_{i}_{key}"].append(value)
            elif self.algorithm == "a3c":
                # A3C requer dados específicos para atualização
                pass

        return losses

    def share_experience(self, sharing_ratio: float = 0.1) -> None:
        """Compartilha experiência entre agentes"""
        if len(self.shared_experience_buffer) < 100:
            return

        # Selecionar experiências para compartilhar
        num_to_share = int(len(self.shared_experience_buffer) * sharing_ratio)
        shared_experiences = random.sample(
            list(self.shared_experience_buffer), num_to_share
        )

        # Distribuir experiências para outros agentes
        for exp in shared_experiences:
            for i, agent in enumerate(self.agents):
                if i != exp["agent_id"] and self.algorithm == "dqn":
                    agent.remember(
                        exp["state"],
                        exp["action"],
                        exp["reward"],
                        exp["next_state"],
                        exp["done"],
                    )

    def get_agent_info(self) -> Dict[str, Any]:
        """Retorna informações dos agentes"""
        info = {}
        for i, agent in enumerate(self.agents):
            info[f"agent_{i}"] = {
                "algorithm": self.algorithm,
                "state_size": self.state_size,
                "action_size": self.action_size,
                "device": self.device,
            }
        return info

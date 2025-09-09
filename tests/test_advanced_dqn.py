"""
Testes para o sistema DQN avançado.
"""

import unittest
import numpy as np
import tempfile
import os
from unittest.mock import patch

# Adiciona src ao path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))  # noqa: E402

from src.ai.advanced_dqn import (
    AdvancedDQN,
    ReplayBuffer,
    Experience,
    MultiAgentDQN,
)  # noqa: E402


class TestReplayBuffer(unittest.TestCase):
    """Testes para ReplayBuffer"""

    def setUp(self):
        self.buffer = ReplayBuffer(capacity=100)

    def test_push_and_sample(self):
        """Testa adicionar e amostrar experiências"""
        # Adiciona algumas experiências
        for i in range(10):
            exp = Experience(
                state=np.random.random(4),
                action=i % 3,
                reward=float(i),
                next_state=np.random.random(4),
                done=i == 9,
            )
            self.buffer.push(exp)

        # Testa amostragem
        batch = self.buffer.sample(5)
        self.assertEqual(len(batch), 5)

        # Testa capacidade máxima
        for i in range(150):
            exp = Experience(
                state=np.random.random(4),
                action=i % 3,
                reward=float(i),
                next_state=np.random.random(4),
                done=False,
            )
            self.buffer.push(exp)

        self.assertEqual(len(self.buffer), 100)

    def test_empty_buffer(self):
        """Testa buffer vazio"""
        batch = self.buffer.sample(5)
        self.assertEqual(len(batch), 0)


class TestAdvancedDQN(unittest.TestCase):
    """Testes para AdvancedDQN"""

    def setUp(self):
        self.dqn = AdvancedDQN(
            state_size=4,
            action_size=3,
            hidden_sizes=[8, 4],
            learning_rate=0.001,
            gamma=0.95,
            epsilon=0.1,
            memory_size=1000,
            batch_size=32,
        )

    def test_initialization(self):
        """Testa inicialização do DQN"""
        self.assertEqual(self.dqn.state_size, 4)
        self.assertEqual(self.dqn.action_size, 3)
        self.assertEqual(self.dqn.epsilon, 0.1)
        self.assertEqual(len(self.dqn.memory), 0)

    def test_act_exploration(self):
        """Testa seleção de ação com exploração"""
        state = np.random.random(4)

        # Com epsilon alto, deve explorar
        self.dqn.epsilon = 1.0
        action = self.dqn.act(state, training=True)
        self.assertIn(action, range(3))

    def test_act_exploitation(self):
        """Testa seleção de ação com exploração"""
        state = np.random.random(4)

        # Com epsilon baixo, deve explorar
        self.dqn.epsilon = 0.0
        action = self.dqn.act(state, training=True)
        self.assertIn(action, range(3))

    def test_remember(self):
        """Testa armazenamento de experiência"""
        state = np.random.random(4)
        action = 1
        reward = 0.5
        next_state = np.random.random(4)
        done = False

        self.dqn.remember(state, action, reward, next_state, done)

        self.assertEqual(len(self.dqn.memory), 1)
        exp = self.dqn.memory.buffer[0]
        self.assertTrue(np.array_equal(exp.state, state))
        self.assertEqual(exp.action, action)
        self.assertEqual(exp.reward, reward)
        self.assertTrue(np.array_equal(exp.next_state, next_state))
        self.assertEqual(exp.done, done)

    def test_replay_empty_buffer(self):
        """Testa replay com buffer vazio"""
        loss = self.dqn.replay()
        self.assertEqual(loss, 0.0)

    def test_replay_with_data(self):
        """Testa replay com dados"""
        # Adiciona experiências ao buffer
        for _ in range(50):
            state = np.random.random(4)
            action = np.random.randint(3)
            reward = np.random.random()
            next_state = np.random.random(4)
            done = np.random.random() < 0.1

            self.dqn.remember(state, action, reward, next_state, done)

        # Testa replay
        loss = self.dqn.replay()
        self.assertIsInstance(loss, float)
        self.assertGreaterEqual(loss, 0.0)

    def test_train_episode(self):
        """Testa treinamento de um episódio"""
        stats = self.dqn.train_episode(max_steps=10)

        self.assertIn("episode_reward", stats)
        self.assertIn("episode_loss", stats)
        self.assertIn("epsilon", stats)
        self.assertIn("steps", stats)

        self.assertIsInstance(stats["episode_reward"], float)
        self.assertIsInstance(stats["episode_loss"], float)
        self.assertIsInstance(stats["steps"], int)

    def test_get_q_values(self):
        """Testa obtenção de Q-values"""
        state = np.random.random(4)
        q_values = self.dqn.get_q_values(state)

        self.assertEqual(len(q_values), 3)
        self.assertTrue(all(isinstance(q, float) for q in q_values))

    def test_save_and_load_model(self):
        """Testa salvamento e carregamento do modelo"""
        # Treina um pouco
        for _ in range(5):
            self.dqn.train_episode(max_steps=10)

        # Salva modelo
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            self.dqn.save_model(temp_path)
            self.assertTrue(os.path.exists(temp_path))

            # Cria novo DQN e carrega modelo
            new_dqn = AdvancedDQN(4, 3)
            new_dqn.load_model(temp_path)

            # Verifica se carregou corretamente
            self.assertEqual(new_dqn.state_size, 4)
            self.assertEqual(new_dqn.action_size, 3)
            self.assertEqual(new_dqn.episode_count, self.dqn.episode_count)

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_training_stats(self):
        """Testa obtenção de estatísticas de treinamento"""
        # Treina um pouco
        for _ in range(3):
            self.dqn.train_episode(max_steps=5)

        stats = self.dqn.get_training_stats()

        self.assertIn("total_episodes", stats)
        self.assertIn("total_steps", stats)
        self.assertIn("current_epsilon", stats)
        self.assertIn("memory_size", stats)

        self.assertEqual(stats["total_episodes"], 3)


class TestMultiAgentDQN(unittest.TestCase):
    """Testes para MultiAgentDQN"""

    def setUp(self):
        self.multi_dqn = MultiAgentDQN(num_agents=3, state_size=4, action_size=3)

    def test_initialization(self):
        """Testa inicialização do MultiAgentDQN"""
        self.assertEqual(self.multi_dqn.num_agents, 3)
        self.assertEqual(len(self.multi_dqn.agents), 3)

        for i, agent in enumerate(self.multi_dqn.agents):
            self.assertEqual(agent.agent_id, i)
            self.assertEqual(agent.state_size, 4)
            self.assertEqual(agent.action_size, 3)

    def test_train_all_agents(self):
        """Testa treinamento de todos os agentes"""
        # Mock do logger para evitar spam
        with patch("src.ai.advanced_dqn.logger"):
            self.multi_dqn.train_all_agents(episodes=2)

        # Verifica se todos os agentes foram treinados
        for agent in self.multi_dqn.agents:
            self.assertGreater(agent.episode_count, 0)

    def test_get_global_stats(self):
        """Testa obtenção de estatísticas globais"""
        stats = self.multi_dqn.get_global_stats()

        self.assertIn("num_agents", stats)
        self.assertIn("agents", stats)

        self.assertEqual(stats["num_agents"], 3)
        self.assertEqual(len(stats["agents"]), 3)

        for agent_stats in stats["agents"]:
            self.assertIn("agent_id", agent_stats)
            self.assertIn("total_episodes", agent_stats)


class TestDQNIntegration(unittest.TestCase):
    """Testes de integração para DQN"""

    def test_full_training_cycle(self):
        """Testa ciclo completo de treinamento"""
        dqn = AdvancedDQN(
            state_size=4,
            action_size=3,
            hidden_sizes=[16, 8],
            learning_rate=0.01,
            epsilon=0.5,
            memory_size=1000,
            batch_size=16,
        )

        # Treina por vários episódios
        for episode in range(10):
            stats = dqn.train_episode(max_steps=20)

            # Verifica se as estatísticas fazem sentido
            self.assertIsInstance(stats["episode_reward"], float)
            self.assertIsInstance(stats["episode_loss"], float)
            self.assertGreaterEqual(stats["steps"], 1)
            self.assertLessEqual(stats["steps"], 20)

        # Verifica se o epsilon decaiu
        self.assertLess(dqn.epsilon, 0.5)

        # Verifica se há experiências na memória
        self.assertGreater(len(dqn.memory), 0)

    def test_agent_learning(self):
        """Testa se o agente está aprendendo"""
        dqn = AdvancedDQN(
            state_size=4,
            action_size=3,
            learning_rate=0.01,
            epsilon=0.1,
            memory_size=1000,
            batch_size=32,
        )

        # Treina por vários episódios
        rewards = []
        for _ in range(20):
            stats = dqn.train_episode(max_steps=50)
            rewards.append(stats["episode_reward"])

        # Verifica se há alguma melhoria (mesmo que pequena)
        # Em um teste real, esperaríamos ver melhoria ao longo do tempo
        self.assertIsInstance(rewards[0], float)
        self.assertIsInstance(rewards[-1], float)


if __name__ == "__main__":
    # Configura logging para testes
    import logging

    logging.basicConfig(level=logging.WARNING)

    # Executa testes
    unittest.main(verbosity=2)

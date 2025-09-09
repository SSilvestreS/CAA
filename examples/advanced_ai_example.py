"""
Exemplo de Uso dos Modelos de IA Avançados
Versão 1.5 - IA Avançada e Escalabilidade

Demonstra como usar os modelos de IA avançados:
- Transformers para análise de sentimento e políticas
- LSTM para previsão de séries temporais
- GANs para geração de dados sintéticos
- Reinforcement Learning para tomada de decisões
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

# datetime removido - não utilizado
from typing import List  # noqa: E402

from src.ai.advanced_models import AdvancedAIManager  # noqa: E402
from src.ai.advanced_models.transformer_models import (  # noqa: E402
    CityTransformerManager,
)
from src.ai.advanced_models.lstm_models import LSTMModelManager  # noqa: E402
from src.ai.advanced_models.gan_models import GANModelManager  # noqa: E402
from src.ai.advanced_models.reinforcement_learning import MultiAgentRL  # noqa: E402


class CitySimulationEnvironment:
    """Ambiente de simulação simples para demonstração"""

    def __init__(self, num_agents: int = 4):
        self.num_agents = num_agents
        self.state_size = 10
        self.action_size = 5
        self.current_states = np.random.randn(num_agents, self.state_size)
        self.step_count = 0
        self.max_steps = 100

    def reset(self) -> List[np.ndarray]:
        """Reset do ambiente"""
        self.current_states = np.random.randn(self.num_agents, self.state_size)
        self.step_count = 0
        return [self.current_states[i] for i in range(self.num_agents)]

    def step(self, actions: List[int]) -> tuple:
        """Executa ações e retorna próximo estado"""
        next_states = []
        rewards = []
        dones = []

        for i, action in enumerate(actions):
            # Simular transição de estado
            noise = np.random.randn(self.state_size) * 0.1
            next_state = self.current_states[i] + noise + action * 0.1
            next_states.append(next_state)

            # Simular recompensa
            reward = np.random.randn() + action * 0.5
            rewards.append(reward)

            # Simular término
            done = self.step_count >= self.max_steps
            dones.append(done)

        self.current_states = np.array(next_states)
        self.step_count += 1

        return next_states, rewards, dones, {}


def demonstrate_transformers():
    """Demonstra uso dos modelos Transformer"""
    print("=== DEMONSTRAÇÃO DE TRANSFORMERS ===")

    # Inicializar gerenciador
    manager = CityTransformerManager(device="cpu")

    # Dados de exemplo para análise de sentimento
    sentiment_data = torch.randint(0, 1000, (100, 50))  # 100 amostras, 50 tokens
    sentiment_labels = torch.randint(0, 3, (100,))  # 3 classes: positivo, neutro, negativo

    # Criar DataLoader simples
    from torch.utils.data import DataLoader, TensorDataset

    dataset = TensorDataset(sentiment_data, sentiment_labels)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

    # Treinar modelo de sentimento
    print("Treinando modelo de análise de sentimento...")
    losses = manager.train_model("sentiment", dataloader, epochs=10)
    print(f"Losses finais: {losses[-5:]}")

    # Fazer predição
    test_data = torch.randint(0, 1000, (5, 50))
    predictions = manager.predict("sentiment", test_data)
    print(f"Predições de sentimento: {predictions.argmax(dim=1)}")

    # Informações do modelo
    info = manager.get_model_info()
    print(f"Informações do modelo: {info['sentiment']}")


def demonstrate_lstm():
    """Demonstra uso dos modelos LSTM"""
    print("\n=== DEMONSTRAÇÃO DE LSTM ===")

    # Inicializar gerenciador
    manager = LSTMModelManager(device="cpu")

    # Dados de exemplo para previsão de tráfego
    sequence_length = 24  # 24 horas
    num_features = 10
    num_samples = 200

    # Gerar dados sintéticos de tráfego
    traffic_data = np.random.randn(num_samples, sequence_length, num_features)
    traffic_targets = np.random.randn(num_samples, 24)  # Previsão para próximas 24 horas

    # Criar DataLoader
    from torch.utils.data import DataLoader, TensorDataset

    dataset = TensorDataset(torch.FloatTensor(traffic_data), torch.FloatTensor(traffic_targets))
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Treinar modelo de tráfego
    print("Treinando modelo de previsão de tráfego...")
    losses = manager.train_model("traffic", dataloader, epochs=20)
    print(f"Losses finais: {losses[-5:]}")

    # Fazer predição
    test_data = torch.FloatTensor(np.random.randn(5, sequence_length, num_features))
    spatial_data = torch.FloatTensor(np.random.randn(5, sequence_length, num_features))

    predictions = manager.predict("traffic", test_data, spatial_data)
    print(f"Predições de tráfego shape: {predictions['traffic_prediction'].shape}")
    print(f"Confiança shape: {predictions['confidence'].shape}")

    # Informações do modelo
    info = manager.get_model_info()
    print(f"Informações do modelo: {info['traffic']}")


def demonstrate_gans():
    """Demonstra uso dos modelos GAN"""
    print("\n=== DEMONSTRAÇÃO DE GANs ===")

    # Inicializar gerenciador
    manager = GANModelManager(device="cpu")

    # Dados de exemplo para treinamento
    real_data = torch.randn(1000, 64)  # 1000 amostras, 64 características

    # Criar DataLoader
    from torch.utils.data import DataLoader, TensorDataset

    dataset = TensorDataset(real_data)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Treinar GAN para dados de cidade
    print("Treinando GAN para dados de cidade...")
    losses = manager.train_model("city_data", dataloader, epochs=50)
    print(f"Losses finais - D: {losses['d_losses'][-5:]}, G: {losses['g_losses'][-5:]}")

    # Gerar dados sintéticos
    synthetic_data = manager.generate_data("city_data", num_samples=100)
    print(f"Dados sintéticos gerados: {synthetic_data.shape}")

    # Gerar agentes sintéticos
    agents = manager.models["agents"].generate_agent(num_agents=10, device="cpu")
    print(f"Agentes sintéticos gerados: {agents['agent_data'].shape}")
    print(f"Tipos de agentes: {agents['agent_types'].argmax(dim=1)}")

    # Informações do modelo
    info = manager.get_model_info()
    print(f"Informações do modelo: {info['city_data']}")


def demonstrate_reinforcement_learning():
    """Demonstra uso do Reinforcement Learning"""
    print("\n=== DEMONSTRAÇÃO DE REINFORCEMENT LEARNING ===")

    # Criar ambiente de simulação
    environment = CitySimulationEnvironment(num_agents=4)

    # Inicializar sistema RL
    rl_system = MultiAgentRL(num_agents=4, state_size=10, action_size=5, algorithm="dqn", device="cpu")

    # Treinar sistema RL
    print("Treinando sistema RL multi-agente...")
    losses = {}

    for episode in range(100):
        states = environment.reset()
        episode_rewards = [0.0] * 4

        for step in range(50):
            # Agentes agem
            actions = rl_system.act(states, training=True)

            # Ambiente responde
            next_states, rewards, dones, info = environment.step(actions)

            # Armazenar experiências
            for i, (state, action, reward, next_state, done) in enumerate(
                zip(states, actions, rewards, next_states, dones)
            ):
                rl_system.store_experience(i, state, action, reward, next_state, done)
                episode_rewards[i] += reward

            states = next_states

            if any(dones):
                break

        # Atualizar agentes a cada 10 episódios
        if episode % 10 == 0:
            episode_losses = rl_system.update_agents()
            for key, value in episode_losses.items():
                if key not in losses:
                    losses[key] = []
                losses[key].extend(value)

        if episode % 20 == 0:
            avg_reward = sum(episode_rewards) / len(episode_rewards)
            print(f"Episódio {episode}, Recompensa Média: {avg_reward:.2f}")

    # Testar sistema treinado
    print("Testando sistema RL treinado...")
    test_states = environment.reset()
    test_actions = rl_system.act(test_states, training=False)
    print(f"Ações dos agentes: {test_actions}")

    # Informações do sistema
    info = rl_system.get_agent_info()
    print(f"Informações do sistema RL: {len(info)} agentes")


def demonstrate_integrated_system():
    """Demonstra sistema integrado de IA avançada"""
    print("\n=== DEMONSTRAÇÃO DE SISTEMA INTEGRADO ===")

    # Inicializar gerenciador principal
    ai_manager = AdvancedAIManager(device="cpu")

    # Inicializar sistema RL
    ai_manager.initialize_rl_system(num_agents=4, state_size=10, action_size=5, algorithm="dqn")

    # Dados de exemplo
    sentiment_data = torch.randint(0, 1000, (50, 30))
    sentiment_labels = torch.randint(0, 3, (50,))

    traffic_data = torch.FloatTensor(np.random.randn(50, 24, 8))
    traffic_targets = torch.FloatTensor(np.random.randn(50, 24))

    # Criar DataLoaders
    from torch.utils.data import DataLoader, TensorDataset

    sentiment_dataset = TensorDataset(sentiment_data, sentiment_labels)
    sentiment_dataloader = DataLoader(sentiment_dataset, batch_size=16, shuffle=True)

    traffic_dataset = TensorDataset(traffic_data, traffic_targets)
    traffic_dataloader = DataLoader(traffic_dataset, batch_size=16, shuffle=True)

    # Treinar modelos
    print("Treinando modelos integrados...")

    # Transformer
    transformer_losses = ai_manager.train_transformer_model("sentiment", sentiment_dataloader, epochs=5)
    print(f"Transformer losses: {transformer_losses[-3:]}")

    # LSTM
    lstm_losses = ai_manager.train_lstm_model("traffic", traffic_dataloader, epochs=10)
    print(f"LSTM losses: {lstm_losses[-3:]}")

    # GAN
    real_data = torch.randn(200, 32)
    gan_dataset = TensorDataset(real_data)
    gan_dataloader = DataLoader(gan_dataset, batch_size=16, shuffle=True)
    gan_losses = ai_manager.train_gan_model("city_data", gan_dataloader, epochs=20)
    print(f"GAN losses - D: {gan_losses['d_losses'][-3:]}, G: {gan_losses['g_losses'][-3:]}")

    # RL
    environment = CitySimulationEnvironment(num_agents=4)
    rl_losses = ai_manager.train_rl_system(environment, episodes=50)
    print(f"RL losses: {len(rl_losses)} tipos de perda")

    # Fazer predições integradas
    print("\nFazendo predições integradas...")

    # Análise de sentimento
    sentiment_input = torch.randint(0, 1000, (3, 30))
    sentiment_pred = ai_manager.predict_with_transformer("sentiment", sentiment_input)
    print(f"Predições de sentimento: {sentiment_pred.argmax(dim=1)}")

    # Previsão de tráfego
    traffic_input = torch.FloatTensor(np.random.randn(3, 24, 8))
    traffic_pred = ai_manager.predict_with_lstm("traffic", traffic_input)
    print(f"Predições de tráfego shape: {traffic_pred['traffic_prediction'].shape}")

    # Geração de dados
    synthetic_data = ai_manager.generate_with_gan("city_data", num_samples=10)
    print(f"Dados sintéticos gerados: {synthetic_data.shape}")

    # Ações RL
    rl_states = [np.random.randn(10) for _ in range(4)]
    rl_actions = ai_manager.act_with_rl(rl_states, training=False)
    print(f"Ações RL: {rl_actions}")

    # Resumo de performance
    summary = ai_manager.get_performance_summary()
    print(f"\nResumo de performance: {summary}")

    # Salvar todos os modelos
    ai_manager.save_all_models("saved_models")
    print("Modelos salvos em 'saved_models'")


def create_visualization():
    """Cria visualizações dos resultados"""
    print("\n=== CRIANDO VISUALIZAÇÕES ===")

    # Exemplo de visualização de perdas de treinamento
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Simular dados de perda
    episodes = range(50)

    # Transformer losses
    transformer_losses = np.exp(-np.array(episodes) * 0.1) + 0.1
    axes[0, 0].plot(episodes, transformer_losses)
    axes[0, 0].set_title("Transformer Training Loss")
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Loss")

    # LSTM losses
    lstm_losses = np.exp(-np.array(episodes) * 0.05) + 0.2
    axes[0, 1].plot(episodes, lstm_losses)
    axes[0, 1].set_title("LSTM Training Loss")
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Loss")

    # GAN losses
    gan_d_losses = np.exp(-np.array(episodes) * 0.02) + 0.5
    gan_g_losses = np.exp(-np.array(episodes) * 0.03) + 0.3
    axes[1, 0].plot(episodes, gan_d_losses, label="Discriminator")
    axes[1, 0].plot(episodes, gan_g_losses, label="Generator")
    axes[1, 0].set_title("GAN Training Losses")
    axes[1, 0].set_xlabel("Epoch")
    axes[1, 0].set_ylabel("Loss")
    axes[1, 0].legend()

    # RL rewards
    rl_rewards = np.cumsum(np.random.randn(50) * 0.1 + 0.5)
    axes[1, 1].plot(episodes, rl_rewards)
    axes[1, 1].set_title("RL Cumulative Rewards")
    axes[1, 1].set_xlabel("Episode")
    axes[1, 1].set_ylabel("Cumulative Reward")

    plt.tight_layout()
    plt.savefig("advanced_ai_training_results.png", dpi=300, bbox_inches="tight")
    print("Visualização salva como 'advanced_ai_training_results.png'")

    # Mostrar gráfico
    plt.show()


def main():
    """Função principal de demonstração"""
    print("🚀 DEMONSTRAÇÃO DE MODELOS DE IA AVANÇADOS - VERSÃO 1.5")
    print("=" * 60)

    try:
        # Demonstrar cada tipo de modelo
        demonstrate_transformers()
        demonstrate_lstm()
        demonstrate_gans()
        demonstrate_reinforcement_learning()

        # Demonstrar sistema integrado
        demonstrate_integrated_system()

        # Criar visualizações
        create_visualization()

        print("\n✅ Demonstração concluída com sucesso!")
        print("\nFuncionalidades implementadas:")
        print("- ✅ Modelos Transformer para análise de linguagem natural")
        print("- ✅ Modelos LSTM para previsão de séries temporais")
        print("- ✅ Modelos GAN para geração de dados sintéticos")
        print("- ✅ Sistema de Reinforcement Learning multi-agente")
        print("- ✅ Gerenciador integrado de todos os modelos")
        print("- ✅ Sistema de treinamento e avaliação")
        print("- ✅ Visualizações e métricas de performance")

    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

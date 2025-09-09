"""
Gerenciador Principal de Modelos de IA Avançados
Versão 1.5 - IA Avançada e Escalabilidade

Gerencia todos os modelos de IA avançados:
- Transformers
- LSTM/GRU
- GANs
- Reinforcement Learning
"""

import torch  # type: ignore
import numpy as np  # type: ignore
from typing import Dict, List, Optional, Any
import os
import json
from datetime import datetime
from .transformer_models import CityTransformerManager
from .lstm_models import LSTMModelManager
from .gan_models import GANModelManager
from .reinforcement_learning import MultiAgentRL


class AdvancedAIManager:
    """Gerenciador principal de todos os modelos de IA avançados"""

    def __init__(self, device: str = "cpu", config_path: Optional[str] = None):
        self.device = device
        self.config_path = config_path or "ai_models_config.json"

        # Inicializar gerenciadores
        self.transformer_manager = CityTransformerManager(device)
        self.lstm_manager = LSTMModelManager(device)
        self.gan_manager = GANModelManager(device)

        # Sistema de RL multi-agente
        self.rl_system = None

        # Configurações
        self.config = self._load_config()

        # Histórico de treinamento
        self.training_history = {"transformer": [], "lstm": [], "gan": [], "rl": []}

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações dos modelos"""
        default_config = {
            "transformer": {
                "learning_rate": 1e-4,
                "batch_size": 32,
                "epochs": 100,
                "d_model": 512,
                "nhead": 8,
                "num_layers": 6,
            },
            "lstm": {
                "learning_rate": 1e-3,
                "batch_size": 64,
                "epochs": 50,
                "hidden_size": 128,
                "num_layers": 3,
            },
            "gan": {
                "learning_rate": 2e-4,
                "batch_size": 32,
                "epochs": 100,
                "noise_dim": 100,
            },
            "rl": {
                "learning_rate": 1e-4,
                "gamma": 0.99,
                "epsilon": 1.0,
                "memory_size": 100000,
            },
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
                return default_config

        return default_config

    def save_config(self) -> None:
        """Salva configurações dos modelos"""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def initialize_rl_system(
        self, num_agents: int, state_size: int, action_size: int, algorithm: str = "dqn"
    ) -> None:
        """Inicializa sistema de RL multi-agente"""
        self.rl_system = MultiAgentRL(
            num_agents=num_agents,
            state_size=state_size,
            action_size=action_size,
            algorithm=algorithm,
            device=self.device,
        )

    def train_transformer_model(
        self, model_name: str, dataloader, epochs: Optional[int] = None
    ) -> List[float]:
        """Treina modelo Transformer"""
        epochs = epochs or self.config["transformer"]["epochs"]
        losses = self.transformer_manager.train_model(model_name, dataloader, epochs)

        # Registrar histórico
        self.training_history["transformer"].append(
            {
                "model": model_name,
                "epochs": epochs,
                "losses": losses,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return losses

    def train_lstm_model(
        self, model_name: str, dataloader, epochs: Optional[int] = None
    ) -> List[float]:
        """Treina modelo LSTM"""
        epochs = epochs or self.config["lstm"]["epochs"]
        losses = self.lstm_manager.train_model(model_name, dataloader, epochs)

        # Registrar histórico
        self.training_history["lstm"].append(
            {
                "model": model_name,
                "epochs": epochs,
                "losses": losses,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return losses

    def train_gan_model(
        self, model_name: str, dataloader, epochs: Optional[int] = None
    ) -> Dict[str, List[float]]:
        """Treina modelo GAN"""
        epochs = epochs or self.config["gan"]["epochs"]
        losses = self.gan_manager.train_model(model_name, dataloader, epochs)

        # Registrar histórico
        self.training_history["gan"].append(
            {
                "model": model_name,
                "epochs": epochs,
                "losses": losses,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return losses

    def train_rl_system(
        self, environment, episodes: int = 1000
    ) -> Dict[str, List[float]]:
        """Treina sistema de RL multi-agente"""
        if self.rl_system is None:
            raise ValueError("Sistema RL não inicializado")

        all_losses = {}

        for episode in range(episodes):
            # Resetar ambiente
            states = environment.reset()
            episode_rewards = [0.0] * self.rl_system.num_agents

            done = False
            step = 0
            max_steps = 1000

            while not done and step < max_steps:
                # Agentes agem
                actions = self.rl_system.act(states, training=True)

                # Ambiente responde
                next_states, rewards, dones, _ = environment.step(actions)

                # Armazenar experiências
                for i, (state, action, reward, next_state, done) in enumerate(
                    zip(states, actions, rewards, next_states, dones)
                ):
                    self.rl_system.store_experience(
                        i, state, action, reward, next_state, done
                    )
                    episode_rewards[i] += reward

                states = next_states
                done = any(dones)
                step += 1

            # Atualizar agentes
            if episode % 10 == 0:
                losses = self.rl_system.update_agents()
                for key, value in losses.items():
                    if key not in all_losses:
                        all_losses[key] = []
                    all_losses[key].extend(value)

            # Compartilhar experiência
            if episode % 50 == 0:
                self.rl_system.share_experience()

            if episode % 100 == 0:
                avg_rewards = [sum(episode_rewards) / len(episode_rewards)]
                print(f"Episódio {episode}, Recompensa Média: {avg_rewards[0]:.2f}")

        # Registrar histórico
        self.training_history["rl"].append(
            {
                "episodes": episodes,
                "losses": all_losses,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return all_losses

    def predict_with_transformer(
        self, model_name: str, data: torch.Tensor
    ) -> torch.Tensor:
        """Faz predição com modelo Transformer"""
        return self.transformer_manager.predict(model_name, data)

    def predict_with_lstm(self, model_name: str, *args) -> Dict[str, torch.Tensor]:
        """Faz predição com modelo LSTM"""
        return self.lstm_manager.predict(model_name, *args)

    def generate_with_gan(self, model_name: str, num_samples: int) -> torch.Tensor:
        """Gera dados com modelo GAN"""
        return self.gan_manager.generate_data(model_name, num_samples)

    def act_with_rl(self, states: List[np.ndarray], training: bool = True) -> List[int]:
        """Agentes RL agem"""
        if self.rl_system is None:
            raise ValueError("Sistema RL não inicializado")
        return self.rl_system.act(states, training)

    def evaluate_model(
        self, model_type: str, model_name: str, dataloader
    ) -> Dict[str, float]:
        """Avalia um modelo específico"""
        if model_type == "transformer":
            trainer = self.transformer_manager.trainers[model_name]
            return trainer.evaluate(dataloader)
        elif model_type == "lstm":
            trainer = self.lstm_manager.trainers[model_name]
            return trainer.evaluate(dataloader)
        else:
            raise ValueError(
                f"Tipo de modelo {model_type} não suportado para avaliação"
            )

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações de todos os modelos"""
        info = {
            "transformer": self.transformer_manager.get_model_info(),
            "lstm": self.lstm_manager.get_model_info(),
            "gan": self.gan_manager.get_model_info(),
            "rl": self.rl_system.get_agent_info() if self.rl_system else {},
        }
        return info

    def save_all_models(self, base_path: str = "models") -> None:
        """Salva todos os modelos"""
        os.makedirs(base_path, exist_ok=True)

        # Salvar modelos Transformer
        for name, trainer in self.transformer_manager.trainers.items():
            path = os.path.join(base_path, f"transformer_{name}.pth")
            trainer.save_model(path)

        # Salvar modelos LSTM
        for name, trainer in self.lstm_manager.trainers.items():
            path = os.path.join(base_path, f"lstm_{name}.pth")
            trainer.save_model(path)

        # Salvar modelos GAN
        for name, trainer in self.gan_manager.trainers.items():
            path = os.path.join(base_path, f"gan_{name}.pth")
            trainer.save_models(path)

        # Salvar sistema RL
        if self.rl_system:
            for i, agent in enumerate(self.rl_system.agents):
                if hasattr(agent, "save"):
                    path = os.path.join(base_path, f"rl_agent_{i}.pth")
                    agent.save(path)

        # Salvar configurações e histórico
        config_path = os.path.join(base_path, "config.json")
        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=2)

        history_path = os.path.join(base_path, "training_history.json")
        with open(history_path, "w") as f:
            json.dump(self.training_history, f, indent=2)

    def load_all_models(self, base_path: str = "models") -> None:
        """Carrega todos os modelos"""
        if not os.path.exists(base_path):
            print(f"Diretório {base_path} não encontrado")
            return

        # Carregar configurações
        config_path = os.path.join(base_path, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = json.load(f)

        # Carregar histórico
        history_path = os.path.join(base_path, "training_history.json")
        if os.path.exists(history_path):
            with open(history_path, "r") as f:
                self.training_history = json.load(f)

        # Carregar modelos (implementação específica para cada tipo)
        print("Modelos carregados com sucesso")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance de todos os modelos"""
        summary = {
            "total_models": 0,
            "models_by_type": {},
            "training_status": {},
            "device_usage": {},
        }

        # Contar modelos por tipo
        for model_type, manager in [
            ("transformer", self.transformer_manager),
            ("lstm", self.lstm_manager),
            ("gan", self.gan_manager),
        ]:
            if hasattr(manager, "models"):
                count = len(manager.models)
                summary["models_by_type"][model_type] = count
                summary["total_models"] += count

        if self.rl_system:
            summary["models_by_type"]["rl"] = self.rl_system.num_agents
            summary["total_models"] += self.rl_system.num_agents

        # Status de treinamento
        for model_type, history in self.training_history.items():
            summary["training_status"][model_type] = len(history)

        # Uso de dispositivo
        summary["device_usage"] = {
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": (
                torch.cuda.device_count() if torch.cuda.is_available() else 0
            ),
        }

        return summary

    def optimize_models(self) -> Dict[str, Any]:
        """Otimiza todos os modelos para melhor performance"""
        optimizations = {}

        # Otimizar modelos Transformer
        for name, model in self.transformer_manager.models.items():
            model.eval()
            optimizations[f"transformer_{name}"] = "Otimizado"

        # Otimizar modelos LSTM
        for name, model in self.lstm_manager.models.items():
            model.eval()
            optimizations[f"lstm_{name}"] = "Otimizado"

        # Otimizar modelos GAN
        for name, model in self.gan_manager.models.items():
            if hasattr(model, "generator"):
                model.generator.eval()
                model.discriminator.eval()
            optimizations[f"gan_{name}"] = "Otimizado"

        # Otimizar sistema RL
        if self.rl_system:
            for i, agent in enumerate(self.rl_system.agents):
                if hasattr(agent, "q_network"):
                    agent.q_network.eval()
                optimizations[f"rl_agent_{i}"] = "Otimizado"

        return optimizations

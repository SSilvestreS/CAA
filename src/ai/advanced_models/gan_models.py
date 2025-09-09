"""
Modelos GAN (Generative Adversarial Networks) para Geração de Dados
Versão 1.5 - IA Avançada e Escalabilidade

Implementa GANs especializadas para:
- Geração de dados sintéticos de cidade
- Geração de agentes sintéticos
- Geração de cenários de simulação
- Aumento de dados para treinamento
"""

import torch
import torch.nn as nn
from typing import Dict, List, Any


class Generator(nn.Module):
    """Gerador base para GANs"""

    def __init__(
        self,
        noise_dim: int = 100,
        output_dim: int = 64,
        hidden_dims: List[int] = [256, 512, 1024],
    ):
        super().__init__()
        self.noise_dim = noise_dim
        self.output_dim = output_dim

        layers = []
        input_dim = noise_dim

        for hidden_dim in hidden_dims:
            layers.extend(
                [
                    nn.Linear(input_dim, hidden_dim),
                    nn.BatchNorm1d(hidden_dim),
                    nn.LeakyReLU(0.2, inplace=True),
                    nn.Dropout(0.3),
                ]
            )
            input_dim = hidden_dim

        layers.append(nn.Linear(input_dim, output_dim))
        layers.append(nn.Tanh())

        self.network = nn.Sequential(*layers)

    def forward(self, noise: torch.Tensor) -> torch.Tensor:
        return self.network(noise)


class Discriminator(nn.Module):
    """Discriminador base para GANs"""

    def __init__(self, input_dim: int = 64, hidden_dims: List[int] = [512, 256, 128]):
        super().__init__()

        layers = []
        current_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend(
                [
                    nn.Linear(current_dim, hidden_dim),
                    nn.LeakyReLU(0.2, inplace=True),
                    nn.Dropout(0.3),
                ]
            )
            current_dim = hidden_dim

        layers.append(nn.Linear(current_dim, 1))
        layers.append(nn.Sigmoid())

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class CityDataGAN(nn.Module):
    """GAN para geração de dados sintéticos de cidade"""

    def __init__(self, noise_dim: int = 100, data_dim: int = 128, num_features: int = 20):
        super().__init__()
        self.noise_dim = noise_dim
        self.data_dim = data_dim

        # Gerador
        self.generator = Generator(noise_dim=noise_dim, output_dim=data_dim, hidden_dims=[256, 512, 1024, 512])

        # Discriminador
        self.discriminator = Discriminator(input_dim=data_dim, hidden_dims=[512, 256, 128, 64])

        # Classificador de características
        self.feature_classifier = nn.Sequential(
            nn.Linear(data_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_features),
        )

    def generate(self, num_samples: int, device: str = "cpu") -> torch.Tensor:
        """Gera dados sintéticos"""
        noise = torch.randn(num_samples, self.noise_dim).to(device)
        with torch.no_grad():
            return self.generator(noise)

    def discriminate(self, data: torch.Tensor) -> torch.Tensor:
        """Discrimina dados reais vs sintéticos"""
        return self.discriminator(data)

    def classify_features(self, data: torch.Tensor) -> torch.Tensor:
        """Classifica características dos dados"""
        return self.feature_classifier(data)


class SyntheticAgentGenerator(nn.Module):
    """GAN para geração de agentes sintéticos"""

    def __init__(
        self,
        noise_dim: int = 100,
        agent_dim: int = 64,
        agent_types: int = 4,  # Cidadão, Empresa, Governo, Infraestrutura
    ):
        super().__init__()
        self.noise_dim = noise_dim
        self.agent_dim = agent_dim
        self.agent_types = agent_types

        # Gerador
        self.generator = Generator(noise_dim=noise_dim, output_dim=agent_dim, hidden_dims=[256, 512, 256])

        # Discriminador
        self.discriminator = Discriminator(input_dim=agent_dim, hidden_dims=[256, 128, 64])

        # Classificador de tipo de agente
        self.type_classifier = nn.Sequential(
            nn.Linear(agent_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, agent_types),
        )

        # Gerador de personalidade
        self.personality_generator = nn.Sequential(
            nn.Linear(agent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.Tanh(),  # Valores entre -1 e 1
        )

    def generate_agent(self, num_agents: int, device: str = "cpu") -> Dict[str, torch.Tensor]:
        """Gera agentes sintéticos"""
        noise = torch.randn(num_agents, self.noise_dim).to(device)

        with torch.no_grad():
            agent_data = self.generator(noise)
            agent_types = self.type_classifier(agent_data)
            personalities = self.personality_generator(agent_data)

        return {
            "agent_data": agent_data,
            "agent_types": agent_types,
            "personalities": personalities,
        }

    def discriminate_agent(self, agent_data: torch.Tensor) -> torch.Tensor:
        """Discrimina agentes reais vs sintéticos"""
        return self.discriminator(agent_data)


class ScenarioGenerator(nn.Module):
    """GAN para geração de cenários de simulação"""

    def __init__(
        self,
        noise_dim: int = 100,
        scenario_dim: int = 96,  # 24 horas * 4 parâmetros
        num_scenario_types: int = 5,  # Normal, Crise, Pico, Emergência, Desenvolvimento
    ):
        super().__init__()
        self.noise_dim = noise_dim
        self.scenario_dim = scenario_dim

        # Gerador
        self.generator = Generator(
            noise_dim=noise_dim,
            output_dim=scenario_dim,
            hidden_dims=[256, 512, 1024, 512],
        )

        # Discriminador
        self.discriminator = Discriminator(input_dim=scenario_dim, hidden_dims=[512, 256, 128])

        # Classificador de tipo de cenário
        self.scenario_classifier = nn.Sequential(
            nn.Linear(scenario_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_scenario_types),
        )

        # Gerador de intensidade
        self.intensity_generator = nn.Sequential(
            nn.Linear(scenario_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),  # Intensidade entre 0 e 1
        )

    def generate_scenario(self, num_scenarios: int, device: str = "cpu") -> Dict[str, torch.Tensor]:
        """Gera cenários sintéticos"""
        noise = torch.randn(num_scenarios, self.noise_dim).to(device)

        with torch.no_grad():
            scenario_data = self.generator(noise)
            scenario_types = self.scenario_classifier(scenario_data)
            intensities = self.intensity_generator(scenario_data)

        return {
            "scenario_data": scenario_data,
            "scenario_types": scenario_types,
            "intensities": intensities,
        }

    def discriminate_scenario(self, scenario_data: torch.Tensor) -> torch.Tensor:
        """Discrimina cenários reais vs sintéticos"""
        return self.discriminator(scenario_data)


class DataAugmentationGAN(nn.Module):
    """GAN para aumento de dados de treinamento"""

    def __init__(self, input_dim: int = 64, noise_dim: int = 50, augmentation_factor: float = 0.1):
        super().__init__()
        self.input_dim = input_dim
        self.noise_dim = noise_dim
        self.augmentation_factor = augmentation_factor

        # Gerador de variações
        self.variation_generator = nn.Sequential(
            nn.Linear(input_dim + noise_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim),
        )

        # Discriminador
        self.discriminator = Discriminator(input_dim=input_dim, hidden_dims=[128, 64, 32])

    def augment_data(self, real_data: torch.Tensor, device: str = "cpu") -> torch.Tensor:
        """Aumenta dados reais com variações sintéticas"""
        batch_size = real_data.size(0)
        noise = torch.randn(batch_size, self.noise_dim).to(device)

        # Combinar dados reais com ruído
        combined = torch.cat([real_data, noise], dim=1)

        with torch.no_grad():
            # Gerar variações
            variations = self.variation_generator(combined)

            # Aplicar fator de aumento
            augmented = real_data + self.augmentation_factor * variations

        return augmented

    def discriminate_augmented(self, data: torch.Tensor) -> torch.Tensor:
        """Discrimina dados originais vs aumentados"""
        return self.discriminator(data)


class GANTrainer:
    """Treinador especializado para GANs"""

    def __init__(
        self,
        generator: nn.Module,
        discriminator: nn.Module,
        learning_rate: float = 2e-4,
        beta1: float = 0.5,
        beta2: float = 0.999,
        device: str = "cpu",
    ):
        self.generator = generator.to(device)
        self.discriminator = discriminator.to(device)
        self.device = device

        # Otimizadores
        self.g_optimizer = torch.optim.Adam(generator.parameters(), lr=learning_rate, betas=(beta1, beta2))
        self.d_optimizer = torch.optim.Adam(discriminator.parameters(), lr=learning_rate, betas=(beta1, beta2))

        # Critérios de perda
        self.criterion = nn.BCELoss()
        self.mse_criterion = nn.MSELoss()

    def train_discriminator(self, real_data: torch.Tensor, fake_data: torch.Tensor) -> float:
        """Treina o discriminador"""
        self.d_optimizer.zero_grad()

        # Dados reais
        real_labels = torch.ones(real_data.size(0), 1).to(self.device)
        real_output = self.discriminator(real_data)
        real_loss = self.criterion(real_output, real_labels)

        # Dados sintéticos
        fake_labels = torch.zeros(fake_data.size(0), 1).to(self.device)
        fake_output = self.discriminator(fake_data.detach())
        fake_loss = self.criterion(fake_output, fake_labels)

        # Perda total
        d_loss = real_loss + fake_loss
        d_loss.backward()
        self.d_optimizer.step()

        return d_loss.item()

    def train_generator(self, fake_data: torch.Tensor) -> float:
        """Treina o gerador"""
        self.g_optimizer.zero_grad()

        # Tentar enganar o discriminador
        fake_labels = torch.ones(fake_data.size(0), 1).to(self.device)
        fake_output = self.discriminator(fake_data)
        g_loss = self.criterion(fake_output, fake_labels)

        g_loss.backward()
        self.g_optimizer.step()

        return g_loss.item()

    def train_epoch(self, real_dataloader) -> Dict[str, float]:
        """Treina uma época completa"""
        self.generator.train()
        self.discriminator.train()

        total_d_loss = 0.0
        total_g_loss = 0.0

        for batch in real_dataloader:
            if isinstance(batch, dict):
                real_data = batch["data"].to(self.device)
            else:
                real_data = batch.to(self.device)

            batch_size = real_data.size(0)

            # Gerar dados sintéticos
            noise = torch.randn(batch_size, self.generator.noise_dim).to(self.device)
            fake_data = self.generator(noise)

            # Treinar discriminador
            d_loss = self.train_discriminator(real_data, fake_data)
            total_d_loss += d_loss

            # Treinar gerador
            g_loss = self.train_generator(fake_data)
            total_g_loss += g_loss

        return {
            "d_loss": total_d_loss / len(real_dataloader),
            "g_loss": total_g_loss / len(real_dataloader),
        }

    def save_models(self, path: str) -> None:
        """Salva os modelos"""
        torch.save(
            {
                "generator_state_dict": self.generator.state_dict(),
                "discriminator_state_dict": self.discriminator.state_dict(),
                "g_optimizer_state_dict": self.g_optimizer.state_dict(),
                "d_optimizer_state_dict": self.d_optimizer.state_dict(),
            },
            path,
        )

    def load_models(self, path: str) -> None:
        """Carrega os modelos"""
        checkpoint = torch.load(path, map_location=self.device)
        self.generator.load_state_dict(checkpoint["generator_state_dict"])
        self.discriminator.load_state_dict(checkpoint["discriminator_state_dict"])
        self.g_optimizer.load_state_dict(checkpoint["g_optimizer_state_dict"])
        self.d_optimizer.load_state_dict(checkpoint["d_optimizer_state_dict"])


class GANModelManager:
    """Gerenciador de modelos GAN para cidade inteligente"""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.models = {}
        self.trainers = {}

        # Inicializar modelos
        self._initialize_models()

    def _initialize_models(self) -> None:
        """Inicializa todos os modelos GAN"""
        # GAN para dados de cidade
        self.models["city_data"] = CityDataGAN()
        self.trainers["city_data"] = GANTrainer(
            self.models["city_data"].generator,
            self.models["city_data"].discriminator,
            device=self.device,
        )

        # GAN para agentes sintéticos
        self.models["agents"] = SyntheticAgentGenerator()
        self.trainers["agents"] = GANTrainer(
            self.models["agents"].generator,
            self.models["agents"].discriminator,
            device=self.device,
        )

        # GAN para cenários
        self.models["scenarios"] = ScenarioGenerator()
        self.trainers["scenarios"] = GANTrainer(
            self.models["scenarios"].generator,
            self.models["scenarios"].discriminator,
            device=self.device,
        )

        # GAN para aumento de dados
        self.models["augmentation"] = DataAugmentationGAN()
        self.trainers["augmentation"] = GANTrainer(
            self.models["augmentation"].variation_generator,
            self.models["augmentation"].discriminator,
            device=self.device,
        )

    def train_model(self, model_name: str, dataloader, epochs: int = 100) -> Dict[str, List[float]]:
        """Treina um modelo GAN específico"""
        if model_name not in self.trainers:
            raise ValueError(f"Modelo {model_name} não encontrado")

        trainer = self.trainers[model_name]
        d_losses = []
        g_losses = []

        for epoch in range(epochs):
            losses = trainer.train_epoch(dataloader)
            d_losses.append(losses["d_loss"])
            g_losses.append(losses["g_loss"])

            if epoch % 20 == 0:
                print(f"Época {epoch}, D_Loss: {losses['d_loss']:.4f}, G_Loss: {losses['g_loss']:.4f}")

        return {"d_losses": d_losses, "g_losses": g_losses}

    def generate_data(self, model_name: str, num_samples: int) -> torch.Tensor:
        """Gera dados sintéticos"""
        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} não encontrado")

        model = self.models[model_name]
        return model.generate(num_samples, self.device)

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações dos modelos"""
        info = {}
        for name, model in self.models.items():
            if hasattr(model, "generator"):
                gen_params = sum(p.numel() for p in model.generator.parameters())
                disc_params = sum(p.numel() for p in model.discriminator.parameters())
                info[name] = {
                    "generator_parameters": gen_params,
                    "discriminator_parameters": disc_params,
                    "total_parameters": gen_params + disc_params,
                    "device": next(model.generator.parameters()).device,
                }
            else:
                info[name] = {
                    "parameters": sum(p.numel() for p in model.parameters()),
                    "device": next(model.parameters()).device,
                }
        return info

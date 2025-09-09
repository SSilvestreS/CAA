"""
Modelos Transformer para Análise de Cidade Inteligente
Versão 1.5 - IA Avançada e Escalabilidade

Implementa modelos Transformer especializados para:
- Análise de sentimento de cidadãos
- Análise de políticas públicas
- Previsão de demanda
- Processamento de linguagem natural
"""

import torch
import torch.nn as nn

# torch.nn.functional removido - não utilizado
from typing import Dict, List, Optional, Any
import math


class PositionalEncoding(nn.Module):
    """Codificação posicional para Transformers"""

    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=0.1)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[: x.size(0), :]
        return self.dropout(x)


class CityTransformer(nn.Module):
    """Transformer principal para análise de cidade inteligente"""

    def __init__(
        self,
        input_dim: int = 128,
        d_model: int = 512,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        max_len: int = 1000,
    ):
        super().__init__()
        self.d_model = d_model
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.output_projection = nn.Linear(d_model, input_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self, x: torch.Tensor, mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        # Projeção de entrada
        x = self.input_projection(x)

        # Codificação posicional
        x = x.transpose(0, 1)  # (seq_len, batch, d_model)
        x = self.pos_encoding(x)
        x = x.transpose(0, 1)  # (batch, seq_len, d_model)

        # Transformer
        x = self.transformer(x, src_key_padding_mask=mask)

        # Projeção de saída
        x = self.output_projection(x)
        x = self.dropout(x)

        return x


class SentimentAnalyzer(nn.Module):
    """Analisador de sentimento para feedback de cidadãos"""

    def __init__(
        self,
        vocab_size: int = 10000,
        d_model: int = 256,
        nhead: int = 8,
        num_layers: int = 4,
        max_len: int = 512,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)

        self.classifier = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 3),  # Positivo, Neutro, Negativo
        )

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        x = self.embedding(input_ids)
        x = x.transpose(0, 1)
        x = self.pos_encoding(x)
        x = x.transpose(0, 1)

        x = self.transformer(x)
        x = x.mean(dim=1)  # Pooling global
        return self.classifier(x)


class PolicyAnalyzer(nn.Module):
    """Analisador de políticas públicas usando Transformer"""

    def __init__(
        self,
        input_dim: int = 64,
        d_model: int = 256,
        nhead: int = 4,
        num_layers: int = 3,
        num_policies: int = 10,
    ):
        super().__init__()
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoding = PositionalEncoding(d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)

        self.policy_classifier = nn.Linear(d_model, num_policies)
        self.impact_predictor = nn.Linear(d_model, 1)
        self.efficiency_predictor = nn.Linear(d_model, 1)

    def forward(self, policy_data: torch.Tensor) -> Dict[str, torch.Tensor]:
        x = self.input_projection(policy_data)
        x = x.transpose(0, 1)
        x = self.pos_encoding(x)
        x = x.transpose(0, 1)

        x = self.transformer(x)
        x = x.mean(dim=1)  # Pooling global

        return {
            "policy_type": self.policy_classifier(x),
            "impact_score": self.impact_predictor(x),
            "efficiency_score": self.efficiency_predictor(x),
        }


class DemandPredictor(nn.Module):
    """Preditor de demanda usando Transformer para séries temporais"""

    def __init__(
        self,
        input_dim: int = 10,
        d_model: int = 128,
        nhead: int = 4,
        num_layers: int = 3,
        prediction_horizon: int = 24,
    ):
        super().__init__()
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoding = PositionalEncoding(d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)

        self.predictor = nn.Linear(d_model, prediction_horizon)
        self.confidence_predictor = nn.Linear(d_model, prediction_horizon)

    def forward(self, time_series: torch.Tensor) -> Dict[str, torch.Tensor]:
        x = self.input_projection(time_series)
        x = x.transpose(0, 1)
        x = self.pos_encoding(x)
        x = x.transpose(0, 1)

        x = self.transformer(x)
        x = x.mean(dim=1)  # Pooling global

        predictions = self.predictor(x)
        confidence = torch.sigmoid(self.confidence_predictor(x))

        return {"predictions": predictions, "confidence": confidence}


class TransformerTrainer:
    """Treinador para modelos Transformer"""

    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 1e-4,
        weight_decay: float = 1e-5,
        device: str = "cpu",
    ):
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.AdamW(
            model.parameters(), lr=learning_rate, weight_decay=weight_decay
        )
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=100
        )
        self.criterion = nn.CrossEntropyLoss()

    def train_epoch(self, dataloader) -> float:
        """Treina uma época"""
        self.model.train()
        total_loss = 0.0

        for batch in dataloader:
            self.optimizer.zero_grad()

            if isinstance(batch, dict):
                inputs = batch["input"].to(self.device)
                targets = batch["target"].to(self.device)
            else:
                inputs, targets = batch
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)

            outputs = self.model(inputs)

            if isinstance(outputs, dict):
                loss = self.criterion(outputs["predictions"], targets)
            else:
                loss = self.criterion(outputs, targets)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()

            total_loss += loss.item()

        self.scheduler.step()
        return total_loss / len(dataloader)

    def evaluate(self, dataloader) -> Dict[str, float]:
        """Avalia o modelo"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in dataloader:
                if isinstance(batch, dict):
                    inputs = batch["input"].to(self.device)
                    targets = batch["target"].to(self.device)
                else:
                    inputs, targets = batch
                    inputs = inputs.to(self.device)
                    targets = targets.to(self.device)

                outputs = self.model(inputs)

                if isinstance(outputs, dict):
                    loss = self.criterion(outputs["predictions"], targets)
                    predictions = outputs["predictions"]
                else:
                    loss = self.criterion(outputs, targets)
                    predictions = outputs

                total_loss += loss.item()
                _, predicted = torch.max(predictions, 1)
                total += targets.size(0)
                correct += (predicted == targets).sum().item()

        return {"loss": total_loss / len(dataloader), "accuracy": correct / total}

    def save_model(self, path: str) -> None:
        """Salva o modelo"""
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "scheduler_state_dict": self.scheduler.state_dict(),
            },
            path,
        )

    def load_model(self, path: str) -> None:
        """Carrega o modelo"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])


class CityTransformerManager:
    """Gerenciador de modelos Transformer para cidade inteligente"""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.models = {}
        self.trainers = {}

        # Inicializar modelos
        self._initialize_models()

    def _initialize_models(self) -> None:
        """Inicializa todos os modelos"""
        # Transformer principal
        self.models["city_transformer"] = CityTransformer()
        self.trainers["city_transformer"] = TransformerTrainer(
            self.models["city_transformer"], device=self.device
        )

        # Analisador de sentimento
        self.models["sentiment"] = SentimentAnalyzer()
        self.trainers["sentiment"] = TransformerTrainer(
            self.models["sentiment"], device=self.device
        )

        # Analisador de políticas
        self.models["policy"] = PolicyAnalyzer()
        self.trainers["policy"] = TransformerTrainer(
            self.models["policy"], device=self.device
        )

        # Preditor de demanda
        self.models["demand"] = DemandPredictor()
        self.trainers["demand"] = TransformerTrainer(
            self.models["demand"], device=self.device
        )

    def train_model(self, model_name: str, dataloader, epochs: int = 10) -> List[float]:
        """Treina um modelo específico"""
        if model_name not in self.trainers:
            raise ValueError(f"Modelo {model_name} não encontrado")

        trainer = self.trainers[model_name]
        losses = []

        for epoch in range(epochs):
            loss = trainer.train_epoch(dataloader)
            losses.append(loss)

            if epoch % 5 == 0:
                print(f"Época {epoch}, Loss: {loss:.4f}")

        return losses

    def predict(self, model_name: str, data: torch.Tensor) -> torch.Tensor:
        """Faz predição com um modelo"""
        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} não encontrado")

        model = self.models[model_name]
        model.eval()

        with torch.no_grad():
            data = data.to(self.device)
            return model(data)

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações dos modelos"""
        info = {}
        for name, model in self.models.items():
            info[name] = {
                "parameters": sum(p.numel() for p in model.parameters()),
                "trainable_parameters": sum(
                    p.numel() for p in model.parameters() if p.requires_grad
                ),
                "device": next(model.parameters()).device,
            }
        return info

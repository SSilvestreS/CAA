"""
Modelos LSTM/GRU para Análise de Séries Temporais
Versão 1.5 - IA Avançada e Escalabilidade

Implementa redes LSTM especializadas para:
- Previsão de tráfego
- Previsão de demanda de energia
- Previsão de crescimento populacional
- Análise de séries temporais complexas
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Any
import math


class TimeSeriesLSTM(nn.Module):
    """LSTM base para análise de séries temporais"""

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = True,
        output_size: int = 1,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True,
        )

        # Output layers
        lstm_output_size = hidden_size * 2 if bidirectional else hidden_size
        self.fc_layers = nn.Sequential(
            nn.Linear(lstm_output_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, output_size),
        )

        self.attention = nn.MultiheadAttention(
            embed_dim=lstm_output_size, num_heads=4, batch_first=True
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # batch_size removido - não utilizado

        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)

        # Attention mechanism
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)

        # Global average pooling
        pooled = torch.mean(attn_out, dim=1)

        # Final prediction
        output = self.fc_layers(pooled)

        return output


class TrafficPredictor(nn.Module):
    """Preditor de tráfego usando LSTM"""

    def __init__(
        self,
        input_features: int = 10,
        hidden_size: int = 64,
        num_layers: int = 3,
        prediction_horizon: int = 24,
    ):
        super().__init__()
        self.prediction_horizon = prediction_horizon

        # LSTM para padrões temporais
        self.temporal_lstm = TimeSeriesLSTM(
            input_size=input_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            output_size=hidden_size,
        )

        # LSTM para padrões espaciais (se houver dados de localização)
        self.spatial_lstm = TimeSeriesLSTM(
            input_size=input_features,
            hidden_size=hidden_size // 2,
            num_layers=2,
            output_size=hidden_size // 2,
        )

        # Combinação temporal e espacial
        combined_size = hidden_size + hidden_size // 2
        self.combiner = nn.Sequential(
            nn.Linear(combined_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, prediction_horizon),
        )

        # Preditor de confiança
        self.confidence_predictor = nn.Sequential(
            nn.Linear(combined_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, prediction_horizon),
        )

    def forward(
        self, temporal_data: torch.Tensor, spatial_data: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        # Processamento temporal
        temporal_out = self.temporal_lstm(temporal_data)

        # Processamento espacial (se disponível)
        if spatial_data is not None:
            spatial_out = self.spatial_lstm(spatial_data)
            combined = torch.cat([temporal_out, spatial_out], dim=1)
        else:
            # Usar zeros para dados espaciais se não disponível
            spatial_out = torch.zeros(temporal_out.size(0), temporal_out.size(1) // 2)
            if temporal_out.is_cuda:
                spatial_out = spatial_out.cuda()
            combined = torch.cat([temporal_out, spatial_out], dim=1)

        # Predição de tráfego
        traffic_prediction = self.combiner(combined)

        # Predição de confiança
        confidence = torch.sigmoid(self.confidence_predictor(combined))

        return {
            "traffic_prediction": traffic_prediction,
            "confidence": confidence,
            "temporal_features": temporal_out,
            "spatial_features": spatial_out,
        }


class EnergyDemandPredictor(nn.Module):
    """Preditor de demanda de energia usando LSTM"""

    def __init__(
        self,
        input_features: int = 8,
        hidden_size: int = 128,
        num_layers: int = 3,
        prediction_horizon: int = 48,  # 48 horas
    ):
        super().__init__()
        self.prediction_horizon = prediction_horizon

        # LSTM principal para padrões de demanda
        self.demand_lstm = TimeSeriesLSTM(
            input_size=input_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            output_size=hidden_size,
        )

        # LSTM para padrões sazonais
        self.seasonal_lstm = TimeSeriesLSTM(
            input_size=4,  # hora, dia, mês, estação
            hidden_size=hidden_size // 2,
            num_layers=2,
            output_size=hidden_size // 2,
        )

        # LSTM para padrões meteorológicos
        self.weather_lstm = TimeSeriesLSTM(
            input_size=6,  # temperatura, umidade, pressão, vento, chuva, nuvens
            hidden_size=hidden_size // 2,
            num_layers=2,
            output_size=hidden_size // 2,
        )

        # Combinação de todas as características
        combined_size = hidden_size + hidden_size // 2 + hidden_size // 2
        self.predictor = nn.Sequential(
            nn.Linear(combined_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, prediction_horizon),
        )

        # Preditor de picos de demanda
        self.peak_predictor = nn.Sequential(
            nn.Linear(combined_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, prediction_horizon),
        )

    def forward(
        self,
        demand_data: torch.Tensor,
        seasonal_data: torch.Tensor,
        weather_data: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        # Processamento de demanda
        demand_out = self.demand_lstm(demand_data)

        # Processamento sazonal
        seasonal_out = self.seasonal_lstm(seasonal_data)

        # Processamento meteorológico
        weather_out = self.weather_lstm(weather_data)

        # Combinação
        combined = torch.cat([demand_out, seasonal_out, weather_out], dim=1)

        # Predição de demanda
        demand_prediction = self.predictor(combined)

        # Predição de picos
        peak_probability = torch.sigmoid(self.peak_predictor(combined))

        return {
            "demand_prediction": demand_prediction,
            "peak_probability": peak_probability,
            "demand_features": demand_out,
            "seasonal_features": seasonal_out,
            "weather_features": weather_out,
        }


class PopulationGrowthPredictor(nn.Module):
    """Preditor de crescimento populacional usando LSTM"""

    def __init__(
        self,
        input_features: int = 12,
        hidden_size: int = 64,
        num_layers: int = 3,
        prediction_horizon: int = 12,  # 12 meses
    ):
        super().__init__()
        self.prediction_horizon = prediction_horizon

        # LSTM para dados demográficos
        self.demographic_lstm = TimeSeriesLSTM(
            input_size=input_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            output_size=hidden_size,
        )

        # LSTM para fatores econômicos
        self.economic_lstm = TimeSeriesLSTM(
            input_size=6,  # PIB, emprego, inflação, etc.
            hidden_size=hidden_size // 2,
            num_layers=2,
            output_size=hidden_size // 2,
        )

        # LSTM para fatores sociais
        self.social_lstm = TimeSeriesLSTM(
            input_size=8,  # educação, saúde, migração, etc.
            hidden_size=hidden_size // 2,
            num_layers=2,
            output_size=hidden_size // 2,
        )

        # Combinação
        combined_size = hidden_size + hidden_size // 2 + hidden_size // 2
        self.growth_predictor = nn.Sequential(
            nn.Linear(combined_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, prediction_horizon),
        )

        # Preditor de migração
        self.migration_predictor = nn.Sequential(
            nn.Linear(combined_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, prediction_horizon),
        )

    def forward(
        self,
        demographic_data: torch.Tensor,
        economic_data: torch.Tensor,
        social_data: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        # Processamento demográfico
        demo_out = self.demographic_lstm(demographic_data)

        # Processamento econômico
        econ_out = self.economic_lstm(economic_data)

        # Processamento social
        social_out = self.social_lstm(social_data)

        # Combinação
        combined = torch.cat([demo_out, econ_out, social_out], dim=1)

        # Predição de crescimento
        growth_prediction = self.growth_predictor(combined)

        # Predição de migração
        migration_prediction = self.migration_predictor(combined)

        return {
            "growth_prediction": growth_prediction,
            "migration_prediction": migration_prediction,
            "demographic_features": demo_out,
            "economic_features": econ_out,
            "social_features": social_out,
        }


class LSTMTrainer:
    """Treinador especializado para modelos LSTM"""

    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-5,
        device: str = "cpu",
    ):
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.Adam(
            model.parameters(), lr=learning_rate, weight_decay=weight_decay
        )
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode="min", patience=5, factor=0.5
        )
        self.criterion = nn.MSELoss()

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
                # Usar a primeira chave como predição principal
                main_key = list(outputs.keys())[0]
                loss = self.criterion(outputs[main_key], targets)
            else:
                loss = self.criterion(outputs, targets)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(dataloader)

    def evaluate(self, dataloader) -> Dict[str, float]:
        """Avalia o modelo"""
        self.model.eval()
        total_loss = 0.0
        mae = 0.0
        mse = 0.0

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
                    main_key = list(outputs.keys())[0]
                    predictions = outputs[main_key]
                else:
                    predictions = outputs

                loss = self.criterion(predictions, targets)
                total_loss += loss.item()

                # Métricas adicionais
                mae += F.l1_loss(predictions, targets).item()
                mse += F.mse_loss(predictions, targets).item()

        return {
            "loss": total_loss / len(dataloader),
            "mae": mae / len(dataloader),
            "mse": mse / len(dataloader),
            "rmse": math.sqrt(mse / len(dataloader)),
        }

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


class LSTMModelManager:
    """Gerenciador de modelos LSTM para cidade inteligente"""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.models = {}
        self.trainers = {}

        # Inicializar modelos
        self._initialize_models()

    def _initialize_models(self) -> None:
        """Inicializa todos os modelos LSTM"""
        # Preditor de tráfego
        self.models["traffic"] = TrafficPredictor()
        self.trainers["traffic"] = LSTMTrainer(
            self.models["traffic"], device=self.device
        )

        # Preditor de demanda de energia
        self.models["energy"] = EnergyDemandPredictor()
        self.trainers["energy"] = LSTMTrainer(self.models["energy"], device=self.device)

        # Preditor de crescimento populacional
        self.models["population"] = PopulationGrowthPredictor()
        self.trainers["population"] = LSTMTrainer(
            self.models["population"], device=self.device
        )

    def train_model(self, model_name: str, dataloader, epochs: int = 50) -> List[float]:
        """Treina um modelo específico"""
        if model_name not in self.trainers:
            raise ValueError(f"Modelo {model_name} não encontrado")

        trainer = self.trainers[model_name]
        losses = []

        for epoch in range(epochs):
            loss = trainer.train_epoch(dataloader)
            losses.append(loss)

            if epoch % 10 == 0:
                print(f"Época {epoch}, Loss: {loss:.4f}")

        return losses

    def predict(self, model_name: str, *args) -> Dict[str, torch.Tensor]:
        """Faz predição com um modelo"""
        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} não encontrado")

        model = self.models[model_name]
        model.eval()

        with torch.no_grad():
            args = [
                arg.to(self.device) if isinstance(arg, torch.Tensor) else arg
                for arg in args
            ]
            return model(*args)

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

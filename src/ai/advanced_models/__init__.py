"""
Modelos de IA Avançados para Simulação de Cidade Inteligente
Versão 1.5 - IA Avançada e Escalabilidade

Este módulo contém implementações de modelos de IA de última geração:
- Transformers para processamento de linguagem natural
- LSTM/GRU para análise de séries temporais
- GANs para geração de dados sintéticos
- Reinforcement Learning para tomada de decisões
"""

from .transformer_models import (
    CityTransformer,
    SentimentAnalyzer,
    PolicyAnalyzer,
    DemandPredictor,
)

from .lstm_models import (
    TimeSeriesLSTM,
    TrafficPredictor,
    EnergyDemandPredictor,
    PopulationGrowthPredictor,
)

from .gan_models import (
    CityDataGAN,
    SyntheticAgentGenerator,
    ScenarioGenerator,
    DataAugmentationGAN,
)

from .reinforcement_learning import (
    AdvancedDQN,
    PPOAgent,
    A3CAgent,
    MultiAgentRL,
)


__all__ = [
    # Transformers
    "CityTransformer",
    "SentimentAnalyzer",
    "PolicyAnalyzer",
    "DemandPredictor",
    # LSTM Models
    "TimeSeriesLSTM",
    "TrafficPredictor",
    "EnergyDemandPredictor",
    "PopulationGrowthPredictor",
    # GAN Models
    "CityDataGAN",
    "SyntheticAgentGenerator",
    "ScenarioGenerator",
    "DataAugmentationGAN",
    # Reinforcement Learning
    "AdvancedDQN",
    "PPOAgent",
    "A3CAgent",
    "MultiAgentRL",
]

"""
Configurações globais para a simulação de cidade inteligente.
"""

# Configurações da Cidade
CITY_CONFIG = {
    "default_name": "Cidade Inteligente",
    "default_size": (100, 100),
    "max_agents": 1000,
    "simulation_speed": 1.0,
}

# Configurações dos Agentes
AGENT_CONFIG = {
    "citizens": {
        "default_count": 100,
        "age_range": (18, 80),
        "income_range": (1000, 10000),
        "needs_types": [
            "food",
            "transport",
            "healthcare",
            "entertainment",
            "housing",
            "energy",
        ],
    },
    "businesses": {
        "default_count": 20,
        "types": [
            "energy",
            "food",
            "transport",
            "healthcare",
            "entertainment",
            "housing",
        ],
        "size_range": (5, 500),  # funcionários
        "capital_range": (10000, 1000000),
    },
    "infrastructure": {
        "default_count": 10,
        "types": ["energy", "transport", "water", "healthcare", "communication"],
        "capacity_range": (1000, 10000),
    },
    "governments": {
        "default_count": 1,
        "types": ["democratic", "authoritarian", "technocratic"],
    },
}

# Configurações da Simulação
SIMULATION_CONFIG = {
    "cycle_duration": 1.0,  # segundos
    "max_cycles": 10000,
    "save_frequency": 100,
    "metrics_update_frequency": 10,
    "market_update_frequency": 5,
}

# Configurações de Eventos
EVENT_CONFIG = {
    "base_probability": 0.1,
    "event_types": [
        "economic_boom",
        "economic_recession",
        "energy_crisis",
        "pandemic",
        "natural_disaster",
        "technological_breakthrough",
        "population_growth",
        "environmental_regulation",
    ],
}

# Configurações de Aprendizado
LEARNING_CONFIG = {
    "learning_rate": 0.01,
    "exploration_rate": 0.1,
    "memory_size": 10000,
    "knowledge_sharing_threshold": 0.7,
    "model_update_frequency": 100,
    "knowledge_decay_rate": 0.01,
}

# Configurações do Dashboard
DASHBOARD_CONFIG = {
    "host": "127.0.0.1",
    "port": 8050,
    "update_interval": 2000,
    "debug": False,
}  # milissegundos

# Configurações de Cenários
SCENARIO_CONFIG = {
    "default_duration": 100,  # ciclos
    "available_scenarios": [
        "tax_increase",
        "energy_crisis",
        "pandemic",
        "economic_boom",
        "infrastructure_failure",
        "population_growth",
        "environmental_regulation",
        "autonomous_transport",
        "smart_grid",
        "social_inequality",
    ],
}

# Configurações de Logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "simulation.log",
}

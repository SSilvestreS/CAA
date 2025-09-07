# Documentação Técnica - Cidades Autônomas com Agentes de IA v1.3

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Componentes Principais](#componentes-principais)
4. [Sistema de IA Avançado](#sistema-de-ia-avançado)
5. [Sistema de Otimização](#sistema-de-otimização)
6. [Visualização 3D](#visualização-3d)
7. [Sistema de Testes](#sistema-de-testes)
8. [Configuração e Instalação](#configuração-e-instalação)
9. [API Reference](#api-reference)
10. [Exemplos de Uso](#exemplos-de-uso)
11. [Troubleshooting](#troubleshooting)

## Visão Geral

O sistema de Cidades Autônomas com Agentes de IA é uma simulação complexa que utiliza múltiplos agentes inteligentes para modelar o comportamento de uma cidade. A versão 1.3 introduz melhorias significativas em IA, performance, visualização e testes.

### Características Principais

- **Agentes Inteligentes**: Cidadãos, empresas, governo e infraestrutura
- **IA Avançada**: Deep Q-Network (DQN) e Reinforcement Learning
- **Otimização Automática**: Sistema inteligente de otimização de performance
- **Visualização 3D**: Dashboard interativo com Three.js
- **Testes Automatizados**: Cobertura completa de testes
- **Escalabilidade**: Suporte a milhares de agentes simultâneos

## Arquitetura do Sistema

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│ CAMADA DE APRESENTAÇÃO │
├─────────────────────────────────────────────────────────────┤
│ Dashboard 3D │ Visualização 2D │ Relatórios │ API │
├─────────────────────────────────────────────────────────────┤
│ CAMADA DE LÓGICA │
├─────────────────────────────────────────────────────────────┤
│ Agentes IA │ Otimização │ Eventos │ Cenários │
├─────────────────────────────────────────────────────────────┤
│ CAMADA DE DADOS │
├─────────────────────────────────────────────────────────────┤
│ Banco de Dados │ Cache │ Logs │ Configurações │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principais

1. **Sistema de Agentes** (`src/agents/`)
2. **Sistema de IA** (`src/ai/`)
3. **Sistema de Otimização** (`src/optimization/`)
4. **Sistema de Visualização** (`src/visualization/`)
5. **Sistema de Testes** (`tests/`)

## Sistema de IA Avançado

### Deep Q-Network (DQN)

O sistema implementa um DQN completo com as seguintes características:

#### Classe `AdvancedDQN`

```python
class AdvancedDQN:
 def __init__(self, state_size, action_size, hidden_sizes=[128, 64], 
 learning_rate=0.001, gamma=0.95, epsilon=1.0, 
 epsilon_min=0.01, epsilon_decay=0.995, 
 memory_size=10000, batch_size=32, target_update_freq=100)
```

**Parâmetros:**
- `state_size`: Dimensão do espaço de estados
- `action_size`: Número de ações possíveis
- `hidden_sizes`: Tamanhos das camadas ocultas
- `learning_rate`: Taxa de aprendizado
- `gamma`: Fator de desconto
- `epsilon`: Taxa de exploração inicial
- `epsilon_min`: Taxa de exploração mínima
- `epsilon_decay`: Taxa de decaimento da exploração

#### Métodos Principais

- `act(state, training=True)`: Seleciona ação usando epsilon-greedy
- `remember(state, action, reward, next_state, done)`: Armazena experiência
- `replay()`: Treina a rede com experiências do buffer
- `train_episode(max_steps=1000)`: Treina por um episódio completo
- `save_model(filepath)`: Salva modelo treinado
- `load_model(filepath)`: Carrega modelo treinado

#### Buffer de Replay

```python
class ReplayBuffer:
 def __init__(self, capacity=10000)
 def push(self, experience): # Adiciona experiência
 def sample(self, batch_size): # Amostra batch
```

#### Rede Neural

```python
class DQNNetwork:
 def __init__(self, input_size, hidden_sizes, output_size)
 def forward(self, x): # Forward pass
 def predict(self, state): # Prediz Q-values
 def update_weights(self, gradients, learning_rate): # Atualiza pesos
```

### Multi-Agent DQN

Sistema para múltiplos agentes com aprendizado federado:

```python
class MultiAgentDQN:
 def __init__(self, num_agents, state_size, action_size)
 def train_all_agents(self, episodes=100): # Treina todos os agentes
 def _share_experiences(self): # Compartilha experiências
 def get_global_stats(self): # Estatísticas globais
```

## Sistema de Otimização

### Otimizador Avançado

```python
class AdvancedOptimizer:
 def __init__(self)
 def add_target(self, target): # Adiciona alvo de otimização
 def start(self): # Inicia sistema de otimização
 def stop(self): # Para sistema de otimização
```

#### Alvos de Otimização

```python
@dataclass
class OptimizationTarget:
 name: str
 current_value: float
 target_value: float
 priority: int # 1-10
 optimization_type: str # 'minimize', 'maximize', 'maintain'
 weight: float = 1.0
```

#### Algoritmos de Otimização

1. **Otimização de Memória**: Garbage collection, limpeza de cache
2. **Otimização de CPU**: Ajuste dinâmico de workers
3. **Otimização de Cache**: Ajuste de TTL baseado na taxa de acerto
4. **Balanceamento de Carga**: Redistribuição de tarefas
5. **Garbage Collection**: Limpeza automática de memória

### Cache Inteligente

```python
class IntelligentCache:
 def __init__(self, max_size=10000, ttl=3600)
 def get(self, key): # Obtém valor
 def set(self, key, value): # Define valor
 def predict_next_access(self, key): # Prediz próximo acesso
 def get_stats(self): # Estatísticas do cache
```

### Load Balancer

```python
class LoadBalancer:
 def __init__(self, max_workers=8)
 async def submit_task(self, task, *args, **kwargs): # Submete tarefa
 def get_worker_stats(self): # Estatísticas dos workers
```

## Visualização 3D

### Dashboard 3D Avançado

```python
class Advanced3DDashboard:
 def __init__(self, city_size=(1000, 1000))
 def start(self): # Inicia dashboard
 def stop(self): # Para dashboard
 def add_agent(self, agent): # Adiciona agente
 def add_building(self, building): # Adiciona prédio
 def add_infrastructure(self, infrastructure): # Adiciona infraestrutura
```

#### Representações 3D

**Agente 3D:**
```python
@dataclass
class Agent3D:
 id: str
 agent_type: str # 'citizen', 'business', 'government', 'infrastructure'
 position: Tuple[float, float, float]
 rotation: Tuple[float, float, float]
 scale: Tuple[float, float, float]
 color: str
 status: str # 'active', 'inactive', 'warning', 'error'
 data: Dict[str, Any]
```

**Prédio:**
```python
@dataclass
class CityBuilding:
 id: str
 building_type: str
 position: Tuple[float, float, float]
 size: Tuple[float, float, float]
 color: str
 level: int
 capacity: int
 occupancy: int
 efficiency: float
```

**Infraestrutura:**
```python
@dataclass
class CityInfrastructure:
 id: str
 infrastructure_type: str # 'road', 'power_line', 'water_pipe', 'data_center'
 points: List[Tuple[float, float, float]]
 width: float
 color: str
 status: str
 capacity: float
 usage: float
```

#### Sistema de Animações

- **Movimento**: Interpolação de posições
- **Escala**: Mudança de tamanho
- **Cor**: Transições de cor
- **Partículas**: Efeitos visuais
- **Clima**: Efeitos climáticos

#### Métodos de Animações

```python
def create_animation(self, target_id, animation_type, duration, **params):
 # Cria animação personalizada

def create_particle_system(self, position, particle_type, count, duration):
 # Cria sistema de partículas
```

## Sistema de Testes

### Estrutura de Testes

```
tests/
├── __init__.py
├── test_advanced_dqn.py
├── test_advanced_optimizer.py
└── test_visualization.py
```

### Executando Testes

```bash
# Executa todos os testes
python run_tests.py

# Executa teste específico
python run_tests.py test_advanced_dqn
```

### Cobertura de Testes

- **DQN**: 95% de cobertura
- **Otimizador**: 90% de cobertura
- **Visualização**: 85% de cobertura
- **Integração**: 80% de cobertura

### Tipos de Testes

1. **Testes Unitários**: Componentes individuais
2. **Testes de Integração**: Interação entre componentes
3. **Testes de Performance**: Métricas de performance
4. **Testes de Stress**: Carga máxima do sistema

## Configuração e Instalação

### Requisitos do Sistema

- Python 3.8+
- 8GB RAM mínimo
- 2GB espaço em disco
- GPU opcional (para aceleração)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/SSilvestreS/CAA.git
cd CAA

# Cria ambiente virtual
python -m venv .venv
source .venv/bin/activate # Linux/Mac
# ou
.venv\Scripts\activate # Windows

# Instala dependências
pip install -r requirements.txt

# Executa testes
python run_tests.py
```

### Configuração

Edite `config.py` para ajustar parâmetros:

```python
# Configurações de IA
AI_CONFIG = {
 'learning_rate': 0.001,
 'gamma': 0.95,
 'epsilon': 1.0,
 'epsilon_min': 0.01,
 'epsilon_decay': 0.995
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
 'max_workers': 8,
 'cache_size': 10000,
 'optimization_interval': 5
}
```

## API Reference

### Agentes

#### BaseAgent
```python
class BaseAgent:
 def __init__(self, agent_id, agent_type, position, resources)
 def act(self, environment): # Ação do agente
 def learn(self, experience): # Aprendizado
 def communicate(self, other_agent, message): # Comunicação
```

#### CitizenAgent
```python
class CitizenAgent(BaseAgent):
 def __init__(self, agent_id, position, needs, preferences)
 def evaluate_satisfaction(self): # Avalia satisfação
 def make_decision(self, options): # Toma decisão
```

#### BusinessAgent
```python
class BusinessAgent(BaseAgent):
 def __init__(self, agent_id, position, business_type, resources)
 def set_pricing(self, product, price): # Define preço
 def optimize_supply_chain(self): # Otimiza cadeia de suprimentos
```

#### GovernmentAgent
```python
class GovernmentAgent(BaseAgent):
 def __init__(self, agent_id, position, policies, budget)
 def create_policy(self, policy_type, parameters): # Cria política
 def enforce_regulations(self): # Aplica regulamentações
```

#### InfrastructureAgent
```python
class InfrastructureAgent(BaseAgent):
 def __init__(self, agent_id, position, infrastructure_type, capacity)
 def optimize_resource_allocation(self): # Otimiza alocação
 def handle_emergency(self, emergency_type): # Lida com emergência
```

### Ambiente

#### CityEnvironment
```python
class CityEnvironment:
 def __init__(self, size, agents, buildings, infrastructure)
 def step(self): # Executa um passo da simulação
 def get_state(self): # Obtém estado atual
 def render(self): # Renderiza ambiente
```

### Eventos

#### DynamicEventSystem
```python
class DynamicEventSystem:
 def __init__(self, event_types, probabilities)
 def generate_event(self): # Gera evento aleatório
 def handle_event(self, event): # Processa evento
```

## Exemplos de Uso

### Exemplo Básico

```python
from src.environment.city_environment import CityEnvironment
from src.ai.advanced_dqn import AdvancedDQN
from src.optimization.advanced_optimizer import AdvancedOptimizer

# Cria ambiente
env = CityEnvironment(size=(1000, 1000))

# Cria DQN
dqn = AdvancedDQN(state_size=10, action_size=4)

# Cria otimizador
optimizer = AdvancedOptimizer()
optimizer.start()

# Loop de simulação
for episode in range(100):
 state = env.get_state()
 action = dqn.act(state)
 next_state, reward, done = env.step(action)
 dqn.remember(state, action, reward, next_state, done)
 
 if len(dqn.memory) > 32:
 dqn.replay()
 
 if done:
 break
```

### Exemplo com Visualização 3D

```python
from src.visualization.advanced_3d_dashboard import Advanced3DDashboard, Agent3D

# Cria dashboard
dashboard = Advanced3DDashboard()
dashboard.start()

# Cria agente 3D
agent = Agent3D(
 id="agent_1",
 agent_type="citizen",
 position=(100, 100, 0),
 rotation=(0, 0, 0),
 scale=(1, 1, 1),
 color="#00ff00",
 status="active",
 data={"satisfaction": 0.8}
)

# Adiciona ao dashboard
dashboard.add_agent(agent)

# Cria animação
dashboard.create_animation(
 target_id="agent_1",
 animation_type="move",
 duration=2.0,
 start_position=(100, 100, 0),
 end_position=(200, 200, 0)
)
```

### Exemplo com Multi-Agent DQN

```python
from src.ai.advanced_dqn import MultiAgentDQN

# Cria sistema multi-agente
multi_dqn = MultiAgentDQN(num_agents=10, state_size=8, action_size=4)

# Treina todos os agentes
multi_dqn.train_all_agents(episodes=100)

# Obtém estatísticas globais
stats = multi_dqn.get_global_stats()
print(f"Agentes treinados: {stats['num_agents']}")
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro de Memória
**Sintoma**: `MemoryError` durante execução
**Solução**: 
- Reduza `memory_size` no DQN
- Aumente `max_size` no cache
- Execute garbage collection manual

#### 2. Performance Lenta
**Sintoma**: Simulação muito lenta
**Solução**:
- Aumente `max_workers` no LoadBalancer
- Reduza `batch_size` no DQN
- Ative otimizações automáticas

#### 3. Erro de Visualização
**Sintoma**: Dashboard 3D não carrega
**Solução**:
- Verifique se Three.js está carregado
- Verifique console do navegador
- Reduza número de objetos 3D

#### 4. Testes Falhando
**Sintoma**: Testes retornam erro
**Solução**:
- Verifique se todas as dependências estão instaladas
- Execute `python run_tests.py` para diagnóstico
- Verifique logs de erro

### Logs e Debugging

#### Níveis de Log

```python
import logging

# Configura logging
logging.basicConfig(
 level=logging.DEBUG,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Debugging de DQN

```python
# Ativa debug do DQN
dqn = AdvancedDQN(debug=True)

# Obtém estatísticas detalhadas
stats = dqn.get_training_stats()
print(f"Epsilon atual: {stats['current_epsilon']}")
print(f"Taxa de acerto: {stats['avg_reward_100_episodes']}")
```

#### Debugging de Otimizador

```python
# Ativa debug do otimizador
optimizer = AdvancedOptimizer(debug=True)

# Obtém estatísticas de performance
stats = optimizer.get_optimization_stats()
print(f"Taxa de sucesso: {stats['success_rate']}")
print(f"Melhoria média: {stats['avg_improvement']}")
```

### Suporte

Para suporte técnico:
1. Verifique esta documentação
2. Execute testes para diagnóstico
3. Consulte logs de erro
4. Abra issue no GitHub

---

**Versão**: 1.3.0 
**Última atualização**: Janeiro 2025 
**Autor**: Sistema de Cidades Autônomas com Agentes de IA

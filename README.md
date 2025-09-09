# Cidades Autônomas com Agentes de IA

Um sistema avançado de simulação de cidade inteligente onde múltiplos agentes de IA atuam como cidadãos, empresas, órgãos públicos e serviços, interagindo entre si para otimizar recursos, resolver conflitos e se adaptar a mudanças no ambiente.

## Versão 1.4 - Segurança, Tempo Real e Monitoramento

A versão 1.4 estabelece uma base sólida e segura para o sistema:

### Novidades da Versão 1.4

- **Segurança Robusta**: Autenticação JWT, autorização RBAC e criptografia
- **Comunicação em Tempo Real**: WebSockets e Event Sourcing
- **Monitoramento Avançado**: Métricas, alertas e observabilidade
- **API RESTful Completa**: Interface padronizada e documentada
- **Auditoria Completa**: Logging de segurança e detecção de anomalias
- **Base Sólida**: Fundação para funcionalidades avançadas

## Versão 1.1 - Arquitetura Multi-Linguagem

A versão 1.1 introduz uma arquitetura moderna multi-linguagem com componentes especializados para máxima performance e escalabilidade:

- **Frontend**: React/TypeScript com dashboard interativo
- **Backend**: Node.js/Express com API RESTful
- **IA Engine**: Rust para algoritmos de alta performance
- **Microserviços**: Go para serviços especializados
- **Banco de Dados**: PostgreSQL com Redis para cache
- **Containerização**: Docker e Docker Compose
- **Monitoramento**: Prometheus + Grafana

## Objetivo

Simular (ou até aplicar em pequena escala) uma cidade inteligente onde múltiplos agentes de IA atuam como cidadãos, empresas, órgãos públicos e serviços, interagindo entre si para otimizar recursos, resolver conflitos e se adaptar a mudanças no ambiente.

## Arquitetura do Sistema

### Tipos de Agentes

- ** Agentes Cidadãos**: Personalidades únicas com rotinas, necessidades e capacidade de aprendizado
- ** Agentes Empresas**: Fornecem produtos/serviços com precificação dinâmica e logística inteligente
- ** Agentes Governo**: Definem regras, políticas públicas e fiscalização
- ** Agentes Infraestrutura**: Controlam sistemas críticos (energia, trânsito, saneamento)

### Mecânicas de Interação

- ** Mercado Dinâmico**: Demanda e oferta em tempo real
- ** Eventos Aleatórios**: Crises, pandemias, mudanças populacionais
- ** Aprendizado Coletivo**: Compartilhamento de experiências entre agentes
- ** Conflitos e Negociações**: Protestos, lobby, sanções

## Instalação Rápida

### Opção 1: Docker Compose (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/SSilvestreS/CAA.git
cd CAA

# Inicie todos os serviços
docker-compose up -d

# Acesse o dashboard
open http://localhost:3000
```

### Opção 2: Instalação Manual

```bash
# Clone o repositório
git clone https://github.com/SSilvestreS/CAA.git
cd CAA

# Backend Node.js
cd backend
npm install
npm run dev

# Frontend React
cd ../frontend
npm install
npm start

# IA Engine Rust
cd ../ai-engine
cargo build --release
cargo run

# Microserviços Go
cd ../microservices
go mod tidy
go run agent-service/main.go
```

Para instalação detalhada, consulte [INSTALL.md](INSTALL.md).

##  Demonstração Interativa

```bash
# Execute a demonstração completa
python demo.py

# Ou execute exemplos específicos
python example_usage.py
```

## Dashboard Interativo

Acesse o dashboard em tempo real: **http://localhost:8050**

### Funcionalidades do Dashboard:
- Métricas em tempo real da cidade
- Mapa interativo com posicionamento dos agentes
- Gráficos de evolução das métricas
- Monitoramento de eventos ativos
- Análise de mercado por setor
- Performance das empresas
- Log de eventos em tempo real

## Cenários de Teste

### Políticas Públicas
```bash
python run_scenarios.py --policies
```

### Cenários de Crise
```bash
python run_scenarios.py --crises
```

### Inovações Tecnológicas
```bash
python run_scenarios.py --innovations
```

### Cenários Disponíveis:
- **Boom Econômico**: Testa crescimento econômico
- **Crise Energética**: Simula escassez de energia
- **Pandemia**: Modela lockdown e redução de atividade
- **Falha de Infraestrutura**: Testa resiliência do sistema
- **Crescimento Populacional**: Avalia impacto demográfico
- **Regulamentação Ambiental**: Testa políticas verdes
- **Transporte Autônomo**: Simula inovação em mobilidade
- **Smart Grid**: Testa rede elétrica inteligente
- **Desigualdade Social**: Modela impactos sociais

## Sistema de IA e Aprendizado

### Reinforcement Learning
- Agentes aprendem com experiências passadas
- Otimização de decisões baseada em recompensas
- Adaptação contínua ao ambiente

### Aprendizado Coletivo
- Compartilhamento de conhecimento entre agentes
- Estratégias bem-sucedidas são propagadas
- Memória coletiva para decisões futuras

### Modelos de Decisão
- Redes neurais para predição de ações
- Análise de contexto para tomada de decisão
- Otimização baseada em múltiplos objetivos

## Tecnologias Utilizadas

### Frameworks Multi-Agente
- **CrewAI**: Coordenação de agentes especializados
- **AutoGen**: Conversação e colaboração entre agentes
- **Mesa**: Simulação multi-agente em Python

### Inteligência Artificial
- **PyTorch**: Redes neurais e deep learning
- **Stable-Baselines3**: Reinforcement Learning
- **Scikit-learn**: Machine Learning tradicional

### Visualização e Interface
- **Dash + Plotly**: Dashboard interativo
- **Matplotlib/Seaborn**: Visualizações estáticas
- **Bootstrap**: Interface responsiva

### Armazenamento e Dados
- **SQLite**: Banco de dados local
- **ChromaDB**: Banco de dados vetorial
- **Pandas**: Manipulação de dados

## Estrutura do Projeto

```
Cidades Autônomas com Agentes de IA/
 src/
  agents/ # Agentes da simulação
   base_agent.py # Classe base para agentes
   citizen_agent.py # Agentes cidadãos
   business_agent.py # Agentes empresas
   government_agent.py # Agentes governo
   infrastructure_agent.py # Agentes infraestrutura
  environment/ # Ambiente de simulação
   city_environment.py # Coordenador principal
  ai/ # Sistema de IA
   collective_learning.py # Aprendizado coletivo
  scenarios/ # Cenários de teste
   scenario_manager.py # Gerenciador de cenários
  visualization/ # Dashboard e visualização
  dashboard.py # Interface web interativa
 main.py # Arquivo principal
 demo.py # Demonstração interativa
 run_scenarios.py # Executor de cenários
 example_usage.py # Exemplos de uso
 config.py # Configurações
 requirements.txt # Dependências
 README.md # Este arquivo
```

## Casos de Uso

### 1. Pesquisa Acadêmica
- Estudo de sistemas complexos
- Análise de políticas públicas
- Modelagem de comportamento social

### 2. Planejamento Urbano
- Teste de políticas de transporte
- Avaliação de impactos ambientais
- Simulação de crescimento urbano

### 3. Desenvolvimento de IA
- Laboratório para algoritmos multi-agente
- Teste de estratégias de aprendizado
- Validação de sistemas de decisão

### 4. Educação
- Demonstração de conceitos de IA
- Simulação de sistemas sociais
- Aprendizado sobre cidades inteligentes

## Exemplos de Uso

### Simulação Básica
```python
import asyncio
from src.environment.city_environment import CityEnvironment

async def main():
 # Cria cidade
 city = CityEnvironment("Minha Cidade", (100, 100))
 
 # Inicializa com agentes
 await city.initialize_city(
 num_citizens=100,
 num_businesses=20,
 num_infrastructure=10
 )
 
 # Executa simulação
 for i in range(100):
 await city._simulation_cycle()
 
 # Exibe resultados
 print(city.get_city_status())

asyncio.run(main())
```

### Execução de Cenário
```python
from src.scenarios.scenario_manager import ScenarioManager

# Cria gerenciador de cenários
scenario_manager = ScenarioManager(city)

# Executa cenário de crise energética
results = await scenario_manager.run_scenario('energy_crisis', duration=50)

print(f"Impacto na satisfação: {results['citizen_satisfaction_change']:.3f}")
```

## Métricas e Indicadores

### Métricas da Cidade
- **População**: Número total de cidadãos
- **Satisfação Cidadã**: Nível médio de satisfação
- **Saúde Econômica**: Indicador de prosperidade
- **Saúde da Infraestrutura**: Qualidade dos serviços
- **Saúde Ambiental**: Impacto ecológico
- **Taxa de Desemprego**: Indicador econômico
- **Taxa de Criminalidade**: Segurança pública

### Métricas de Aprendizado
- **Experiências Coletadas**: Total de experiências
- **Estratégias Compartilhadas**: Conhecimento propagado
- **Taxa de Sucesso**: Efetividade das decisões
- **Adaptações Bem-sucedidas**: Aprendizado efetivo

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## Agradecimentos

- Comunidade Python
- Desenvolvedores dos frameworks utilizados
- Pesquisadores em sistemas multi-agente
- Contribuidores do projeto

## Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação
- Execute os exemplos em `example_usage.py`
- Teste a demonstração em `demo.py`

---


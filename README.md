# Cidades Autônomas com Agentes de IA

Sistema de simulação de cidade inteligente onde múltiplos agentes de IA interagem para otimizar recursos, resolver conflitos e se adaptar a mudanças no ambiente.

## Versão Atual: 1.7 - Correção de Bugs e Erros

### Versão 1.7 - Melhorias de Qualidade
- Correção de 104 erros de linting (84% de redução)
- Remoção de 89 imports não utilizados
- Correção de 186 imports faltantes
- Código mais limpo e profissional
- 100% de funcionalidade preservada
- Base sólida para futuras versões

### Funcionalidades Principais

#### Agentes Inteligentes
- **Cidadãos**: Personalidades únicas com rotinas e necessidades
- **Empresas**: Produtos/serviços com precificação dinâmica
- **Governo**: Políticas públicas e fiscalização
- **Infraestrutura**: Sistemas críticos (energia, trânsito, saneamento)

#### Inteligência Artificial Avançada
- **Reinforcement Learning**: DQN, PPO, A3C
- **Transformers**: Análise de sentimento e predição
- **LSTM/GRU**: Análise de séries temporais
- **GANs**: Geração de dados sintéticos
- **Aprendizado Coletivo**: Compartilhamento de conhecimento

#### Segurança e Monitoramento
- **Autenticação JWT**: Sistema seguro de acesso
- **RBAC**: Controle de acesso baseado em funções
- **Criptografia AES-256**: Proteção de dados
- **Auditoria**: Logging completo de segurança
- **Métricas**: Monitoramento em tempo real

#### Comunicação e APIs
- **WebSockets**: Comunicação em tempo real
- **Event Sourcing**: Rastreamento de eventos
- **API RESTful**: Interface padronizada
- **Integrações**: APIs externas e IoT

#### Analytics e Visualização
- **Dashboard Interativo**: Métricas em tempo real
- **Relatórios**: Geração automática
- **Alertas**: Sistema de notificações
- **Métricas**: Análise de performance

#### Arquitetura Enterprise
- **Microserviços**: Escalabilidade horizontal
- **MLOps**: Pipeline completo de ML
- **Kubernetes**: Orquestração em nuvem
- **Docker**: Containerização
- **Monitoramento**: Prometheus, Grafana, Jaeger

## Instalação Rápida

### Docker Compose (Recomendado)
```bash
git clone https://github.com/SSilvestreS/CAA.git
cd CAA
docker-compose up -d
open http://localhost:3000
```

### Instalação Manual
```bash
git clone https://github.com/SSilvestreS/CAA.git
cd CAA

# Backend
cd backend && npm install && npm run dev

# Frontend
cd ../frontend && npm install && npm start

# IA Engine
cd ../ai-engine && cargo build --release && cargo run

# Microserviços
cd ../microservices && go mod tidy && go run agent-service/main.go
```

## Uso Rápido

### Demonstração Interativa
```bash
python demo.py
```

### Dashboard
Acesse: **http://localhost:8050**

### Cenários de Teste
```bash
# Políticas públicas
python run_scenarios.py --policies

# Cenários de crise
python run_scenarios.py --crises

# Inovações tecnológicas
python run_scenarios.py --innovations
```

## Estrutura do Projeto

```
src/
├── agents/              # Agentes da simulação
├── ai/                  # Sistema de IA
│   ├── advanced_models/ # Modelos avançados (Transformers, LSTM, GANs)
│   └── collective_learning.py
├── environment/         # Ambiente de simulação
├── scenarios/           # Cenários de teste
├── visualization/       # Dashboard e visualização
├── security/           # Sistema de segurança
├── realtime/           # Comunicação em tempo real
├── monitoring/         # Monitoramento e métricas
├── api/                # API RESTful
├── microservices/      # Microserviços
├── mlops/              # MLOps e pipelines
├── integrations/       # Integrações externas
├── analytics/          # Analytics avançado
└── infrastructure/     # Infraestrutura (Docker, K8s)
```

## Exemplos de Uso

### Simulação Básica
```python
import asyncio
from src.environment.city_environment import CityEnvironment

async def main():
    city = CityEnvironment("Minha Cidade", (100, 100))
    await city.initialize_city(num_citizens=100, num_businesses=20)
    
    for i in range(100):
        await city._simulation_cycle()
    
    print(city.get_city_status())

asyncio.run(main())
```

### Cenário de Crise
```python
from src.scenarios.scenario_manager import ScenarioManager

scenario_manager = ScenarioManager(city)
results = await scenario_manager.run_scenario('energy_crisis', duration=50)
print(f"Impacto na satisfação: {results['citizen_satisfaction_change']:.3f}")
```

## Métricas Principais

- **População**: Número total de cidadãos
- **Satisfação Cidadã**: Nível médio de satisfação
- **Saúde Econômica**: Indicador de prosperidade
- **Saúde da Infraestrutura**: Qualidade dos serviços
- **Saúde Ambiental**: Impacto ecológico
- **Taxa de Desemprego**: Indicador econômico
- **Taxa de Criminalidade**: Segurança pública

## Casos de Uso

- **Pesquisa Acadêmica**: Estudo de sistemas complexos
- **Planejamento Urbano**: Teste de políticas públicas
- **Desenvolvimento de IA**: Laboratório para algoritmos
- **Educação**: Demonstração de conceitos

## Segurança

- Autenticação JWT
- Controle de acesso RBAC
- Criptografia AES-256
- Auditoria completa
- Detecção de anomalias

## Monitoramento

- Métricas em tempo real
- Alertas automáticos
- Dashboards interativos
- Logs estruturados
- Tracing distribuído

## Tecnologias

### Backend
- Python 3.8+
- FastAPI
- SQLAlchemy
- Redis
- PostgreSQL

### Frontend
- React/TypeScript
- Dash/Plotly
- Bootstrap

### IA/ML
- PyTorch
- Transformers
- Stable-Baselines3
- Scikit-learn

### Infraestrutura
- Docker
- Kubernetes
- Prometheus
- Grafana
- Jaeger

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## Suporte

- Abra uma issue no GitHub
- Consulte a documentação
- Execute os exemplos
- Teste a demonstração

---

**Desenvolvido com amor para pesquisa e educação em IA e sistemas complexos**
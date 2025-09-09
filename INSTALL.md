# Guia de Instalação - Cidades Autônomas com Agentes de IA

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- 4GB de RAM mínimo (8GB recomendado)
- 2GB de espaço em disco

## Instalação Rápida

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd "Cidades Autônomas com Agentes de IA"
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Execute a Simulação
```bash
python main.py
```

## Instalação Detalhada

### Opção 1: Instalação com pip
```bash
# Instala o projeto como pacote
pip install -e .

# Executa a simulação
smart-city
```

### Opção 2: Ambiente Virtual (Recomendado)
```bash
# Cria ambiente virtual
python -m venv venv

# Ativa ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instala dependências
pip install -r requirements.txt

# Executa simulação
python main.py
```

### Opção 3: Conda
```bash
# Cria ambiente conda
conda create -n smart-city python=3.9
conda activate smart-city

# Instala dependências
pip install -r requirements.txt

# Executa simulação
python main.py
```

## Executando Cenários

### Executar Cenário Específico
```bash
python run_scenarios.py --scenario energy_crisis --duration 100
```

### Listar Cenários Disponíveis
```bash
python run_scenarios.py --list
```

### Executar Comparação de Políticas
```bash
python run_scenarios.py --policies
```

### Executar Cenários de Crise
```bash
python run_scenarios.py --crises
```

## Dashboard Interativo

### Executar Apenas o Dashboard
```bash
python main.py --dashboard-only
```

### Acessar Dashboard
Abra seu navegador e acesse: http://localhost:8050

## Exemplos de Uso

### Executar Exemplos
```bash
python example_usage.py
```

### Exemplo Básico
```python
import asyncio
from src.environment.city_environment import CityEnvironment

async def main():
 environment = CityEnvironment("Minha Cidade", (50, 50))
 await environment.initialize_city(num_citizens=50, num_businesses=10)
 
 # Executa 100 ciclos
 for i in range(100):
 await environment._simulation_cycle()
 
 print(environment.get_city_status())

asyncio.run(main())
```

## Configurações

### Personalizar Configurações
Edite o arquivo `config.py` para ajustar:
- Número de agentes
- Velocidade da simulação
- Configurações de aprendizado
- Parâmetros do dashboard

### Exemplo de Configuração Personalizada
```python
# config.py
CITY_CONFIG = {
 'default_name': 'Minha Cidade Personalizada',
 'default_size': (200, 200),
 'max_agents': 2000
}

AGENT_CONFIG = {
 'citizens': {
 'default_count': 200,
 'income_range': (2000, 15000)
 }
}
```

##  Solução de Problemas

### Erro de Dependências
```bash
# Atualiza pip
pip install --upgrade pip

# Reinstala dependências
pip install -r requirements.txt --force-reinstall
```

### Erro de Porta Ocupada
```bash
# Usa porta diferente
python main.py --port 8051
```

### Erro de Memória
```bash
# Reduz número de agentes
python main.py --citizens 50 --businesses 10 --infrastructure 5
```

### Erro de PyTorch
```bash
# Instala versão CPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

##  Estrutura do Projeto

```
Cidades Autônomas com Agentes de IA/
 src/
  agents/ # Agentes (Cidadãos, Empresas, etc.)
  environment/ # Ambiente de simulação
  ai/ # Sistema de IA e aprendizado
  scenarios/ # Cenários de teste
  visualization/ # Dashboard e visualização
 main.py # Arquivo principal
 run_scenarios.py # Executor de cenários
 example_usage.py # Exemplos de uso
 config.py # Configurações
 requirements.txt # Dependências
 README.md # Documentação
```

## Verificação da Instalação

### Teste Básico
```bash
python -c "
import sys
sys.path.append('src')
from src.environment.city_environment import CityEnvironment
print(' Instalação bem-sucedida!')
"
```

### Teste Completo
```bash
python example_usage.py
```

##  Suporte

Se encontrar problemas:

1. Verifique se todas as dependências estão instaladas
2. Consulte a documentação no README.md
3. Execute os exemplos em example_usage.py
4. Verifique os logs de erro

## Próximos Passos

Após a instalação:

1. Execute `python main.py` para iniciar a simulação
2. Acesse o dashboard em http://localhost:8050
3. Experimente diferentes cenários com `run_scenarios.py`
4. Personalize as configurações em `config.py`
5. Explore os exemplos em `example_usage.py`

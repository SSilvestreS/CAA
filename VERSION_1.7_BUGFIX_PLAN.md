# Versão 1.7 - Correção de Bugs e Erros

## Objetivo
Versão focada exclusivamente na correção de bugs, erros de linting e melhorias de qualidade de código.

## Bugs e Erros Identificados

### 1. Erros de Linting (124 total)

#### F401 - Imports não utilizados (89 erros)
- **asyncio**: Importado mas não usado em 15 arquivos
- **typing**: Imports desnecessários de Dict, List, Optional, Any
- **datetime**: Imports não utilizados
- **numpy**: Import não utilizado
- **os**: Import não utilizado

#### E402 - Imports não no topo do arquivo (14 erros)
- **main_v1_6.py**: 8 imports após sys.path.append
- **test_v1_6.py**: 6 imports após sys.path.append

#### W503 - Quebra de linha antes de operador binário (16 erros)
- **agents/**: 3 erros em citizen_agent.py, government_agent.py, infrastructure_agent.py
- **ai/**: 5 erros em reinforcement_learning.py, collective_learning.py
- **environment/**: 2 erros em city_environment.py
- **integrations/**: 1 erro em external_apis.py
- **realtime/**: 1 erro em event_sourcing.py
- **visualization/**: 2 erros em advanced_3d_dashboard.py

#### F841 - Variável local não utilizada (1 erro)
- **optimization/advanced_optimizer.py**: variável 'improvement' não usada

#### W292/W293 - Problemas de formatação (4 erros)
- **agent_controller.py**: 3 linhas com whitespace, 1 sem newline no final
- **test_v1_6.py**: 1 import não utilizado

### 2. Problemas de Estrutura

#### Imports Desnecessários
- Muitos arquivos importam módulos que não usam
- Imports de typing excessivos
- Imports de asyncio em arquivos síncronos

#### Formatação Inconsistente
- Quebras de linha antes de operadores binários
- Whitespace em linhas vazias
- Falta de newline no final de arquivos

#### Código Morto
- Variáveis declaradas mas não utilizadas
- Imports de funções não usadas

## Plano de Correção

### Fase 1: Limpeza de Imports (Prioridade Alta)
1. Remover imports não utilizados
2. Consolidar imports de typing
3. Mover imports para o topo dos arquivos

### Fase 2: Correção de Formatação (Prioridade Alta)
1. Corrigir quebras de linha antes de operadores
2. Remover whitespace desnecessário
3. Adicionar newlines no final de arquivos

### Fase 3: Limpeza de Código (Prioridade Média)
1. Remover variáveis não utilizadas
2. Limpar código morto
3. Otimizar imports

### Fase 4: Validação (Prioridade Alta)
1. Executar flake8 para verificar correções
2. Executar testes para garantir funcionalidade
3. Verificar imports e dependências

## Arquivos Prioritários

### Alta Prioridade
- `src/main_v1_6.py` - 8 erros E402
- `test_v1_6.py` - 6 erros E402 + 1 F401
- `src/optimization/advanced_optimizer.py` - 1 F841

### Média Prioridade
- Todos os arquivos com F401 (89 erros)
- Arquivos com W503 (16 erros)

### Baixa Prioridade
- Arquivos com W292/W293 (4 erros)

## Critérios de Sucesso
- 0 erros F401 (imports não utilizados)
- 0 erros E402 (imports não no topo)
- 0 erros F841 (variáveis não utilizadas)
- Máximo 5 erros W503 (formatação)
- 0 erros W292/W293 (whitespace)

## Estimativa
- **Tempo**: 2-3 horas
- **Arquivos**: ~50 arquivos
- **Erros**: 124 total
- **Foco**: Qualidade de código e limpeza

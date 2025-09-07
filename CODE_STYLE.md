# Guia de Estilo de Código - Cidades Autônomas com Agentes de IA

## Padrões de Código

### Python
- **Formatação**: PEP 8 com Black (linha máxima: 88 caracteres)
- **Imports**: Organizados com isort
- **Linting**: Flake8 para verificação de qualidade
- **Documentação**: Docstrings em português para todas as funções e classes

### TypeScript/JavaScript
- **Formatação**: Prettier com configurações padrão
- **Linting**: ESLint com regras TypeScript
- **Imports**: Organizados alfabeticamente

### Rust
- **Formatação**: rustfmt padrão
- **Linting**: clippy para verificação de qualidade
- **Documentação**: Comentários em português

### Go
- **Formatação**: gofmt padrão
- **Linting**: golint e go vet
- **Documentação**: Comentários em português

## Configurações de Ferramentas

### Black (Python)
```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
```

### isort (Python)
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

### Flake8 (Python)
```toml
[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
```

## Comandos de Limpeza

### Python
```bash
# Formatar código
black .

# Organizar imports
isort .

# Verificar qualidade
flake8 .

# Executar todos
black . && isort . && flake8 .
```

### TypeScript
```bash
# Formatar código
prettier --write .

# Verificar qualidade
eslint . --ext .ts,.tsx
```

### Rust
```bash
# Formatar código
cargo fmt

# Verificar qualidade
cargo clippy
```

### Go
```bash
# Formatar código
gofmt -w .

# Verificar qualidade
golint ./...
go vet ./...
```

## Convenções de Nomenclatura

### Python
- **Classes**: PascalCase (ex: `CitizenAgent`)
- **Funções/Variáveis**: snake_case (ex: `make_decision`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_AGENTS`)

### TypeScript
- **Classes**: PascalCase (ex: `CityDashboard`)
- **Funções/Variáveis**: camelCase (ex: `updateState`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_AGENTS`)

### Rust
- **Structs/Enums**: PascalCase (ex: `AgentState`)
- **Funções/Variáveis**: snake_case (ex: `make_decision`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_AGENTS`)

### Go
- **Structs/Interfaces**: PascalCase (ex: `AgentState`)
- **Funções/Variáveis**: camelCase (ex: `makeDecision`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_AGENTS`)

## Documentação

### Python
```python
def exemplo_funcao(parametro: str) -> bool:
 """
 Descrição da função em português.
 
 Args:
 parametro: Descrição do parâmetro
 
 Returns:
 Descrição do retorno
 
 Raises:
 ValueError: Quando o parâmetro é inválido
 """
 pass
```

### TypeScript
```typescript
/**
 * Descrição da função em português
 * @param parametro - Descrição do parâmetro
 * @returns Descrição do retorno
 */
function exemploFuncao(parametro: string): boolean {
 return true;
}
```

## Estrutura de Arquivos

```
projeto/
├── src/ # Código fonte Python
├── frontend/ # Frontend React/TypeScript
├── backend/ # Backend Node.js/TypeScript
├── ai-engine/ # Engine AI em Rust
├── microservices/ # Microserviços em Go
├── database/ # Scripts de banco de dados
├── docs/ # Documentação
├── tests/ # Testes
├── .github/ # Configurações GitHub
└── docker/ # Configurações Docker
```

## Checklist de Código Limpo

- [ ] Código formatado com ferramentas apropriadas
- [ ] Imports organizados e desnecessários removidos
- [ ] Nomes descritivos e consistentes
- [ ] Documentação em português
- [ ] Sem erros de linter
- [ ] Testes passando
- [ ] Comentários explicativos onde necessário
- [ ] Estrutura de arquivos organizada

# Frontend - Cidades Autônomas com Agentes de IA

Interface moderna e futurística para o sistema de simulação de cidades inteligentes com agentes de IA.

## Características

### Design Moderno
- **Tema Cyberpunk**: Cores neon, efeitos de brilho
- **Glassmorphism**: Elementos translúcidos com blur
- **Animações Fluidas**: Framer Motion para transições
- **Responsivo**: Adaptável para desktop, tablet e mobile

### Tecnologias

#### Frontend
- **React 18** + **TypeScript**
- **Vite** para desenvolvimento rápido
- **Tailwind CSS** para estilização
- **Framer Motion** para animações
- **Lucide React** para ícones modernos

#### Ferramentas
- **ESLint** + **Prettier** para qualidade de código
- **PostCSS** + **Autoprefixer** para compatibilidade CSS
- **TypeScript** para tipagem estática

## Instalação

### Pré-requisitos
- Node.js 18+
- npm ou yarn

### Comandos

```bash
# Instalar dependências
npm install

# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Preview da build
npm run preview

# Lint
npm run lint
npm run lint:fix

# Type checking
npm run type-check
```

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/     # Componentes reutilizáveis
│   ├── hooks/         # Hooks personalizados
│   ├── types/         # Tipos TypeScript
│   ├── utils/         # Utilitários
│   ├── App.tsx        # Componente principal
│   ├── App.css        # Estilos principais
│   └── main.tsx       # Ponto de entrada
├── public/            # Arquivos estáticos
├── vite.config.ts     # Configuração do Vite
├── tailwind.config.js # Configuração do Tailwind
├── tsconfig.json      # Configuração do TypeScript
└── package.json       # Dependências e scripts
```

## Funcionalidades

### Dashboard Principal
- **Mapa 3D Interativo** da cidade
- **Agentes em Tempo Real** com animações
- **Métricas Dinâmicas** com gráficos
- **Controles de Simulação**

### Componentes Principais

#### AgentCard
- Visualização individual de agentes
- Métricas de performance
- Status em tempo real
- Animações de estado

#### CityMap
- Mapa interativo da cidade
- Posicionamento de agentes
- Linhas de conexão
- Efeitos visuais

#### MetricsPanel
- Contadores animados
- Gráficos de tendência
- Alertas e notificações
- Progress rings

### Temas Disponíveis
1. **Cyberpunk**: Cores neon, efeitos de brilho
2. **Dark Mode**: Tema escuro com acentos
3. **Light Mode**: Tema claro para uso diurno
4. **Minimalist**: Limpo e funcional

## Personalização

### Cores
Edite `tailwind.config.js` para personalizar as cores:

```javascript
colors: {
  primary: { /* cores primárias */ },
  secondary: { /* cores secundárias */ },
  accent: { /* cores de destaque */ },
}
```

### Animações
Adicione novas animações em `tailwind.config.js`:

```javascript
animation: {
  'custom-float': 'float 3s ease-in-out infinite',
}
```

### Componentes
Crie novos componentes em `src/components/` seguindo o padrão:

```typescript
interface ComponentProps {
  // props do componente
}

export const Component: React.FC<ComponentProps> = ({ props }) => {
  // lógica do componente
  return <div>...</div>;
};
```

## Performance

### Otimizações Implementadas
- **Code Splitting** automático
- **Lazy Loading** de componentes
- **Memoização** de cálculos pesados
- **Throttling/Debouncing** de eventos
- **Virtual Scrolling** para listas grandes

### Monitoramento
- **Performance API** para métricas
- **Memory Usage** tracking
- **FPS Counter** em desenvolvimento
- **Bundle Size** analysis

## Desenvolvimento

### Convenções de Código
- **TypeScript** obrigatório
- **Functional Components** com hooks
- **CSS-in-JS** com Tailwind
- **Naming**: camelCase para variáveis, PascalCase para componentes

### Estrutura de Commits
```
feat: adicionar nova funcionalidade
fix: corrigir bug
style: alterações de estilo
refactor: refatoração de código
test: adicionar testes
docs: atualizar documentação
```

### Debugging
- **React DevTools** para componentes
- **Vite DevTools** para build
- **TypeScript** para erros de tipo
- **ESLint** para qualidade de código

## Deploy

### Build de Produção
```bash
npm run build
```

### Configuração do Servidor
- **Nginx** ou **Apache** para servir arquivos estáticos
- **Gzip** compression habilitada
- **Cache headers** configurados
- **HTTPS** obrigatório

### Variáveis de Ambiente
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8001
VITE_ENVIRONMENT=production
```

## Contribuição

1. Fork do projeto
2. Criar branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -m 'feat: adicionar nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abrir Pull Request

## Licença

MIT License - veja o arquivo LICENSE para detalhes.
-- Schema do banco de dados para Simulação de Cidade Inteligente
-- Versão 1.1 - PostgreSQL com suporte a múltiplas linguagens

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Tabela de simulações
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) NOT NULL DEFAULT 'created',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    metrics JSONB DEFAULT '{}',
    created_by VARCHAR(255),
    version VARCHAR(50) DEFAULT '1.1.0'
);

-- Tabela de agentes
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    name VARCHAR(255),
    state JSONB NOT NULL DEFAULT '{}',
    position POINT,
    energy DECIMAL(10,2) DEFAULT 100.0,
    resources JSONB DEFAULT '{}',
    goals JSONB DEFAULT '[]',
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Tabela de eventos
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    description TEXT,
    data JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    severity VARCHAR(20) DEFAULT 'info',
    source VARCHAR(100) DEFAULT 'system'
);

-- Tabela de interações
CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    agent_from UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    agent_to UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    interaction_type VARCHAR(100) NOT NULL,
    data JSONB DEFAULT '{}',
    result VARCHAR(50),
    duration_ms INTEGER,
    success BOOLEAN DEFAULT true,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de métricas
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    value DECIMAL(15,6) NOT NULL,
    unit VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100) DEFAULT 'system'
);

-- Tabela de cenários
CREATE TABLE IF NOT EXISTS scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    scenario_type VARCHAR(100) NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    expected_outcomes JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    version VARCHAR(50) DEFAULT '1.1.0'
);

-- Tabela de execuções de cenários
CREATE TABLE IF NOT EXISTS scenario_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario_id UUID NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    results JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}'
);

-- Tabela de aprendizado coletivo
CREATE TABLE IF NOT EXISTS collective_learning (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    experience_type VARCHAR(100) NOT NULL,
    state JSONB NOT NULL,
    action JSONB NOT NULL,
    reward DECIMAL(10,6) NOT NULL,
    next_state JSONB,
    done BOOLEAN DEFAULT false,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Tabela de otimizações
CREATE TABLE IF NOT EXISTS optimizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    optimization_type VARCHAR(100) NOT NULL,
    parameters JSONB NOT NULL,
    results JSONB NOT NULL,
    performance_improvement DECIMAL(10,6),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    algorithm VARCHAR(100) DEFAULT 'genetic'
);

-- Tabela de logs do sistema
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    simulation_id UUID REFERENCES simulations(id) ON DELETE SET NULL
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_simulations_status ON simulations(status);
CREATE INDEX IF NOT EXISTS idx_simulations_created_at ON simulations(created_at);
CREATE INDEX IF NOT EXISTS idx_agents_simulation_id ON agents(simulation_id);
CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_position ON agents USING GIST(position);
CREATE INDEX IF NOT EXISTS idx_events_simulation_id ON events(simulation_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_interactions_simulation_id ON interactions(simulation_id);
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_simulation_id ON metrics(simulation_id);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_collective_learning_simulation_id ON collective_learning(simulation_id);
CREATE INDEX IF NOT EXISTS idx_collective_learning_timestamp ON collective_learning(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);

-- Índices GIN para busca em JSONB
CREATE INDEX IF NOT EXISTS idx_simulations_config_gin ON simulations USING GIN(config);
CREATE INDEX IF NOT EXISTS idx_agents_state_gin ON agents USING GIN(state);
CREATE INDEX IF NOT EXISTS idx_agents_resources_gin ON agents USING GIN(resources);
CREATE INDEX IF NOT EXISTS idx_events_data_gin ON events USING GIN(data);
CREATE INDEX IF NOT EXISTS idx_interactions_data_gin ON interactions USING GIN(data);
CREATE INDEX IF NOT EXISTS idx_metrics_metadata_gin ON metrics USING GIN(metadata);

-- Triggers para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_updated_at 
    BEFORE UPDATE ON agents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Função para limpeza automática de dados antigos
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Remover logs antigos (mais de 30 dias)
    DELETE FROM system_logs 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    -- Remover métricas antigas (mais de 90 dias)
    DELETE FROM metrics 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    -- Remover eventos antigos (mais de 60 dias)
    DELETE FROM events 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '60 days';
    
    -- Remover interações antigas (mais de 60 dias)
    DELETE FROM interactions 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '60 days';
END;
$$ LANGUAGE plpgsql;

-- View para estatísticas de simulação
CREATE OR REPLACE VIEW simulation_stats AS
SELECT 
    s.id,
    s.name,
    s.status,
    s.created_at,
    s.started_at,
    s.ended_at,
    COUNT(DISTINCT a.id) as total_agents,
    COUNT(DISTINCT CASE WHEN a.agent_type = 'citizen' THEN a.id END) as citizens,
    COUNT(DISTINCT CASE WHEN a.agent_type = 'business' THEN a.id END) as businesses,
    COUNT(DISTINCT CASE WHEN a.agent_type = 'government' THEN a.id END) as government,
    COUNT(DISTINCT CASE WHEN a.agent_type = 'infrastructure' THEN a.id END) as infrastructure,
    COUNT(DISTINCT e.id) as total_events,
    COUNT(DISTINCT i.id) as total_interactions,
    AVG(m.value) as avg_metric_value
FROM simulations s
LEFT JOIN agents a ON s.id = a.simulation_id
LEFT JOIN events e ON s.id = e.simulation_id
LEFT JOIN interactions i ON s.id = i.simulation_id
LEFT JOIN metrics m ON s.id = m.simulation_id
GROUP BY s.id, s.name, s.status, s.created_at, s.started_at, s.ended_at;

-- View para performance de agentes
CREATE OR REPLACE VIEW agent_performance AS
SELECT 
    a.id,
    a.simulation_id,
    a.agent_type,
    a.name,
    a.energy,
    (a.performance_metrics->>'total_reward')::decimal as total_reward,
    (a.performance_metrics->>'average_reward')::decimal as average_reward,
    (a.performance_metrics->>'success_rate')::decimal as success_rate,
    (a.performance_metrics->>'efficiency')::decimal as efficiency,
    (a.performance_metrics->>'collaboration_score')::decimal as collaboration_score,
    COUNT(DISTINCT i.id) as total_interactions,
    COUNT(DISTINCT CASE WHEN i.success = true THEN i.id END) as successful_interactions
FROM agents a
LEFT JOIN interactions i ON a.id = i.agent_from OR a.id = i.agent_to
GROUP BY a.id, a.simulation_id, a.agent_type, a.name, a.energy, a.performance_metrics;

-- Inserir dados iniciais
INSERT INTO scenarios (name, description, scenario_type, config) VALUES
('Crise Energética', 'Simula uma crise de energia na cidade', 'crisis', '{"energy_shortage": 0.5, "duration": 3600}'),
('Boom Econômico', 'Simula um período de crescimento econômico', 'economic', '{"growth_rate": 0.2, "duration": 7200}'),
('Pandemia', 'Simula uma pandemia na cidade', 'health', '{"infection_rate": 0.1, "duration": 10800}'),
('Trânsito Autônomo', 'Testa sistema de trânsito autônomo', 'transport', '{"autonomous_vehicles": 0.8, "duration": 5400}'),
('Cidade Sustentável', 'Simula políticas de sustentabilidade', 'sustainability', '{"renewable_energy": 0.9, "duration": 9000}');

-- Comentários nas tabelas
COMMENT ON TABLE simulations IS 'Armazena informações sobre simulações de cidade inteligente';
COMMENT ON TABLE agents IS 'Representa agentes individuais na simulação';
COMMENT ON TABLE events IS 'Registra eventos que ocorrem durante a simulação';
COMMENT ON TABLE interactions IS 'Registra interações entre agentes';
COMMENT ON TABLE metrics IS 'Armazena métricas de performance da simulação';
COMMENT ON TABLE scenarios IS 'Define cenários de teste para simulações';
COMMENT ON TABLE collective_learning IS 'Armazena experiências para aprendizado coletivo';
COMMENT ON TABLE optimizations IS 'Registra otimizações aplicadas ao sistema';
COMMENT ON TABLE system_logs IS 'Logs do sistema para debugging e monitoramento';

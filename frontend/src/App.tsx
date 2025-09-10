import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Cpu, 
  Users, 
  Building2, 
  Shield, 
  Activity, 
  Zap, 
  Globe, 
  Settings,
  Play,
  Pause,
  RotateCcw,
  BarChart3,
  MapPin,
  Brain,
  Network
} from 'lucide-react';
import './App.css';

// Tipos TypeScript
interface Agent {
  id: string;
  type: 'citizen' | 'business' | 'government' | 'infrastructure';
  name: string;
  status: 'active' | 'inactive' | 'warning';
  position: { x: number; y: number };
  energy: number;
  metrics: {
    satisfaction: number;
    productivity: number;
    efficiency: number;
  };
}

interface CityMetrics {
  totalAgents: number;
  activeAgents: number;
  averageSatisfaction: number;
  cityHealth: number;
  energyConsumption: number;
  economicGrowth: number;
}

// Componente principal
const App: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [cityMetrics, setCityMetrics] = useState<CityMetrics>({
    totalAgents: 1247,
    activeAgents: 1189,
    averageSatisfaction: 87.3,
    cityHealth: 92.1,
    energyConsumption: 78.5,
    economicGrowth: 15.7
  });

  // Simulação de dados em tempo real
  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        setCityMetrics(prev => ({
          ...prev,
          activeAgents: prev.activeAgents + Math.floor(Math.random() * 10 - 5),
          averageSatisfaction: Math.max(0, Math.min(100, prev.averageSatisfaction + (Math.random() - 0.5) * 2)),
          cityHealth: Math.max(0, Math.min(100, prev.cityHealth + (Math.random() - 0.5) * 1)),
          energyConsumption: Math.max(0, Math.min(100, prev.energyConsumption + (Math.random() - 0.5) * 3)),
          economicGrowth: Math.max(0, prev.economicGrowth + (Math.random() - 0.5) * 0.5)
        }));
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [isRunning]);

  // Agentes de exemplo
  const agents: Agent[] = [
    {
      id: '1',
      type: 'citizen',
      name: 'Maria Silva',
      status: 'active',
      position: { x: 120, y: 80 },
      energy: 85,
      metrics: { satisfaction: 92, productivity: 78, efficiency: 88 }
    },
    {
      id: '2',
      type: 'business',
      name: 'TechCorp Solutions',
      status: 'active',
      position: { x: 300, y: 150 },
      energy: 92,
      metrics: { satisfaction: 89, productivity: 95, efficiency: 91 }
    },
    {
      id: '3',
      type: 'government',
      name: 'Prefeitura Central',
      status: 'active',
      position: { x: 200, y: 200 },
      energy: 78,
      metrics: { satisfaction: 85, productivity: 82, efficiency: 79 }
    },
    {
      id: '4',
      type: 'infrastructure',
      name: 'Sistema de Energia',
      status: 'warning',
      position: { x: 250, y: 120 },
      energy: 65,
      metrics: { satisfaction: 75, productivity: 88, efficiency: 72 }
    }
  ];

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'citizen': return <Users className="w-5 h-5" />;
      case 'business': return <Building2 className="w-5 h-5" />;
      case 'government': return <Shield className="w-5 h-5" />;
      case 'infrastructure': return <Zap className="w-5 h-5" />;
      default: return <Users className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'inactive': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden">
      {/* Partículas de fundo */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-blue-400 rounded-full opacity-30"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -100, 0],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 3 + 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <motion.header 
        className="relative z-10 p-6 border-b border-white/10 backdrop-blur-md bg-white/5"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <motion.div 
              className="flex items-center space-x-3"
              whileHover={{ scale: 1.05 }}
            >
              <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
                <Brain className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Cidades Autônomas IA
                </h1>
                <p className="text-sm text-gray-400">Sistema de Simulação Inteligente</p>
              </div>
            </motion.div>
          </div>

          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
              <span className="text-sm font-medium">
                {isRunning ? 'Online' : 'Offline'}
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <motion.button
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <Settings className="w-5 h-5" />
              </motion.button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="relative z-10 p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Métricas */}
          <motion.div 
            className="lg:col-span-1 space-y-6"
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            {/* Controles */}
            <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                Controles
              </h3>
              <div className="space-y-3">
                <motion.button
                  className={`w-full py-3 px-4 rounded-lg font-medium transition-all ${
                    isRunning 
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                      : 'bg-green-500/20 text-green-400 border border-green-500/30'
                  }`}
                  onClick={() => setIsRunning(!isRunning)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isRunning ? (
                    <>
                      <Pause className="w-4 h-4 inline mr-2" />
                      Pausar Simulação
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 inline mr-2" />
                      Iniciar Simulação
                    </>
                  )}
                </motion.button>
                
                <motion.button
                  className="w-full py-3 px-4 rounded-lg font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 transition-all"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <RotateCcw className="w-4 h-4 inline mr-2" />
                  Resetar
                </motion.button>
              </div>
            </div>

            {/* Métricas da Cidade */}
            <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Métricas da Cidade
              </h3>
              <div className="space-y-4">
                <MetricCard
                  label="Total de Agentes"
                  value={cityMetrics.totalAgents}
                  icon={<Users className="w-4 h-4" />}
                  color="blue"
                />
                <MetricCard
                  label="Agentes Ativos"
                  value={cityMetrics.activeAgents}
                  icon={<Activity className="w-4 h-4" />}
                  color="green"
                />
                <MetricCard
                  label="Satisfação Média"
                  value={`${cityMetrics.averageSatisfaction.toFixed(1)}%`}
                  icon={<Globe className="w-4 h-4" />}
                  color="purple"
                />
                <MetricCard
                  label="Saúde da Cidade"
                  value={`${cityMetrics.cityHealth.toFixed(1)}%`}
                  icon={<Shield className="w-4 h-4" />}
                  color="emerald"
                />
              </div>
            </div>
          </motion.div>

          {/* Área Principal - Mapa e Agentes */}
          <motion.div 
            className="lg:col-span-3"
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {/* Mapa da Cidade */}
            <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10 mb-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <MapPin className="w-5 h-5 mr-2" />
                Mapa da Cidade
              </h3>
              <div className="relative h-96 bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl overflow-hidden">
                {/* Grid de fundo */}
                <div className="absolute inset-0 opacity-20">
                  {[...Array(20)].map((_, i) => (
                    <div key={i} className="absolute border border-white/10" style={{
                      left: `${i * 5}%`,
                      top: 0,
                      width: '1px',
                      height: '100%'
                    }} />
                  ))}
                  {[...Array(15)].map((_, i) => (
                    <div key={i} className="absolute border border-white/10" style={{
                      top: `${i * 6.67}%`,
                      left: 0,
                      height: '1px',
                      width: '100%'
                    }} />
                  ))}
                </div>

                {/* Agentes no mapa */}
                {agents.map((agent) => (
                  <motion.div
                    key={agent.id}
                    className={`absolute w-8 h-8 rounded-full flex items-center justify-center cursor-pointer ${
                      agent.status === 'active' ? 'bg-green-500/80' :
                      agent.status === 'warning' ? 'bg-yellow-500/80' :
                      'bg-red-500/80'
                    }`}
                    style={{
                      left: `${agent.position.x}px`,
                      top: `${agent.position.y}px`,
                    }}
                    onClick={() => setSelectedAgent(agent)}
                    whileHover={{ scale: 1.2 }}
                    animate={{
                      y: [0, -5, 0],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      delay: Math.random() * 2,
                    }}
                  >
                    {getAgentIcon(agent.type)}
                  </motion.div>
                ))}

                {/* Linhas de conexão */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  {agents.map((agent, i) => 
                    agents.slice(i + 1).map((otherAgent, j) => (
                      <motion.line
                        key={`${agent.id}-${otherAgent.id}`}
                        x1={agent.position.x + 16}
                        y1={agent.position.y + 16}
                        x2={otherAgent.position.x + 16}
                        y2={otherAgent.position.y + 16}
                        stroke="rgba(59, 130, 246, 0.3)"
                        strokeWidth="1"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: 1 }}
                        transition={{ duration: 2, delay: Math.random() * 2 }}
                      />
                    ))
                  )}
                </svg>
              </div>
            </div>

            {/* Lista de Agentes */}
            <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Network className="w-5 h-5 mr-2" />
                Agentes Ativos
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {agents.map((agent) => (
                  <motion.div
                    key={agent.id}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      selectedAgent?.id === agent.id
                        ? 'bg-blue-500/20 border-blue-500/50'
                        : 'bg-white/5 border-white/10 hover:bg-white/10'
                    }`}
                    onClick={() => setSelectedAgent(agent)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${
                          agent.type === 'citizen' ? 'bg-blue-500/20' :
                          agent.type === 'business' ? 'bg-green-500/20' :
                          agent.type === 'government' ? 'bg-purple-500/20' :
                          'bg-yellow-500/20'
                        }`}>
                          {getAgentIcon(agent.type)}
                        </div>
                        <div>
                          <h4 className="font-medium">{agent.name}</h4>
                          <p className="text-sm text-gray-400 capitalize">{agent.type}</p>
                        </div>
                      </div>
                      <div className={`text-sm font-medium ${getStatusColor(agent.status)}`}>
                        {agent.status}
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Energia:</span>
                        <span>{agent.energy}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <motion.div
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${agent.energy}%` }}
                          transition={{ duration: 1, delay: 0.5 }}
                        />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Modal de Detalhes do Agente */}
      <AnimatePresence>
        {selectedAgent && (
          <motion.div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedAgent(null)}
          >
            <motion.div
              className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 max-w-md w-full"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Detalhes do Agente</h3>
                <button
                  className="text-gray-400 hover:text-white"
                  onClick={() => setSelectedAgent(null)}
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-3 rounded-lg ${
                    selectedAgent.type === 'citizen' ? 'bg-blue-500/20' :
                    selectedAgent.type === 'business' ? 'bg-green-500/20' :
                    selectedAgent.type === 'government' ? 'bg-purple-500/20' :
                    'bg-yellow-500/20'
                  }`}>
                    {getAgentIcon(selectedAgent.type)}
                  </div>
                  <div>
                    <h4 className="font-medium text-lg">{selectedAgent.name}</h4>
                    <p className="text-gray-400 capitalize">{selectedAgent.type}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className={getStatusColor(selectedAgent.status)}>
                      {selectedAgent.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Energia:</span>
                    <span>{selectedAgent.energy}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Satisfação:</span>
                    <span>{selectedAgent.metrics.satisfaction}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Produtividade:</span>
                    <span>{selectedAgent.metrics.productivity}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Eficiência:</span>
                    <span>{selectedAgent.metrics.efficiency}%</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Componente de Métrica
const MetricCard: React.FC<{
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
}> = ({ label, value, icon, color }) => {
  const colorClasses = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    purple: 'text-purple-400',
    emerald: 'text-emerald-400',
  };

  return (
    <motion.div
      className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg bg-${color}-500/20`}>
          {icon}
        </div>
        <span className="text-sm font-medium">{label}</span>
      </div>
      <motion.span
        className={`text-lg font-bold ${colorClasses[color as keyof typeof colorClasses]}`}
        key={value}
        initial={{ scale: 1.2 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        {value}
      </motion.span>
    </motion.div>
  );
};

export default App;
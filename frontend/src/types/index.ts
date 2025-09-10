// Tipos principais do sistema
export interface Agent {
  id: string;
  type: AgentType;
  name: string;
  status: AgentStatus;
  position: Position;
  energy: number;
  metrics: AgentMetrics;
  createdAt: Date;
  updatedAt: Date;
}

export type AgentType = 'citizen' | 'business' | 'government' | 'infrastructure';

export type AgentStatus = 'active' | 'inactive' | 'warning' | 'error';

export interface Position {
  x: number;
  y: number;
  z?: number;
}

export interface AgentMetrics {
  satisfaction: number;
  productivity: number;
  efficiency: number;
  health: number;
  happiness: number;
  stress: number;
}

// Métricas da cidade
export interface CityMetrics {
  totalAgents: number;
  activeAgents: number;
  averageSatisfaction: number;
  cityHealth: number;
  energyConsumption: number;
  economicGrowth: number;
  populationGrowth: number;
  crimeRate: number;
  pollutionLevel: number;
  trafficFlow: number;
  publicTransportEfficiency: number;
  educationLevel: number;
  healthcareAccess: number;
  housingAvailability: number;
  employmentRate: number;
}

// Configurações do sistema
export interface SystemConfig {
  simulationSpeed: number;
  maxAgents: number;
  citySize: {
    width: number;
    height: number;
  };
  timeScale: number;
  enableRealTime: boolean;
  enableAI: boolean;
  enableOptimization: boolean;
}

// Eventos do sistema
export interface SystemEvent {
  id: string;
  type: EventType;
  message: string;
  severity: EventSeverity;
  timestamp: Date;
  agentId?: string;
  data?: Record<string, any>;
}

export type EventType = 
  | 'agent_created'
  | 'agent_updated'
  | 'agent_deleted'
  | 'simulation_started'
  | 'simulation_paused'
  | 'simulation_stopped'
  | 'error_occurred'
  | 'warning_issued'
  | 'optimization_completed'
  | 'city_metric_updated';

export type EventSeverity = 'info' | 'warning' | 'error' | 'critical';

// Configurações de visualização
export interface ViewConfig {
  theme: Theme;
  showGrid: boolean;
  showConnections: boolean;
  showMetrics: boolean;
  showParticles: boolean;
  showAnimations: boolean;
  cameraPosition: Position;
  zoomLevel: number;
  selectedAgentId?: string;
}

export type Theme = 'dark' | 'light' | 'cyberpunk' | 'minimalist';

// Dados de simulação
export interface SimulationData {
  timestamp: Date;
  agents: Agent[];
  metrics: CityMetrics;
  events: SystemEvent[];
  config: SystemConfig;
}

// Configurações de API
export interface APIConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  enableCaching: boolean;
  cacheTimeout: number;
}

// Estados do sistema
export interface SystemState {
  isRunning: boolean;
  isPaused: boolean;
  isInitialized: boolean;
  currentTime: Date;
  simulationSpeed: number;
  error?: string;
}

// Configurações de notificação
export interface NotificationConfig {
  enabled: boolean;
  types: NotificationType[];
  soundEnabled: boolean;
  desktopEnabled: boolean;
}

export type NotificationType = 
  | 'agent_status_change'
  | 'metric_threshold_exceeded'
  | 'system_error'
  | 'optimization_complete'
  | 'simulation_event';

// Dados de performance
export interface PerformanceMetrics {
  fps: number;
  memoryUsage: number;
  cpuUsage: number;
  renderTime: number;
  updateTime: number;
  networkLatency: number;
}

// Configurações de exportação
export interface ExportConfig {
  format: ExportFormat;
  includeAgents: boolean;
  includeMetrics: boolean;
  includeEvents: boolean;
  timeRange: {
    start: Date;
    end: Date;
  };
}

export type ExportFormat = 'json' | 'csv' | 'pdf' | 'png' | 'mp4';

// Configurações de backup
export interface BackupConfig {
  enabled: boolean;
  interval: number; // em minutos
  maxBackups: number;
  includeAssets: boolean;
  compression: boolean;
}

// Dados de usuário
export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  preferences: UserPreferences;
  lastLogin: Date;
  createdAt: Date;
}

export type UserRole = 'admin' | 'user' | 'viewer';

export interface UserPreferences {
  theme: Theme;
  language: string;
  notifications: NotificationConfig;
  viewConfig: ViewConfig;
  shortcuts: Record<string, string>;
}

// Configurações de segurança
export interface SecurityConfig {
  enableAuth: boolean;
  sessionTimeout: number;
  maxLoginAttempts: number;
  enableAuditLog: boolean;
  allowedOrigins: string[];
}

// Dados de auditoria
export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resource: string;
  timestamp: Date;
  ipAddress: string;
  userAgent: string;
  details: Record<string, any>;
}

// Configurações de desenvolvimento
export interface DevConfig {
  enableDebugMode: boolean;
  enablePerformanceMonitoring: boolean;
  enableErrorReporting: boolean;
  logLevel: LogLevel;
  enableHotReload: boolean;
}

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

// Tipos de utilitários
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type Required<T, K extends keyof T> = T & { [P in K]-?: T[P] };
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Tipos de callback
export type EventCallback<T = any> = (data: T) => void;
export type ErrorCallback = (error: Error) => void;
export type SuccessCallback<T = any> = (data: T) => void;

// Tipos de promise
export type AsyncResult<T, E = Error> = Promise<{ data: T; error?: never } | { data?: never; error: E }>;

// Tipos de estado
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'reconnecting';

// Tipos de validação
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// Tipos de filtro
export interface FilterConfig {
  agentTypes?: AgentType[];
  statuses?: AgentStatus[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  searchQuery?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Tipos de paginação
export interface PaginationConfig {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationConfig;
}

// Tipos de estatísticas
export interface Statistics {
  total: number;
  average: number;
  median: number;
  min: number;
  max: number;
  standardDeviation: number;
  percentiles: {
    p25: number;
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
  };
}

// Tipos de gráfico
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  fill?: boolean;
}

// Tipos de mapa
export interface MapConfig {
  center: Position;
  zoom: number;
  minZoom: number;
  maxZoom: number;
  enableClustering: boolean;
  showHeatmap: boolean;
  showTraffic: boolean;
}

// Tipos de tempo real
export interface RealtimeConfig {
  enabled: boolean;
  updateInterval: number;
  enableWebSocket: boolean;
  enableServerSentEvents: boolean;
  fallbackToPolling: boolean;
}

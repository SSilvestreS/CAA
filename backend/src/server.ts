import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import dotenv from 'dotenv';

import { logger } from './utils/logger';
import { errorHandler } from './middleware/errorHandler';
import { rateLimiter } from './middleware/rateLimiter';
import { simulationRoutes } from './routes/simulation';
import { agentRoutes } from './routes/agents';
import { analyticsRoutes } from './routes/analytics';
import { scenarioRoutes } from './routes/scenarios';
import { SimulationManager } from './services/SimulationManager';
import { DatabaseService } from './services/DatabaseService';
import { RedisService } from './services/RedisService';

// Carregar variáveis de ambiente
dotenv.config();

const app = express();
const server = createServer(app);
const io = new SocketIOServer(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 5000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(morgan('combined', { stream: { write: (message) => logger.info(message.trim()) } }));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(rateLimiter);

// Inicializar serviços
const databaseService = new DatabaseService();
const redisService = new RedisService();
const simulationManager = new SimulationManager(io, databaseService, redisService);

// Rotas da API
app.use('/api/simulation', simulationRoutes(simulationManager));
app.use('/api/agents', agentRoutes(simulationManager));
app.use('/api/analytics', analyticsRoutes(simulationManager));
app.use('/api/scenarios', scenarioRoutes(simulationManager));

// Rota de health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: '1.1.0',
    services: {
      database: databaseService.isConnected(),
      redis: redisService.isConnected(),
      simulation: simulationManager.isRunning()
    }
  });
});

// Middleware de tratamento de erros
app.use(errorHandler);

// WebSocket para comunicação em tempo real
io.on('connection', (socket) => {
  logger.info(`Cliente conectado: ${socket.id}`);

  socket.on('join_simulation', (simulationId: string) => {
    socket.join(`simulation_${simulationId}`);
    logger.info(`Cliente ${socket.id} entrou na simulação ${simulationId}`);
  });

  socket.on('leave_simulation', (simulationId: string) => {
    socket.leave(`simulation_${simulationId}`);
    logger.info(`Cliente ${socket.id} saiu da simulação ${simulationId}`);
  });

  socket.on('disconnect', () => {
    logger.info(`Cliente desconectado: ${socket.id}`);
  });
});

// Inicializar servidor
async function startServer() {
  try {
    // Conectar aos serviços
    await databaseService.connect();
    await redisService.connect();
    
    server.listen(PORT, () => {
      logger.info(`🚀 Servidor rodando na porta ${PORT}`);
      logger.info(`📊 Dashboard disponível em: http://localhost:${PORT}`);
      logger.info(`🔌 WebSocket ativo para comunicação em tempo real`);
    });
  } catch (error) {
    logger.error('Erro ao inicializar servidor:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('Recebido SIGTERM, encerrando servidor...');
  await simulationManager.stopAllSimulations();
  await databaseService.disconnect();
  await redisService.disconnect();
  server.close(() => {
    logger.info('Servidor encerrado');
    process.exit(0);
  });
});

process.on('SIGINT', async () => {
  logger.info('Recebido SIGINT, encerrando servidor...');
  await simulationManager.stopAllSimulations();
  await databaseService.disconnect();
  await redisService.disconnect();
  server.close(() => {
    logger.info('Servidor encerrado');
    process.exit(0);
  });
});

startServer();

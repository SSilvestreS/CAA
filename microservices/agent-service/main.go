package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gin-contrib/cors"
	"github.com/sirupsen/logrus"
	"github.com/spf13/viper"
	"github.com/redis/go-redis/v9"
	"github.com/lib/pq"
	"github.com/google/uuid"

	"smart-city-microservices/internal/agent"
	"smart-city-microservices/internal/database"
	"smart-city-microservices/internal/redis"
	"smart-city-microservices/internal/websocket"
	"smart-city-microservices/internal/middleware"
)

func main() {
	// Configurar logging
	logrus.SetFormatter(&logrus.JSONFormatter{})
	logrus.SetLevel(logrus.InfoLevel)

	// Carregar configurações
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.AddConfigPath("./configs")
	
	viper.SetDefault("server.port", "8080")
	viper.SetDefault("server.host", "0.0.0.0")
	viper.SetDefault("database.host", "localhost")
	viper.SetDefault("database.port", 5432)
	viper.SetDefault("database.name", "smart_city")
	viper.SetDefault("database.user", "postgres")
	viper.SetDefault("database.password", "password")
	viper.SetDefault("redis.host", "localhost")
	viper.SetDefault("redis.port", 6379)
	viper.SetDefault("redis.password", "")

	if err := viper.ReadInConfig(); err != nil {
		logrus.Warn("Arquivo de configuração não encontrado, usando padrões")
	}

	// Conectar ao banco de dados
	dbConfig := database.Config{
		Host:     viper.GetString("database.host"),
		Port:     viper.GetInt("database.port"),
		User:     viper.GetString("database.user"),
		Password: viper.GetString("database.password"),
		DBName:   viper.GetString("database.name"),
		SSLMode:  viper.GetString("database.sslmode"),
	}

	db, err := database.Connect(dbConfig)
	if err != nil {
		logrus.Fatal("Erro ao conectar ao banco de dados:", err)
	}
	defer db.Close()

	// Executar migrações
	if err := database.RunMigrations(db); err != nil {
		logrus.Fatal("Erro ao executar migrações:", err)
	}

	// Conectar ao Redis
	redisConfig := redis.Config{
		Host:     viper.GetString("redis.host"),
		Port:     viper.GetInt("redis.port"),
		Password: viper.GetString("redis.password"),
		DB:       0,
	}

	redisClient, err := redis.Connect(redisConfig)
	if err != nil {
		logrus.Fatal("Erro ao conectar ao Redis:", err)
	}
	defer redisClient.Close()

	// Inicializar serviços
	agentRepo := agent.NewRepository(db)
	agentService := agent.NewService(agentRepo, redisClient)
	agentHandler := agent.NewHandler(agentService)

	// Configurar Gin
	if viper.GetString("gin.mode") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// CORS
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000", "http://localhost:5000"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Middleware customizado
	router.Use(middleware.RequestID())
	router.Use(middleware.Logger())
	router.Use(middleware.Recovery())

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "ok",
			"service":   "agent-service",
			"version":   "1.1.0",
			"timestamp": time.Now().UTC(),
		})
	})

	// Rotas da API
	v1 := router.Group("/api/v1")
	{
		agents := v1.Group("/agents")
		{
			agents.GET("", agentHandler.GetAgents)
			agents.GET("/:id", agentHandler.GetAgent)
			agents.POST("", agentHandler.CreateAgent)
			agents.PUT("/:id", agentHandler.UpdateAgent)
			agents.DELETE("/:id", agentHandler.DeleteAgent)
			agents.POST("/:id/actions", agentHandler.ExecuteAction)
			agents.GET("/:id/performance", agentHandler.GetPerformance)
		}

		simulations := v1.Group("/simulations")
		{
			simulations.GET("", agentHandler.GetSimulations)
			simulations.POST("", agentHandler.CreateSimulation)
			simulations.GET("/:id", agentHandler.GetSimulation)
			simulations.PUT("/:id/start", agentHandler.StartSimulation)
			simulations.PUT("/:id/stop", agentHandler.StopSimulation)
		}
	}

	// WebSocket para comunicação em tempo real
	wsHub := websocket.NewHub()
	go wsHub.Run()

	router.GET("/ws", func(c *gin.Context) {
		websocket.HandleWebSocket(wsHub, c)
	})

	// Configurar servidor
	server := &http.Server{
		Addr:         viper.GetString("server.host") + ":" + viper.GetString("server.port"),
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Iniciar servidor em goroutine
	go func() {
		logrus.Infof("Servidor de agentes iniciado em %s", server.Addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logrus.Fatal("Erro ao iniciar servidor:", err)
		}
	}()

	// Aguardar sinal de interrupção
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logrus.Info("Encerrando servidor...")

	// Graceful shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		logrus.Fatal("Erro ao encerrar servidor:", err)
	}

	logrus.Info("Servidor encerrado")
}

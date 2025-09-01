// @title Liora Backend API
// @version 1.0
// @description AI-powered startup analysis platform that evaluates startups by synthesizing founder materials and public data to generate investment insights.
// @termsOfService http://swagger.io/terms/

// @contact.name Liora Team
// @contact.email team@liora.ai

// @license.name MIT
// @license.url https://opensource.org/licenses/MIT

// @host localhost:8080
// @BasePath /
// @schemes http https

// @accept json
// @produce json

package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	"liora-backend/config"
	_ "liora-backend/docs"
	"liora-backend/handlers"
	"liora-backend/middleware"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system environment variables")
	}

	// Initialize configuration
	cfg := config.New()

	// Set Gin mode
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Initialize router
	r := gin.New()

	// Add middleware
	r.Use(gin.Logger())
	r.Use(gin.Recovery())
	r.Use(middleware.CORSMiddleware(cfg.CORSOrigins))

	// Health check endpoint
	r.GET("/health", handlers.HealthCheck)

	// Swagger documentation
	r.GET("/docs/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// API routes
	v1 := r.Group("/api/v1")
	{
		// Health and status
		v1.GET("/status", handlers.APIStatus)

		// File upload routes
		v1.POST("/upload", handlers.UploadFiles)
		v1.GET("/uploads/:id", handlers.GetUploadStatus)
		v1.DELETE("/uploads/:id", handlers.DeleteUpload)

		// Company routes
		v1.POST("/companies", handlers.CreateCompany)
		v1.GET("/companies/:id", handlers.GetCompany)
		v1.PUT("/companies/:id", handlers.UpdateCompany)

		// Analysis routes
		v1.POST("/analysis/start", handlers.StartAnalysis)
		v1.GET("/analysis/:id", handlers.GetAnalysis)
		v1.GET("/analysis/:id/status", handlers.GetAnalysisStatus)
		v1.GET("/analysis/:id/report", handlers.GetAnalysisReport)
	}

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
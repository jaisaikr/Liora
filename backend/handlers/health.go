package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"liora-backend/utils"
)

type HealthStatus struct {
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
	Version   string    `json:"version"`
}

type APIStatusResponse struct {
	API       string    `json:"api"`
	Version   string    `json:"version"`
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
	Endpoints []string  `json:"endpoints"`
}

// HealthCheck godoc
// @Summary Health check endpoint
// @Description Check if the API is running and healthy
// @Tags health
// @Accept json
// @Produce json
// @Success 200 {object} HealthStatus
// @Router /health [get]
func HealthCheck(c *gin.Context) {
	health := HealthStatus{
		Status:    "healthy",
		Timestamp: time.Now(),
		Version:   "1.0.0",
	}
	
	c.JSON(http.StatusOK, health)
}

// APIStatus godoc
// @Summary API status and information
// @Description Get API status, version, and available endpoints
// @Tags health
// @Accept json
// @Produce json
// @Success 200 {object} utils.APIResponse{data=APIStatusResponse}
// @Router /api/v1/status [get]
func APIStatus(c *gin.Context) {
	status := APIStatusResponse{
		API:       "Liora Backend API",
		Version:   "v1",
		Status:    "operational",
		Timestamp: time.Now(),
		Endpoints: []string{
			"GET /health",
			"GET /api/v1/status",
			"POST /api/v1/upload",
			"GET /api/v1/uploads/:id",
			"DELETE /api/v1/uploads/:id",
			"POST /api/v1/companies",
			"GET /api/v1/companies/:id",
			"PUT /api/v1/companies/:id",
			"POST /api/v1/analysis/start",
			"GET /api/v1/analysis/:id",
			"GET /api/v1/analysis/:id/status",
			"GET /api/v1/analysis/:id/report",
		},
	}

	utils.SuccessResponse(c, status)
}
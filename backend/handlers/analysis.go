package handlers

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"

	"liora-backend/models"
	"liora-backend/utils"
)

var (
	// In-memory storage for analyses (replace with database in production)
	analyses = make(map[string]models.Analysis)
)

// Mock data generators
func generateMockMetrics() []models.Metric {
	metrics := []models.Metric{
		{Label: "Market Potential", Value: 7.0 + rand.Float64()*3.0, Color: "text-green-600"},
		{Label: "Team Strength", Value: 6.5 + rand.Float64()*3.5, Color: "text-green-600"},
		{Label: "Product Viability", Value: 6.0 + rand.Float64()*4.0, Color: "text-yellow-600"},
		{Label: "Financial Health", Value: 5.5 + rand.Float64()*4.5, Color: "text-yellow-600"},
	}

	// Adjust colors based on values
	for i := range metrics {
		if metrics[i].Value >= 8.0 {
			metrics[i].Color = "text-green-600"
		} else if metrics[i].Value >= 6.0 {
			metrics[i].Color = "text-yellow-600"
		} else {
			metrics[i].Color = "text-red-600"
		}
	}

	return metrics
}

func generateMockInsights() []string {
	insights := [][]string{
		{
			"Strong founding team with relevant industry experience",
			"Large addressable market with growing demand",
			"Competitive product differentiation identified",
			"Revenue growth trajectory shows positive momentum",
		},
		{
			"Experienced leadership team with proven track record",
			"Innovative technology with patent protection",
			"Strong customer acquisition metrics",
			"Clear path to market expansion",
		},
		{
			"Well-defined value proposition resonates with target market",
			"Solid financial projections with conservative assumptions",
			"Strategic partnerships provide competitive advantage",
			"Scalable business model with recurring revenue potential",
		},
	}

	return insights[rand.Intn(len(insights))]
}

func generateMockRisks() []string {
	risks := [][]string{
		{
			"High competition in target market segment",
			"Dependency on key partnerships for distribution",
			"Limited runway based on current burn rate",
		},
		{
			"Regulatory challenges in target markets",
			"Customer concentration risk with top clients",
			"Technology scalability concerns at growth stage",
		},
		{
			"Market timing risks for product launch",
			"Key person dependency on founders",
			"Potential intellectual property disputes",
		},
	}

	return risks[rand.Intn(len(risks))]
}

func generateRecommendation(score float64) string {
	if score >= 8.5 {
		return "Exceptional Investment Opportunity"
	} else if score >= 7.5 {
		return "Strong Investment Opportunity"
	} else if score >= 6.5 {
		return "Moderate Investment Potential"
	} else if score >= 5.5 {
		return "Proceed with Caution"
	} else {
		return "High Risk Investment"
	}
}

// StartAnalysis godoc
// @Summary Start startup analysis
// @Description Initiate AI-powered analysis of a startup using uploaded materials
// @Tags analysis
// @Accept json
// @Produce json
// @Param analysis body models.StartAnalysisRequest true "Analysis request"
// @Success 200 {object} utils.APIResponse{data=models.Analysis}
// @Failure 400 {object} utils.APIResponse
// @Failure 404 {object} utils.APIResponse
// @Router /api/v1/analysis/start [post]
func StartAnalysis(c *gin.Context) {
	var req models.StartAnalysisRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ValidationErrorResponse(c, err.Error())
		return
	}

	// Validate company exists
	if _, exists := companies[req.CompanyID]; !exists {
		utils.NotFoundResponse(c, "Company")
		return
	}

	// Validate files exist
	for _, fileID := range req.FileIDs {
		if _, exists := uploadedFiles[fileID]; !exists {
			utils.ValidationErrorResponse(c, fmt.Sprintf("File %s not found", fileID))
			return
		}
	}

	// Create new analysis
	analysis := models.Analysis{
		ID:        uuid.New().String(),
		CompanyID: req.CompanyID,
		Status:    models.StatusPending,
		Progress:  0,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Store analysis
	analyses[analysis.ID] = analysis

	// Start mock processing (in real app, this would trigger background processing)
	go simulateAnalysisProcessing(analysis.ID)

	utils.SuccessResponseWithMessage(c, analysis, "Analysis started successfully")
}

func simulateAnalysisProcessing(analysisID string) {
	// Simulate processing stages
	stages := []struct {
		status   models.AnalysisStatus
		progress int
		duration time.Duration
	}{
		{models.StatusProcessing, 25, 2 * time.Second},
		{models.StatusProcessing, 50, 3 * time.Second},
		{models.StatusProcessing, 75, 2 * time.Second},
		{models.StatusCompleted, 100, 1 * time.Second},
	}

	for _, stage := range stages {
		time.Sleep(stage.duration)

		analysis := analyses[analysisID]
		analysis.Status = stage.status
		analysis.Progress = stage.progress
		analysis.UpdatedAt = time.Now()

		if stage.status == models.StatusCompleted {
			// Generate mock results
			metrics := generateMockMetrics()
			overallScore := 0.0
			for _, metric := range metrics {
				overallScore += metric.Value
			}
			overallScore = overallScore / float64(len(metrics))

			analysis.OverallScore = overallScore
			analysis.Recommendation = generateRecommendation(overallScore)
			analysis.KeyMetrics = metrics
			analysis.Insights = generateMockInsights()
			analysis.Risks = generateMockRisks()
			
			now := time.Now()
			analysis.CompletedAt = &now
		}

		analyses[analysisID] = analysis
	}
}

// GetAnalysis godoc
// @Summary Get analysis results
// @Description Get complete analysis results including scores, insights, and recommendations
// @Tags analysis
// @Accept json
// @Produce json
// @Param id path string true "Analysis ID"
// @Success 200 {object} utils.APIResponse{data=models.Analysis}
// @Failure 404 {object} utils.APIResponse
// @Router /api/v1/analysis/{id} [get]
func GetAnalysis(c *gin.Context) {
	analysisID := c.Param("id")

	analysis, exists := analyses[analysisID]
	if !exists {
		utils.NotFoundResponse(c, "Analysis")
		return
	}

	utils.SuccessResponse(c, analysis)
}

// GetAnalysisStatus godoc
// @Summary Get analysis status
// @Description Get current status and progress of an analysis
// @Tags analysis
// @Accept json
// @Produce json
// @Param id path string true "Analysis ID"
// @Success 200 {object} utils.APIResponse{data=models.AnalysisStatusResponse}
// @Failure 404 {object} utils.APIResponse
// @Router /api/v1/analysis/{id}/status [get]
func GetAnalysisStatus(c *gin.Context) {
	analysisID := c.Param("id")

	analysis, exists := analyses[analysisID]
	if !exists {
		utils.NotFoundResponse(c, "Analysis")
		return
	}

	var message string
	switch analysis.Status {
	case models.StatusPending:
		message = "Analysis queued for processing"
	case models.StatusProcessing:
		message = "Analysis in progress"
	case models.StatusCompleted:
		message = "Analysis completed successfully"
	case models.StatusFailed:
		message = "Analysis failed"
	}

	status := models.AnalysisStatusResponse{
		ID:       analysis.ID,
		Status:   analysis.Status,
		Progress: analysis.Progress,
		Message:  message,
	}

	utils.SuccessResponse(c, status)
}

// GetAnalysisReport godoc
// @Summary Download analysis report
// @Description Download comprehensive analysis report (PDF format)
// @Tags analysis
// @Accept json
// @Produce json
// @Param id path string true "Analysis ID"
// @Success 200 {object} utils.APIResponse{data=models.Analysis}
// @Failure 400 {object} utils.APIResponse
// @Failure 404 {object} utils.APIResponse
// @Router /api/v1/analysis/{id}/report [get]
func GetAnalysisReport(c *gin.Context) {
	analysisID := c.Param("id")

	analysis, exists := analyses[analysisID]
	if !exists {
		utils.NotFoundResponse(c, "Analysis")
		return
	}

	if analysis.Status != models.StatusCompleted {
		utils.ValidationErrorResponse(c, "Analysis not completed yet")
		return
	}

	// In a real application, this would generate and return a PDF report
	// For now, we'll return the analysis data
	utils.SuccessResponseWithMessage(c, analysis, "Report generated successfully")
}
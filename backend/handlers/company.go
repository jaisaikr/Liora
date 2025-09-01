package handlers

import (
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"

	"liora-backend/models"
	"liora-backend/utils"
)

var (
	// In-memory storage for companies (replace with database in production)
	companies = make(map[string]models.Company)
)

// CreateCompany godoc
// @Summary Create a new company
// @Description Create a new company profile for analysis
// @Tags companies
// @Accept json
// @Produce json
// @Param company body models.CreateCompanyRequest true "Company information"
// @Success 200 {object} utils.APIResponse{data=models.Company}
// @Failure 400 {object} utils.APIResponse
// @Router /api/v1/companies [post]
func CreateCompany(c *gin.Context) {
	var req models.CreateCompanyRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ValidationErrorResponse(c, err.Error())
		return
	}

	// Create new company
	company := models.Company{
		ID:           uuid.New().String(),
		Name:         req.Name,
		Industry:     req.Industry,
		Website:      req.Website,
		FundingStage: req.FundingStage,
		Description:  req.Description,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}

	// Store in memory (replace with database)
	companies[company.ID] = company

	utils.SuccessResponseWithMessage(c, company, "Company created successfully")
}

// GetCompany godoc
// @Summary Get company details
// @Description Get company information by ID
// @Tags companies
// @Accept json
// @Produce json
// @Param id path string true "Company ID"
// @Success 200 {object} utils.APIResponse{data=models.Company}
// @Failure 404 {object} utils.APIResponse
// @Router /api/v1/companies/{id} [get]
func GetCompany(c *gin.Context) {
	companyID := c.Param("id")

	company, exists := companies[companyID]
	if !exists {
		utils.NotFoundResponse(c, "Company")
		return
	}

	utils.SuccessResponse(c, company)
}

// UpdateCompany godoc
// @Summary Update company information
// @Description Update company details by ID
// @Tags companies
// @Accept json
// @Produce json
// @Param id path string true "Company ID"
// @Param company body models.UpdateCompanyRequest true "Updated company information"
// @Success 200 {object} utils.APIResponse{data=models.Company}
// @Failure 400 {object} utils.APIResponse
// @Failure 404 {object} utils.APIResponse
// @Router /api/v1/companies/{id} [put]
func UpdateCompany(c *gin.Context) {
	companyID := c.Param("id")

	company, exists := companies[companyID]
	if !exists {
		utils.NotFoundResponse(c, "Company")
		return
	}

	var req models.UpdateCompanyRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.ValidationErrorResponse(c, err.Error())
		return
	}

	// Update fields if provided
	if req.Name != "" {
		company.Name = req.Name
	}
	if req.Industry != "" {
		company.Industry = req.Industry
	}
	if req.Website != "" {
		company.Website = req.Website
	}
	if req.FundingStage != "" {
		company.FundingStage = req.FundingStage
	}
	if req.Description != "" {
		company.Description = req.Description
	}

	company.UpdatedAt = time.Now()

	// Store updated company
	companies[companyID] = company

	utils.SuccessResponseWithMessage(c, company, "Company updated successfully")
}
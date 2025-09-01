package models

import (
	"time"
)

type Company struct {
	ID           string    `json:"id"`
	Name         string    `json:"name" binding:"required"`
	Industry     string    `json:"industry" binding:"required"`
	Website      string    `json:"website"`
	FundingStage string    `json:"funding_stage" binding:"required"`
	Description  string    `json:"description"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

type CreateCompanyRequest struct {
	Name         string `json:"name" binding:"required"`
	Industry     string `json:"industry" binding:"required"`
	Website      string `json:"website"`
	FundingStage string `json:"funding_stage" binding:"required"`
	Description  string `json:"description"`
}

type UpdateCompanyRequest struct {
	Name         string `json:"name"`
	Industry     string `json:"industry"`
	Website      string `json:"website"`
	FundingStage string `json:"funding_stage"`
	Description  string `json:"description"`
}
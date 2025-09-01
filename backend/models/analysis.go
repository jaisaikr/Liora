package models

import (
	"time"
)

type AnalysisStatus string

const (
	StatusPending    AnalysisStatus = "pending"
	StatusProcessing AnalysisStatus = "processing"
	StatusCompleted  AnalysisStatus = "completed"
	StatusFailed     AnalysisStatus = "failed"
)

type Metric struct {
	Label string  `json:"label"`
	Value float64 `json:"value"`
	Color string  `json:"color"`
}

type Analysis struct {
	ID             string         `json:"id"`
	CompanyID      string         `json:"company_id"`
	Status         AnalysisStatus `json:"status"`
	Progress       int            `json:"progress"` // 0-100
	OverallScore   float64        `json:"overall_score"`
	Recommendation string         `json:"recommendation"`
	KeyMetrics     []Metric       `json:"key_metrics"`
	Insights       []string       `json:"insights"`
	Risks          []string       `json:"risks"`
	CreatedAt      time.Time      `json:"created_at"`
	UpdatedAt      time.Time      `json:"updated_at"`
	CompletedAt    *time.Time     `json:"completed_at,omitempty"`
}

type StartAnalysisRequest struct {
	CompanyID string   `json:"company_id" binding:"required"`
	FileIDs   []string `json:"file_ids" binding:"required"`
}

type AnalysisStatusResponse struct {
	ID       string         `json:"id"`
	Status   AnalysisStatus `json:"status"`
	Progress int            `json:"progress"`
	Message  string         `json:"message"`
}

type UploadedFile struct {
	ID           string    `json:"id"`
	Filename     string    `json:"filename"`
	OriginalName string    `json:"original_name"`
	Size         int64     `json:"size"`
	ContentType  string    `json:"content_type"`
	UploadedAt   time.Time `json:"uploaded_at"`
	Status       string    `json:"status"` // uploaded, processing, processed, error
}

type UploadResponse struct {
	Files []UploadedFile `json:"files"`
}
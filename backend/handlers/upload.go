package handlers

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"

	"liora-backend/models"
	"liora-backend/utils"
)

var (
	// In-memory storage for uploaded files (replace with database in production)
	uploadedFiles = make(map[string]models.UploadedFile)
)

var allowedFileTypes = map[string]bool{
	".pdf":  true,
	".doc":  true,
	".docx": true,
	".ppt":  true,
	".pptx": true,
	".xls":  true,
	".xlsx": true,
	".txt":  true,
}

// UploadFiles godoc
// @Summary Upload founder materials and documents
// @Description Upload multiple files (PDF, DOC, PPT, XLS, TXT) for analysis
// @Tags upload
// @Accept multipart/form-data
// @Produce json
// @Param files formData file true "Files to upload" 
// @Success 200 {object} utils.APIResponse{data=models.UploadResponse}
// @Failure 400 {object} utils.APIResponse
// @Failure 500 {object} utils.APIResponse
// @Router /api/v1/upload [post]
func UploadFiles(c *gin.Context) {
	// Create uploads directory if it doesn't exist
	uploadDir := "./uploads"
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		utils.InternalServerErrorResponse(c, "Failed to create upload directory")
		return
	}

	// Parse multipart form
	form, err := c.MultipartForm()
	if err != nil {
		utils.ValidationErrorResponse(c, "Invalid multipart form")
		return
	}

	files := form.File["files"]
	if len(files) == 0 {
		utils.ValidationErrorResponse(c, "No files provided")
		return
	}

	var uploadedFilesList []models.UploadedFile

	for _, file := range files {
		// Validate file type
		ext := strings.ToLower(filepath.Ext(file.Filename))
		if !allowedFileTypes[ext] {
			utils.ValidationErrorResponse(c, fmt.Sprintf("File type %s not allowed", ext))
			return
		}

		// Validate file size (10MB limit)
		if file.Size > 10*1024*1024 {
			utils.ValidationErrorResponse(c, fmt.Sprintf("File %s exceeds size limit", file.Filename))
			return
		}

		// Generate unique filename
		fileID := uuid.New().String()
		filename := fmt.Sprintf("%s%s", fileID, ext)
		filepath := filepath.Join(uploadDir, filename)

		// Save file
		src, err := file.Open()
		if err != nil {
			utils.InternalServerErrorResponse(c, "Failed to open uploaded file")
			return
		}
		defer src.Close()

		dst, err := os.Create(filepath)
		if err != nil {
			utils.InternalServerErrorResponse(c, "Failed to create file")
			return
		}
		defer dst.Close()

		if _, err := io.Copy(dst, src); err != nil {
			utils.InternalServerErrorResponse(c, "Failed to save file")
			return
		}

		// Create file record
		uploadedFile := models.UploadedFile{
			ID:           fileID,
			Filename:     filename,
			OriginalName: file.Filename,
			Size:         file.Size,
			ContentType:  file.Header.Get("Content-Type"),
			UploadedAt:   time.Now(),
			Status:       "uploaded",
		}

		// Store in memory (replace with database)
		uploadedFiles[fileID] = uploadedFile
		uploadedFilesList = append(uploadedFilesList, uploadedFile)
	}

	response := models.UploadResponse{
		Files: uploadedFilesList,
	}

	utils.SuccessResponseWithMessage(c, response, fmt.Sprintf("Successfully uploaded %d files", len(uploadedFilesList)))
}

// GetUploadStatus godoc
// @Summary Get upload file status
// @Description Get status and details of an uploaded file
// @Tags upload
// @Accept json
// @Produce json
// @Param id path string true "File ID"
// @Success 200 {object} utils.APIResponse{data=models.UploadedFile}
// @Failure 404 {object} utils.APIResponse
// @Router /api/v1/uploads/{id} [get]
func GetUploadStatus(c *gin.Context) {
	fileID := c.Param("id")

	file, exists := uploadedFiles[fileID]
	if !exists {
		utils.NotFoundResponse(c, "File")
		return
	}

	utils.SuccessResponse(c, file)
}

// DeleteUpload godoc
// @Summary Delete uploaded file
// @Description Delete an uploaded file from storage
// @Tags upload
// @Accept json
// @Produce json
// @Param id path string true "File ID"
// @Success 200 {object} utils.APIResponse
// @Failure 404 {object} utils.APIResponse
// @Failure 500 {object} utils.APIResponse
// @Router /api/v1/uploads/{id} [delete]
func DeleteUpload(c *gin.Context) {
	fileID := c.Param("id")

	file, exists := uploadedFiles[fileID]
	if !exists {
		utils.NotFoundResponse(c, "File")
		return
	}

	// Delete physical file
	filepath := filepath.Join("./uploads", file.Filename)
	if err := os.Remove(filepath); err != nil {
		utils.InternalServerErrorResponse(c, "Failed to delete file")
		return
	}

	// Remove from memory storage
	delete(uploadedFiles, fileID)

	utils.SuccessResponseWithMessage(c, nil, "File deleted successfully")
}
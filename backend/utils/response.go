package utils

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type APIResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
	Message string      `json:"message,omitempty"`
}

func SuccessResponse(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, APIResponse{
		Success: true,
		Data:    data,
	})
}

func SuccessResponseWithMessage(c *gin.Context, data interface{}, message string) {
	c.JSON(http.StatusOK, APIResponse{
		Success: true,
		Data:    data,
		Message: message,
	})
}

func ErrorResponse(c *gin.Context, statusCode int, error string) {
	c.JSON(statusCode, APIResponse{
		Success: false,
		Error:   error,
	})
}

func ValidationErrorResponse(c *gin.Context, error string) {
	ErrorResponse(c, http.StatusBadRequest, error)
}

func NotFoundResponse(c *gin.Context, resource string) {
	ErrorResponse(c, http.StatusNotFound, resource+" not found")
}

func InternalServerErrorResponse(c *gin.Context, error string) {
	ErrorResponse(c, http.StatusInternalServerError, error)
}
package config

import (
	"os"
	"strconv"
	"strings"
)

type Config struct {
	Port           string
	Environment    string
	APIVersion     string
	UploadDir      string
	MaxUploadSize  int64
	CORSOrigins    []string
}

func New() *Config {
	return &Config{
		Port:           getEnv("PORT", "8080"),
		Environment:    getEnv("ENVIRONMENT", "development"),
		APIVersion:     getEnv("API_VERSION", "v1"),
		UploadDir:      getEnv("UPLOAD_DIR", "./uploads"),
		MaxUploadSize:  getEnvAsInt64("MAX_UPLOAD_SIZE", 10485760), // 10MB default
		CORSOrigins:    getEnvAsSlice("CORS_ORIGINS", []string{"http://localhost:5173"}),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt64(key string, defaultValue int64) int64 {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.ParseInt(value, 10, 64); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvAsSlice(key string, defaultValue []string) []string {
	if value := os.Getenv(key); value != "" {
		return strings.Split(value, ",")
	}
	return defaultValue
}
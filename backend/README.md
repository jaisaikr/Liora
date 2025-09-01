# Liora Backend

The backend API for Liora, an AI-powered analyst platform that evaluates startups by synthesizing founder materials and public data to generate concise, actionable investment insights.

## Tech Stack

- **Language**: Go (Golang)
- **Framework**: Gin Web Framework
- **Documentation**: Swagger/OpenAPI 3.0
- **Libraries**: UUID, godotenv, CORS middleware

## Getting Started

### Prerequisites

- Go 1.21 or higher
- Git
- Swag CLI tool for API documentation

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   go mod tidy
   ```

3. Install Swag CLI (if not already installed):
   ```bash
   go install github.com/swaggo/swag/cmd/swag@latest
   ```
   
   Make sure your GOPATH/bin is in your PATH environment variable.

4. Generate Swagger documentation:
   ```bash
   swag init
   ```

### Development

To run the development server:

```bash
go run main.go
```

The API will be available at `http://localhost:8080` (or the configured port).

## API Documentation

Interactive Swagger UI is available at: `http://localhost:8080/docs/index.html`

JSON OpenAPI specification: `http://localhost:8080/docs/doc.json`

### Updating API Documentation

When you add, modify, or remove API endpoints:

1. **Add Swagger annotations** to your handler functions following this pattern:
   ```go
   // HandlerName godoc
   // @Summary Brief description
   // @Description Detailed description  
   // @Tags tag-name
   // @Accept json
   // @Produce json
   // @Param paramName path/query/body type true/false "Description"
   // @Success 200 {object} ResponseType
   // @Failure 400 {object} utils.APIResponse
   // @Router /api/v1/endpoint [method]
   func HandlerName(c *gin.Context) {
   ```

2. **Regenerate documentation**:
   ```bash
   swag init
   ```

3. **Restart the server** to see updated documentation:
   ```bash
   go run main.go
   ```

The documentation will be automatically updated at `/docs/` endpoint.

## Project Structure

```
backend/
├── main.go         # Application entry point with API metadata
├── docs/           # Generated Swagger documentation (auto-generated)
│   ├── docs.go     # Embedded OpenAPI specification
│   ├── swagger.json # JSON format OpenAPI spec
│   └── swagger.yaml # YAML format OpenAPI spec
├── handlers/       # HTTP request handlers with Swagger annotations
├── models/         # Data models and structures
├── services/       # Business logic layer
├── middleware/     # HTTP middleware (CORS, logging)
├── config/         # Configuration management
├── utils/          # Utility functions and response helpers
└── uploads/        # File upload storage (created at runtime)
```

## API Endpoints

### Health & Status
- `GET /health` - Health check endpoint
- `GET /api/v1/status` - API status and information

### File Upload
- `POST /api/v1/upload` - Upload founder materials (PDF, DOC, PPT, XLS, TXT)
- `GET /api/v1/uploads/:id` - Get upload status
- `DELETE /api/v1/uploads/:id` - Delete uploaded file

### Company Management
- `POST /api/v1/companies` - Create company profile
- `GET /api/v1/companies/:id` - Get company details
- `PUT /api/v1/companies/:id` - Update company information

### Analysis Engine
- `POST /api/v1/analysis/start` - Initiate startup analysis
- `GET /api/v1/analysis/:id` - Get analysis results
- `GET /api/v1/analysis/:id/status` - Check analysis progress
- `GET /api/v1/analysis/:id/report` - Download analysis report

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
PORT=8080
API_VERSION=v1
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
CORS_ORIGINS=http://localhost:5173
```

## Available Commands

- `go run main.go` - Start development server
- `go build` - Build the application
- `go test ./...` - Run all tests
- `go mod tidy` - Clean up dependencies
- `swag init` - Generate/update Swagger documentation
- `swag fmt` - Format Swagger annotations

## Contributing

Please follow Go conventions and best practices when contributing to this project:

1. **Add Swagger annotations** for any new endpoints
2. **Run `swag init`** after adding/modifying API endpoints
3. **Test your changes** using the Swagger UI at `/docs/`
4. **Ensure all tests pass** before submitting pull requests
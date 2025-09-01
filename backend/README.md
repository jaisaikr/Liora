# Liora Backend

The backend API for Liora, an AI-powered analyst platform that evaluates startups by synthesizing founder materials and public data to generate concise, actionable investment insights.

## Tech Stack

- **Language**: Go (Golang)
- **Framework**: Standard library with additional packages as needed

## Getting Started

### Prerequisites

- Go 1.21 or higher
- Git

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Initialize Go modules (if not already done):
   ```bash
   go mod init liora-backend
   ```

3. Install dependencies:
   ```bash
   go mod tidy
   ```

### Development

To run the development server:

```bash
go run main.go
```

The API will be available at `http://localhost:8080` (or the configured port).

## Project Structure

```
backend/
├── main.go         # Application entry point
├── handlers/       # HTTP request handlers
├── models/         # Data models and structures
├── services/       # Business logic layer
├── middleware/     # HTTP middleware
├── config/         # Configuration management
├── utils/          # Utility functions
└── tests/          # Test files
```

## API Endpoints

The backend provides RESTful API endpoints for:

- Startup data ingestion and processing
- AI-powered analysis generation
- Investment insights retrieval
- User authentication and management

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
PORT=8080
DATABASE_URL=your_database_connection_string
API_KEY=your_api_key
```

## Available Commands

- `go run main.go` - Start development server
- `go build` - Build the application
- `go test ./...` - Run all tests
- `go mod tidy` - Clean up dependencies
- `go mod download` - Download dependencies

## Contributing

Please follow Go conventions and best practices when contributing to this project. Ensure all tests pass before submitting pull requests.
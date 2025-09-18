# Liora Platform System Design

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Layer                              │
├─────────────────────────────────────────────────────────────────────┤
│  Web Application (React/Next.js)  │  Mobile Apps (Future - Phase 2) │
└──────────────┬──────────────────────────────────┬──────────────────┘
               │                                  │
               ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          API Gateway                                │
│                    (FastAPI + Rate Limiting)                        │
└──────────────┬──────────────────────────────────┬──────────────────┘
               │                                  │
               ▼                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Application Services Layer                      │
├────────────────┬─────────────────┬─────────────────┬────────────────┤
│ Auth Service   │  User Service   │ Company Service │ Meeting Service│
├────────────────┼─────────────────┼─────────────────┼────────────────┤
│ Upload Service │ Search Service  │ Analytics Service│ Notification  │
└────────────────┴─────────────────┴─────────────────┴────────────────┘
               │                                  │
               ▼                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        AI Agent Orchestration                        │
├─────────────────────┬──────────────────┬────────────────────────────┤
│  Summarize Agent    │ Questionnaire    │  Investment Memo Agent     │
│  (Google ADK)       │ Agent (ADK)      │     (Google ADK)          │
└─────────────────────┴──────────────────┴────────────────────────────┘
               │                                  │
               ▼                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                   │
├──────────────┬──────────────┬───────────────┬───────────────────────┤
│ PostgreSQL   │    Redis     │  S3 Storage   │ Elasticsearch (P2)    │
│  (Primary)   │   (Cache)    │   (Files)     │    (Search)          │
└──────────────┴──────────────┴───────────────┴───────────────────────┘
               │                                  │
               ▼                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    External Services                                 │
├──────────────┬──────────────┬───────────────┬───────────────────────┤
│ Email (SMTP) │ Transcription│ Market Data   │  Social Media APIs    │
│              │   Services   │     APIs      │                       │
└──────────────┴──────────────┴───────────────┴───────────────────────┘
```

### 1.2 Component Interaction Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Frontend │────▶│   API    │────▶│ Services │────▶│  Agents  │
│          │◀────│ Gateway  │◀────│          │◀────│          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                 │                │
     │                │                 │                │
     ▼                ▼                 ▼                ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Users   │     │   Auth   │     │Database  │     │  Queue   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

## 2. Database Design

### 2.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Core Entities                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐        ┌──────────────┐        ┌──────────────┐    │
│  │  Users   │───────▶│   Companies  │───────▶│  Documents   │    │
│  └──────────┘        └──────────────┘        └──────────────┘    │
│       │                     │                        │            │
│       │                     │                        │            │
│       ▼                     ▼                        ▼            │
│  ┌──────────┐        ┌──────────────┐        ┌──────────────┐    │
│  │ Profiles │        │Questionnaires│        │ Transcripts  │    │
│  └──────────┘        └──────────────┘        └──────────────┘    │
│       │                     │                        │            │
│       │                     │                        │            │
│       ▼                     ▼                        ▼            │
│  ┌──────────┐        ┌──────────────┐        ┌──────────────┐    │
│  │Preferences│        │  Interviews  │        │    Memos     │    │
│  └──────────┘        └──────────────┘        └──────────────┘    │
│       │                     │                        │            │
│       │                     │                        │            │
│       ▼                     ▼                        ▼            │
│  ┌──────────┐        ┌──────────────┐        ┌──────────────┐    │
│  │ Meetings │◀───────│   Schedules  │───────▶│Notifications │    │
│  └──────────┘        └──────────────┘        └──────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('founder', 'investor', 'admin')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Profiles
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    profile_picture_url VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Companies
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    founder_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    sub_industry VARCHAR(100),
    stage VARCHAR(50) NOT NULL,
    founded_date DATE,
    headquarters_location VARCHAR(255),
    team_size INTEGER,
    website_url VARCHAR(500),
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    upload_status VARCHAR(50) DEFAULT 'pending',
    processed_at TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questionnaires
CREATE TABLE questionnaires (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    questions JSONB NOT NULL,
    responses JSONB,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interviews
CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 45,
    meeting_url VARCHAR(500),
    recording_url VARCHAR(500),
    transcript_id UUID,
    status VARCHAR(50) DEFAULT 'scheduled',
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Investment Memos
CREATE TABLE investment_memos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    version VARCHAR(10) NOT NULL,
    executive_summary TEXT,
    market_analysis JSONB,
    product_analysis JSONB,
    team_analysis JSONB,
    financial_analysis JSONB,
    competition_analysis JSONB,
    risk_assessment JSONB,
    ai_insights JSONB,
    full_content JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Investor Preferences
CREATE TABLE investor_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investor_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sectors JSONB,
    stages JSONB,
    check_size_min DECIMAL(15, 2),
    check_size_max DECIMAL(15, 2),
    geographic_preferences JSONB,
    scoring_weights JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meetings
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    investor_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    meeting_type VARCHAR(50),
    meeting_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_companies_founder ON companies(founder_id);
CREATE INDEX idx_companies_status ON companies(status);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_documents_company ON documents(company_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_memos_company ON investment_memos(company_id);
CREATE INDEX idx_meetings_company ON meetings(company_id);
CREATE INDEX idx_meetings_investor ON meetings(investor_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
```

## 3. API Design

### 3.1 API Structure

```
/api/v1/
├── auth/
│   ├── POST   /register
│   ├── POST   /login
│   ├── POST   /logout
│   ├── POST   /refresh
│   └── POST   /reset-password
├── users/
│   ├── GET    /me
│   ├── PUT    /me
│   ├── GET    /{user_id}
│   └── PUT    /{user_id}/profile
├── companies/
│   ├── GET    /                  # List with filters
│   ├── POST   /                  # Create company
│   ├── GET    /{company_id}
│   ├── PUT    /{company_id}
│   ├── DELETE /{company_id}
│   └── PUT    /{company_id}/status
├── documents/
│   ├── POST   /upload
│   ├── GET    /{document_id}
│   ├── DELETE /{document_id}
│   └── GET    /company/{company_id}
├── questionnaires/
│   ├── POST   /generate
│   ├── GET    /{questionnaire_id}
│   ├── PUT    /{questionnaire_id}/responses
│   └── POST   /{questionnaire_id}/submit
├── interviews/
│   ├── POST   /schedule
│   ├── GET    /{interview_id}
│   ├── PUT    /{interview_id}/status
│   └── POST   /{interview_id}/transcript
├── memos/
│   ├── GET    /company/{company_id}
│   ├── GET    /{memo_id}
│   └── POST   /generate
├── preferences/
│   ├── GET    /
│   ├── PUT    /
│   └── DELETE /
├── meetings/
│   ├── POST   /request
│   ├── GET    /
│   ├── GET    /{meeting_id}
│   └── PUT    /{meeting_id}/status
└── search/
    ├── POST   /companies
    └── GET    /suggestions
```

### 3.2 API Request/Response Examples

```python
# Authentication
POST /api/v1/auth/register
{
    "email": "founder@startup.com",
    "password": "SecurePass123!",
    "role": "founder",
    "full_name": "John Doe"
}
Response: {
    "user_id": "uuid",
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 3600
}

# Company Creation
POST /api/v1/companies
{
    "name": "TechStartup Inc.",
    "industry": "Technology",
    "sub_industry": "SaaS",
    "stage": "Seed",
    "founded_date": "2022-01-15",
    "headquarters_location": "San Francisco, CA",
    "team_size": 12,
    "website_url": "https://techstartup.com",
    "description": "AI-powered analytics platform"
}
Response: {
    "company_id": "uuid",
    "status": "draft",
    "created_at": "2024-01-20T10:30:00Z"
}

# Document Upload
POST /api/v1/documents/upload
Content-Type: multipart/form-data
{
    "company_id": "uuid",
    "document_type": "pitch_deck",
    "file": <binary>
}
Response: {
    "document_id": "uuid",
    "file_name": "pitch_deck.pdf",
    "upload_status": "processing",
    "file_size": 2048576
}

# Generate Investment Memo
POST /api/v1/memos/generate
{
    "company_id": "uuid",
    "version": "1.0",
    "include_external_data": true
}
Response: {
    "memo_id": "uuid",
    "status": "generating",
    "estimated_completion": "2024-01-20T11:00:00Z"
}
```

## 4. Agent Architecture

### 4.1 Agent Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Agent Orchestration Flow                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Stage 1: Document Processing & Summarization                       │
│  ─────────────────────────────────────────────────────────         │
│                                                                     │
│  Pitch Materials Upload                                            │
│  (PPT/Keynote/Audio/Video/PDF)                                     │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────┐                     │
│  │        Summarize Agent                   │                     │
│  ├─────────────────────────────────────────┤                     │
│  │ Sub-agents:                             │                     │
│  │ • Video/Audio Extractor                 │                     │
│  │ • PPT/Keynote Parser                    │                     │
│  │ • PDF/Doc Processor                     │                     │
│  │ • Content Aggregator                    │                     │
│  └─────────────────────────────────────────┘                     │
│       │                                                            │
│       ▼ Summary                                                    │
│       │                                                            │
│       + Company Details                                            │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────┐                     │
│  │    Combine Sources Agent                 │                     │
│  ├─────────────────────────────────────────┤                     │
│  │ • Merge extracted summaries             │                     │
│  │ • Combine with company details          │                     │
│  │ • Standardize format                    │                     │
│  │ • Generate BasicInfo structure          │                     │
│  └─────────────────────────────────────────┘                     │
│       │                                                            │
│       ▼ BasicInfo                                                  │
│                                                                     │
│  Stage 2: Multi-Dimensional Analysis                               │
│  ─────────────────────────────────────────────────────────         │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────┐                     │
│  │        Analysis Agent                    │                     │
│  ├─────────────────────────────────────────┤                     │
│  │ Sub-agents (parallel execution):        │                     │
│  │ • Founder Profile Analyzer              │                     │
│  │ • Market Data Extractor                 │                     │
│  │ • Competition Analyzer                  │                     │
│  │ • Industry Trend Analyzer               │                     │
│  │ • Financial Metrics Extractor           │                     │
│  │ • Team Assessment Agent                 │                     │
│  └─────────────────────────────────────────┘                     │
│       │                                                            │
│       ▼ Multi-Analysis Outputs                                     │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────┐                     │
│  │    Combine Analysis Agent                │                     │
│  ├─────────────────────────────────────────┤                     │
│  │ • Aggregate all analysis outputs        │                     │
│  │ • Extract founder profiles              │                     │
│  │ • Compile market data analysis          │                     │
│  │ • Synthesize competition info           │                     │
│  │ • Generate InvestmentMemo v1.0          │                     │
│  └─────────────────────────────────────────┘                     │
│       │                                                            │
│       ▼ InvestmentMemo v1.0                                        │
│                                                                     │
│  Stage 3: Questionnaire Generation                                 │
│  ─────────────────────────────────────────────────────────         │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────┐                     │
│  │      Questionnaire Agent                 │                     │
│  ├─────────────────────────────────────────┤                     │
│  │ • Analyze InvestmentMemo gaps           │                     │
│  │ • Generate industry-specific questions  │                     │
│  │ • Prioritize by relevance              │                     │
│  │ • Format for UI display                │                     │
│  └─────────────────────────────────────────┘                     │
│       │                                                            │
│       ▼ Questions                                                  │
│       │                                                            │
│       + InvestmentMemo v1.0                                        │
│       │                                                            │
│  Stage 4: Interview & Transcript Processing                        │
│  ─────────────────────────────────────────────────────────         │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────┐                     │
│  │         Call Agent                       │                     │
│  ├─────────────────────────────────────────┤                     │
│  │ • Conduct AI interview                  │                     │
│  │ • Ask generated questions               │                     │
│  │ • Follow-up on responses                │                     │
│  │ • Record and transcribe                 │                     │
│  │ • Generate CallTranscript               │                     │
│  └─────────────────────────────────────────┘                     │
│       │                                                            │
│       ▼ CallTranscript                                             │
│       │                                                            │
│       + InvestmentMemo v1.0                                        │
│       │                                                            │
│  Stage 5: Final Investment Memo Generation                         │
│  ─────────────────────────────────────────────────────────         │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────┐                     │
│  │    Investment Memo Agent v2.0            │                     │
│  ├─────────────────────────────────────────┤                     │
│  │ • Integrate call transcript insights    │                     │
│  │ • Update all sections with new info     │                     │
│  │ • Refine risk assessment               │                     │
│  │ • Enhance recommendations              │                     │
│  │ • Generate final InvestmentMemo v2.0   │                     │
│  └─────────────────────────────────────────┘                     │
│       │                                                            │
│       ▼ InvestmentMemo v2.0 (Final)                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Structures

```python
# Core Data Structures

class BasicInfo:
    """Base information extracted from pitch materials and company details"""
    company_name: str
    founder_profile: Optional[FounderProfile]
    industry: str
    sub_industry: Optional[str]
    stage: str
    founded_date: Optional[date]
    headquarters_location: str
    team_size: int
    website_url: Optional[str]
    description: str
    pitch_summary: str
    key_highlights: List[str]
    
class FounderProfile:
    """Detailed founder information"""
    name: str
    role: str
    email: str
    phone: Optional[str]
    linkedin_url: Optional[str]
    previous_experience: List[Experience]
    education: List[Education]
    achievements: List[str]
    
class MarketDataAnalysis:
    """Market analysis results"""
    tam: float  # Total Addressable Market
    sam: float  # Serviceable Addressable Market
    som: float  # Serviceable Obtainable Market
    growth_rate: float
    market_trends: List[str]
    market_drivers: List[str]
    market_challenges: List[str]
    
class CompetitionInfo:
    """Competition analysis"""
    direct_competitors: List[Competitor]
    indirect_competitors: List[Competitor]
    competitive_advantages: List[str]
    market_position: str
    differentiation_factors: List[str]
    
class KPIs:
    """Key Performance Indicators"""
    revenue: Optional[float]
    mrr: Optional[float]  # Monthly Recurring Revenue
    arr: Optional[float]  # Annual Recurring Revenue
    growth_rate: Optional[float]
    cagr: Optional[float]  # Compound Annual Growth Rate
    burn_rate: Optional[float]
    runway_months: Optional[int]
    customer_count: Optional[int]
    employee_count: int
    churn_rate: Optional[float]
    ltv: Optional[float]  # Lifetime Value
    cac: Optional[float]  # Customer Acquisition Cost
    
class InvestmentMemo(BasicInfo):
    """Complete investment memo extending BasicInfo"""
    # Inherited from BasicInfo
    # Additional fields:
    founder_profiles: List[FounderProfile]
    market_data_analysis: MarketDataAnalysis
    competition_info: CompetitionInfo
    usp: str  # Unique Selling Proposition
    kpis: KPIs
    financial_projections: FinancialProjections
    business_model: BusinessModel
    go_to_market_strategy: str
    product_analysis: ProductAnalysis
    team_analysis: TeamAnalysis
    risk_assessment: RiskAssessment
    investment_terms: InvestmentTerms
    ai_insights: AIInsights
    memo_version: str  # "1.0" or "2.0"
    
class Question:
    """Individual question for questionnaire"""
    id: str
    text: str
    question_type: str  # "multiple_choice", "short_answer", "numerical"
    options: Optional[List[str]]  # For multiple choice
    validation_rules: Optional[Dict]
    importance: str  # "critical", "high", "medium", "low"
    category: str  # "financial", "market", "team", etc.
    
class CallTranscript:
    """Interview call transcript"""
    interview_id: str
    company_id: str
    duration_minutes: int
    conducted_at: datetime
    participants: List[str]
    qa_pairs: List[QAPair]
    summary: str
    key_insights: List[str]
    
class QAPair:
    """Question-Answer pair from interview"""
    question: str
    answer: str
    timestamp: float  # Seconds from start
    follow_up_questions: Optional[List[str]]
    sentiment: Optional[str]  # "positive", "neutral", "negative"
    confidence_score: float
```

### 4.3 Agent Communication Protocol

```python
# Agent Message Format
{
    "agent_id": "summarize_agent_001",
    "task_id": "task_uuid",
    "company_id": "company_uuid",
    "action": "process_documents",
    "payload": {
        "documents": ["doc_id_1", "doc_id_2"],
        "options": {
            "include_transcription": true,
            "extract_financials": true
        }
    },
    "priority": "high",
    "timeout": 300,
    "callback_url": "https://api.liora.com/webhooks/agent-complete"
}

# Agent Response Format
{
    "task_id": "task_uuid",
    "agent_id": "summarize_agent_001",
    "status": "completed",
    "result": {
        "summary": {...},
        "extracted_data": {...},
        "confidence_scores": {...},
        "processing_time": 45.2
    },
    "errors": [],
    "metadata": {
        "model_version": "1.2.0",
        "timestamp": "2024-01-20T10:30:00Z"
    }
}
```

## 5. File Processing Pipeline

### 5.1 Upload and Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     File Processing Pipeline                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Client Upload                                                      │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │
│  │   Validate  │────▶│  Virus Scan │────▶│  Store in   │        │
│  │  File Type  │     │             │     │     S3      │        │
│  └─────────────┘     └─────────────┘     └─────────────┘        │
│       │                                           │                │
│       ▼                                           ▼                │
│  ┌─────────────┐                        ┌─────────────┐          │
│  │   Update    │                        │   Queue     │          │
│  │   Database  │                        │  Processing │          │
│  └─────────────┘                        └─────────────┘          │
│                                                │                   │
│                                                ▼                   │
│                                    ┌─────────────────────┐        │
│                                    │   Process Based on   │        │
│                                    │     File Type        │        │
│                                    └─────────────────────┘        │
│                                                │                   │
│                  ┌─────────────────────────────┼──────────────┐   │
│                  ▼                             ▼              ▼   │
│         ┌──────────────┐           ┌──────────────┐  ┌──────────┐│
│         │ PDF Extract  │           │Video/Audio   │  │ Image    ││
│         │    (PyPDF2)  │           │ Transcribe   │  │  Process ││
│         └──────────────┘           └──────────────┘  └──────────┘│
│                  │                             │              │   │
│                  └─────────────────────────────┼──────────────┘   │
│                                                ▼                   │
│                                    ┌─────────────────────┐        │
│                                    │   Store Processed   │        │
│                                    │       Content       │        │
│                                    └─────────────────────┘        │
│                                                │                   │
│                                                ▼                   │
│                                    ┌─────────────────────┐        │
│                                    │  Trigger Agent      │        │
│                                    │     Pipeline        │        │
│                                    └─────────────────────┘        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 6. Real-time Interview System

### 6.1 Interview Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Real-time Interview System                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐                                   ┌──────────┐      │
│  │ Founder  │◀─────── WebRTC Connection ───────▶│   AI     │      │
│  │ Browser  │                                   │  Agent   │      │
│  └──────────┘                                   └──────────┘      │
│       │                                              │             │
│       │                                              │             │
│       ▼                                              ▼             │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │                  Signaling Server                        │      │
│  │                  (WebSocket/FastAPI)                    │      │
│  └─────────────────────────────────────────────────────────┘      │
│       │                                              │             │
│       ▼                                              ▼             │
│  ┌──────────────┐                         ┌──────────────┐        │
│  │   Record     │                         │ Transcribe   │        │
│  │   Stream     │                         │  Real-time   │        │
│  └──────────────┘                         └──────────────┘        │
│       │                                              │             │
│       ▼                                              ▼             │
│  ┌──────────────┐                         ┌──────────────┐        │
│  │   Store      │                         │   Display    │        │
│  │  Recording   │                         │  Transcript  │        │
│  └──────────────┘                         └──────────────┘        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Interview State Machine

```
   ┌─────────┐
   │  IDLE   │
   └────┬────┘
        │ Schedule
        ▼
   ┌─────────┐
   │SCHEDULED│
   └────┬────┘
        │ Start
        ▼
   ┌─────────┐
   │  SETUP  │──────┐
   └────┬────┘      │ Technical
        │           │ Issues
        │ Ready     ▼
        ▼      ┌─────────┐
   ┌─────────┐ │ FAILED  │
   │  LIVE   │ └─────────┘
   └────┬────┘
        │ Complete
        ▼
   ┌─────────┐
   │PROCESSING│
   └────┬────┘
        │ Done
        ▼
   ┌─────────┐
   │COMPLETED│
   └─────────┘
```

## 7. Security Architecture

### 7.1 Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      JWT Authentication Flow                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Client                   API Gateway              Auth Service     │
│    │                          │                         │          │
│    ├─────Login Request────────▶                         │          │
│    │                          ├──────Validate──────────▶│          │
│    │                          │                         │          │
│    │                          │◀─────JWT Token──────────┤          │
│    │◀────Token Response───────┤                         │          │
│    │                          │                         │          │
│    ├────API Request + Token──▶│                         │          │
│    │                          ├──────Verify Token──────▶│          │
│    │                          │◀─────User Context──────┤          │
│    │                          │                         │          │
│    │◀───Protected Resource────┤                         │          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Data Encryption Strategy

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Data Encryption Layers                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Transport Layer (TLS 1.3)                                         │
│  ├── HTTPS for all API communications                              │
│  ├── WSS for WebSocket connections                                 │
│  └── Certificate pinning for mobile apps                           │
│                                                                     │
│  Application Layer                                                  │
│  ├── JWT tokens with RS256 signing                                 │
│  ├── Password hashing with bcrypt (12 rounds)                      │
│  └── API key encryption for external services                      │
│                                                                     │
│  Storage Layer                                                      │
│  ├── Database: Transparent Data Encryption (TDE)                   │
│  ├── File Storage: S3 server-side encryption (SSE-S3)            │
│  └── Backups: AES-256 encryption                                   │
│                                                                     │
│  Field-Level Encryption                                            │
│  ├── PII data (SSN, bank details)                                 │
│  ├── API credentials                                               │
│  └── Sensitive business metrics                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 8. Scalability Design

### 8.1 Horizontal Scaling Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Load Balanced Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                        ┌──────────────┐                            │
│                        │Load Balancer │                            │
│                        └──────┬───────┘                            │
│                               │                                     │
│                ┌──────────────┼──────────────┐                    │
│                ▼              ▼              ▼                    │
│         ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│         │  API-1   │  │  API-2   │  │  API-3   │                │
│         └──────────┘  └──────────┘  └──────────┘                │
│                │              │              │                     │
│                └──────────────┼──────────────┘                    │
│                               ▼                                     │
│                      ┌──────────────┐                              │
│                      │  Redis Cache │                              │
│                      └──────────────┘                              │
│                               │                                     │
│                               ▼                                     │
│              ┌────────────────────────────────┐                    │
│              │   PostgreSQL (Primary)         │                    │
│              ├────────────────────────────────┤                    │
│              │   Read Replicas (1..N)         │                    │
│              └────────────────────────────────┘                    │
│                                                                     │
│  Agent Processing (Queue-Based)                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  Celery Workers                                       │         │
│  ├──────────┬──────────┬──────────┬──────────┐         │         │
│  │ Worker-1 │ Worker-2 │ Worker-3 │ Worker-N │         │         │
│  └──────────┴──────────┴──────────┴──────────┘         │         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.2 Caching Strategy

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Multi-Level Caching                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Browser Cache (L1)                                                │
│  ├── Static assets (1 year)                                        │
│  ├── API responses (varies)                                        │
│  └── Service Worker cache                                          │
│                                                                     │
│  CDN Cache (L2)                                                    │
│  ├── Static files                                                  │
│  ├── Document previews                                             │
│  └── Public company data                                           │
│                                                                     │
│  Redis Cache (L3)                                                  │
│  ├── Session data (15 min)                                         │
│  ├── User preferences (1 hour)                                     │
│  ├── Company summaries (30 min)                                    │
│  ├── Search results (5 min)                                        │
│  └── API rate limiting                                             │
│                                                                     │
│  Database Query Cache (L4)                                         │
│  ├── Prepared statements                                           │
│  ├── Query result sets                                             │
│  └── Materialized views                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 9. Monitoring and Observability

### 9.1 Monitoring Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Observability Architecture                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Metrics Collection                                                │
│  ├── Prometheus                                                    │
│  │   ├── Application metrics                                       │
│  │   ├── System metrics                                           │
│  │   └── Custom business metrics                                  │
│  └── Grafana Dashboards                                           │
│                                                                     │
│  Logging Pipeline                                                  │
│  ├── Application Logs → Fluentd → Elasticsearch → Kibana         │
│  ├── Structured logging (JSON)                                     │
│  └── Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL           │
│                                                                     │
│  Distributed Tracing                                               │
│  ├── OpenTelemetry                                                │
│  ├── Jaeger for trace visualization                               │
│  └── Trace context propagation                                    │
│                                                                     │
│  Error Tracking                                                    │
│  ├── Sentry integration                                           │
│  ├── Error grouping and alerts                                    │
│  └── Performance monitoring                                        │
│                                                                     │
│  Health Checks                                                     │
│  ├── /health/live - Liveness probe                                │
│  ├── /health/ready - Readiness probe                              │
│  └── /health/startup - Startup probe                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 10. Deployment Architecture

### 10.1 Container Orchestration

```yaml
# Docker Compose Structure (Development)
version: '3.8'
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/liora
      - REDIS_URL=redis://redis:6379
    depends_on: [db, redis]
  
  celery-worker:
    build: ./backend
    command: celery worker
    environment:
      - CELERY_BROKER_URL=redis://redis:6379
    depends_on: [redis]
  
  db:
    image: postgres:15
    volumes: ["postgres_data:/var/lib/postgresql/data"]
    environment:
      - POSTGRES_DB=liora
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
  
  redis:
    image: redis:7-alpine
    volumes: ["redis_data:/data"]
  
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
```

### 10.2 Kubernetes Architecture (Production)

```yaml
# Kubernetes Deployment Structure
apiVersion: apps/v1
kind: Deployment
metadata:
  name: liora-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: liora-api
  template:
    metadata:
      labels:
        app: liora-api
    spec:
      containers:
      - name: api
        image: liora/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: liora-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: liora-api-service
spec:
  selector:
    app: liora-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: liora-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: liora-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 11. Integration Patterns

### 11.1 External Service Integration

```
┌─────────────────────────────────────────────────────────────────────┐
│                   External Service Integration                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Market Data APIs                                                  │
│  ├── Circuit Breaker Pattern                                       │
│  ├── Retry with Exponential Backoff                               │
│  ├── Response Caching (TTL: 1 hour)                               │
│  └── Fallback to Cached Data                                      │
│                                                                     │
│  Social Media APIs                                                 │
│  ├── Rate Limiting Compliance                                      │
│  ├── Batch Processing                                              │
│  ├── Webhook for Updates                                           │
│  └── OAuth 2.0 Authentication                                      │
│                                                                     │
│  Email Service (SMTP/SendGrid)                                     │
│  ├── Template Management                                           │
│  ├── Queue-based Sending                                           │
│  ├── Delivery Tracking                                             │
│  └── Bounce Handling                                               │
│                                                                     │
│  Video Processing (FFmpeg)                                         │
│  ├── Containerized Processing                                      │
│  ├── Progress Tracking                                             │
│  ├── Multiple Format Support                                       │
│  └── Thumbnail Generation                                          │
│                                                                     │
│  Calendar Integration                                               │
│  ├── CalDAV Protocol                                               │
│  ├── Google Calendar API                                           │
│  ├── Outlook Calendar API                                          │
│  └── iCal Format Support                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 12. Data Flow Diagrams

### 12.1 Complete Founder Journey Data Flow

```
Start → Registration → Company Profile → Document Upload
           │                                   │
           ▼                                   ▼
    Email Verification                 Process Documents
           │                                   │
           ▼                                   ▼
     Profile Active                    Summarize Content
                                              │
                                              ▼
                                    Generate Questions
                                              │
                                              ▼
                                    Founder Answers
                                              │
                                              ▼
                                    Generate Memo v1.0
                                              │
                                              ▼
                                    Schedule Interview
                                              │
                                              ▼
                                    Conduct Interview
                                              │
                                              ▼
                                    Process Transcript
                                              │
                                              ▼
                                    Generate Memo v2.0
                                              │
                                              ▼
                                    Publish to Investors
```

### 12.2 Investor Discovery Flow

```
Login → Set Preferences → Browse Companies → View Details
           │                     │                │
           ▼                     ▼                ▼
    Save Preferences      Apply Filters    Read Memo
           │                     │                │
           ▼                     ▼                ▼
    Get Recommendations    Sort Results    Schedule Meeting
                                │                │
                                ▼                ▼
                          Select Company   Send Request
                                │                │
                                ▼                ▼
                           View Details    Await Confirmation
```

## 13. Technology Stack Summary

### 13.1 Backend Technologies
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **ORM**: SQLModel
- **Cache**: Redis 7+
- **Queue**: Celery 5.3+
- **AI Framework**: Google ADK
- **Authentication**: JWT (PyJWT)
- **File Storage**: S3-compatible (MinIO/AWS S3)

### 13.2 Infrastructure
- **Container**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions / GitLab CI
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **Tracing**: Jaeger
- **Error Tracking**: Sentry

### 13.3 Development Tools
- **API Docs**: OpenAPI/Swagger
- **Testing**: Pytest
- **Linting**: Ruff
- **Type Checking**: MyPy
- **Pre-commit**: pre-commit hooks
- **Database Migrations**: Alembic

## 14. Performance Optimization Strategies

### 14.1 Database Optimization
- Proper indexing on frequently queried columns
- Materialized views for complex queries
- Connection pooling
- Query optimization and EXPLAIN analysis
- Partitioning for large tables

### 14.2 Application Optimization
- Async/await for I/O operations
- Connection pooling for external services
- Lazy loading of relationships
- Pagination for large datasets
- Background task processing

### 14.3 Caching Strategy
- Redis for session and application cache
- CDN for static assets
- Browser caching headers
- Database query result caching
- API response caching

## 15. Disaster Recovery Plan

### 15.1 Backup Strategy
- **Database**: Daily automated backups, 30-day retention
- **Files**: S3 versioning and cross-region replication
- **Code**: Git repository with multiple remotes
- **Configuration**: Encrypted secrets in vault

### 15.2 Recovery Procedures
- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Failover**: Automated with health checks
- **Rollback**: Blue-green deployment strategy

This design document provides a comprehensive technical blueprint for implementing the Liora platform, covering all major architectural decisions, system components, and integration patterns necessary for successful development and deployment.

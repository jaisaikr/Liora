"""Data models for Liora agents based on design.md specifications."""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CompanyStage(str, Enum):
    """Company funding stages."""
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"


class Experience(BaseModel):
    """Professional experience details."""
    company: str
    role: str
    duration: str
    description: Optional[str] = None
    achievements: Optional[List[str]] = None


class Education(BaseModel):
    """Educational background details."""
    institution: str
    degree: str
    field: str
    graduation_year: Optional[int] = None


class FounderProfile(BaseModel):
    """Detailed founder information."""
    name: str
    role: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    previous_experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class MarketDataAnalysis(BaseModel):
    """Market analysis results."""
    tam: Optional[float] = Field(None, description="Total Addressable Market")
    sam: Optional[float] = Field(None, description="Serviceable Addressable Market")
    som: Optional[float] = Field(None, description="Serviceable Obtainable Market")
    growth_rate: Optional[float] = None
    market_trends: List[str] = Field(default_factory=list)
    market_drivers: List[str] = Field(default_factory=list)
    market_challenges: List[str] = Field(default_factory=list)


class Competitor(BaseModel):
    """Competitor information."""
    name: str
    description: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    market_share: Optional[float] = None


class CompetitionInfo(BaseModel):
    """Competition analysis."""
    direct_competitors: List[Competitor] = Field(default_factory=list)
    indirect_competitors: List[Competitor] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    market_position: Optional[str] = None
    differentiation_factors: List[str] = Field(default_factory=list)


class KPIs(BaseModel):
    """Key Performance Indicators."""
    revenue: Optional[float] = None
    mrr: Optional[float] = Field(None, description="Monthly Recurring Revenue")
    arr: Optional[float] = Field(None, description="Annual Recurring Revenue")
    growth_rate: Optional[float] = None
    cagr: Optional[float] = Field(None, description="Compound Annual Growth Rate")
    burn_rate: Optional[float] = None
    runway_months: Optional[int] = None
    customer_count: Optional[int] = None
    employee_count: Optional[int] = None
    churn_rate: Optional[float] = None
    ltv: Optional[float] = Field(None, description="Lifetime Value")
    cac: Optional[float] = Field(None, description="Customer Acquisition Cost")


class BasicInfo(BaseModel):
    """Base information extracted from pitch materials and company details."""
    company_name: str
    founder_profile: Optional[FounderProfile] = None
    industry: str
    sub_industry: Optional[str] = None
    stage: CompanyStage
    founded_date: Optional[date] = None
    headquarters_location: str
    team_size: int
    website_url: Optional[str] = None
    description: str
    pitch_summary: str
    key_highlights: List[str] = Field(default_factory=list)


class FinancialProjections(BaseModel):
    """Financial projections and forecasts."""
    revenue_projections: Dict[str, float] = Field(default_factory=dict)
    expense_projections: Dict[str, float] = Field(default_factory=dict)
    profitability_timeline: Optional[str] = None
    key_assumptions: List[str] = Field(default_factory=list)


class BusinessModel(BaseModel):
    """Business model details."""
    revenue_streams: List[str] = Field(default_factory=list)
    pricing_strategy: Optional[str] = None
    unit_economics: Dict[str, Any] = Field(default_factory=dict)
    customer_segments: List[str] = Field(default_factory=list)


class ProductAnalysis(BaseModel):
    """Product/Technology analysis."""
    core_features: List[str] = Field(default_factory=list)
    technical_architecture: Optional[str] = None
    ip_patents: List[str] = Field(default_factory=list)
    product_roadmap: List[str] = Field(default_factory=list)


class TeamAnalysis(BaseModel):
    """Team composition and strength analysis."""
    founders: List[FounderProfile] = Field(default_factory=list)
    key_hires: List[Dict[str, str]] = Field(default_factory=list)
    advisory_board: List[Dict[str, str]] = Field(default_factory=list)
    team_strengths: List[str] = Field(default_factory=list)
    team_gaps: List[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    """Risk analysis and mitigation strategies."""
    market_risks: List[str] = Field(default_factory=list)
    technology_risks: List[str] = Field(default_factory=list)
    regulatory_risks: List[str] = Field(default_factory=list)
    financial_risks: List[str] = Field(default_factory=list)
    mitigation_strategies: Dict[str, str] = Field(default_factory=dict)


class InvestmentTerms(BaseModel):
    """Investment terms and requirements."""
    amount_seeking: float
    valuation_expectations: Optional[float] = None
    use_of_funds: List[str] = Field(default_factory=list)
    investment_type: Optional[str] = None
    board_seats: Optional[int] = None


class AIInsights(BaseModel):
    """AI-generated insights and recommendations."""
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    investment_score: Optional[float] = None
    confidence_level: Optional[float] = None


class InvestmentMemo(BasicInfo):
    """Complete investment memo extending BasicInfo."""
    # Inherited from BasicInfo, adding additional fields
    founder_profiles: List[FounderProfile] = Field(default_factory=list)
    market_data_analysis: Optional[MarketDataAnalysis] = None
    competition_info: Optional[CompetitionInfo] = None
    usp: Optional[str] = Field(None, description="Unique Selling Proposition")
    kpis: Optional[KPIs] = None
    financial_projections: Optional[FinancialProjections] = None
    business_model: Optional[BusinessModel] = None
    go_to_market_strategy: Optional[str] = None
    product_analysis: Optional[ProductAnalysis] = None
    team_analysis: Optional[TeamAnalysis] = None
    risk_assessment: Optional[RiskAssessment] = None
    investment_terms: Optional[InvestmentTerms] = None
    ai_insights: Optional[AIInsights] = None
    memo_version: str = Field(default="1.0", description="Version: 1.0 or 2.0")


class QuestionType(str, Enum):
    """Types of questions in questionnaire."""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    NUMERICAL = "numerical"


class QuestionImportance(str, Enum):
    """Importance levels for questions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Question(BaseModel):
    """Individual question for questionnaire."""
    id: str
    text: str
    question_type: QuestionType
    options: Optional[List[str]] = None  # For multiple choice
    validation_rules: Optional[Dict[str, Any]] = None
    importance: QuestionImportance
    category: str  # "financial", "market", "team", etc.


class QAPair(BaseModel):
    """Question-Answer pair from interview."""
    question: str
    answer: str
    timestamp: Optional[float] = Field(None, description="Seconds from start")
    follow_up_questions: Optional[List[str]] = None
    sentiment: Optional[str] = None  # "positive", "neutral", "negative"
    confidence_score: Optional[float] = None


class CallTranscript(BaseModel):
    """Interview call transcript."""
    interview_id: str
    company_id: str
    duration_minutes: int
    conducted_at: datetime
    participants: List[str]
    qa_pairs: List[QAPair] = Field(default_factory=list)
    summary: str
    key_insights: List[str] = Field(default_factory=list)


# Agent Communication Models
class AgentMessage(BaseModel):
    """Message format for agent communication."""
    agent_id: str
    task_id: str
    company_id: str
    action: str
    payload: Dict[str, Any]
    priority: str = "normal"
    timeout: int = 300
    callback_url: Optional[str] = None


class AgentResponse(BaseModel):
    """Response format from agents."""
    task_id: str
    agent_id: str
    status: str  # "completed", "failed", "in_progress"
    result: Dict[str, Any]
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
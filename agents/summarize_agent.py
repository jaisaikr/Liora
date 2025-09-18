"""
Liora Summarize Agent - Main orchestration for document summarization and analysis.
This agent processes pitch materials and extracts structured information for investment analysis.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

# Google ADK imports
import google.auth
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.tools import FunctionTool

# Local imports
from models import (
    BasicInfo, FounderProfile, MarketDataAnalysis, 
    CompetitionInfo, KPIs, InvestmentMemo, CompanyStage
)
from document_processor import DocumentProcessor, ContentCombiner, ProcessedDocument

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Google Cloud credentials
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id or "liora-project")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


# ============================================================================
# SUB-AGENT TOOLS - Document Processing
# ============================================================================

def extract_pdf_content(file_path: str) -> Dict[str, Any]:
    """
    Extract content from PDF documents.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing extracted content and metadata
    """
    try:
        processor = DocumentProcessor()
        result = processor.process_document(file_path)
        
        if result.error:
            return {"status": "error", "message": result.error}
        
        return {
            "status": "success",
            "content": result.content,
            "metadata": result.metadata,
            "pages": result.pages,
            "word_count": result.word_count
        }
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return {"status": "error", "message": str(e)}


def extract_presentation_content(file_path: str) -> Dict[str, Any]:
    """
    Extract content from PowerPoint/Keynote presentations.
    
    Args:
        file_path: Path to the presentation file
        
    Returns:
        Dictionary containing extracted content and metadata
    """
    try:
        processor = DocumentProcessor()
        result = processor.process_document(file_path)
        
        if result.error:
            return {"status": "error", "message": result.error}
        
        return {
            "status": "success",
            "content": result.content,
            "metadata": result.metadata,
            "slides": result.pages,
            "word_count": result.word_count
        }
    except Exception as e:
        logger.error(f"Error processing presentation: {str(e)}")
        return {"status": "error", "message": str(e)}


def extract_document_content(file_path: str) -> Dict[str, Any]:
    """
    Extract content from Word documents.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Dictionary containing extracted content and metadata
    """
    try:
        processor = DocumentProcessor()
        result = processor.process_document(file_path)
        
        if result.error:
            return {"status": "error", "message": result.error}
        
        return {
            "status": "success",
            "content": result.content,
            "metadata": result.metadata,
            "word_count": result.word_count
        }
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# SUB-AGENTS DEFINITIONS
# ============================================================================

# Video/Audio Extractor Sub-agent
video_audio_extractor = Agent(
    name="video_audio_extractor",
    model="gemini-2.5-flash",
    instruction="""You are a specialist in extracting and transcribing content from video and audio materials.
    Your task is to:
    1. Transcribe spoken content accurately
    2. Identify key speakers and their roles
    3. Extract main talking points and presentations
    4. Note any visual elements or demonstrations mentioned
    5. Summarize the core message and value propositions
    
    Output a structured summary of the media content.""",
    description="Extracts and transcribes content from video/audio pitch materials",
    output_key="video_audio_summary"
)

# PPT/Keynote Parser Sub-agent
presentation_parser = Agent(
    name="presentation_parser",
    model="gemini-2.5-flash",
    instruction="""You are an expert at analyzing pitch deck presentations.
    Extract the following information from the presentation content:
    1. Company name and tagline
    2. Problem statement and solution
    3. Market opportunity and size
    4. Business model and revenue streams
    5. Product features and differentiation
    6. Team information and backgrounds
    7. Financial projections and metrics
    8. Funding ask and use of funds
    9. Competitive landscape
    10. Go-to-market strategy
    
    Structure your output as a comprehensive summary with clear sections.""",
    description="Parses and analyzes PowerPoint/Keynote presentations",
    tools=[extract_presentation_content],
    output_key="presentation_summary"
)

# PDF/Doc Processor Sub-agent
document_parser = Agent(
    name="document_parser",
    model="gemini-2.5-flash",
    instruction="""You are a document analysis expert specializing in business documents.
    Extract and analyze:
    1. Executive summary or overview
    2. Business description and value proposition
    3. Market analysis and opportunity
    4. Financial information and projections
    5. Team and organizational structure
    6. Product/service details
    7. Growth strategy and milestones
    8. Risk factors and mitigation
    9. Investment terms if mentioned
    10. Any supporting data or evidence
    
    Provide a structured analysis of the document content.""",
    description="Processes PDF and Word documents for key information",
    tools=[extract_pdf_content, extract_document_content],
    output_key="document_summary"
)

# Content Aggregator Sub-agent
content_aggregator = Agent(
    name="content_aggregator",
    model="gemini-2.5-pro",
    instruction="""You are responsible for combining and synthesizing information from multiple sources.
    Your tasks:
    1. Combine summaries from video_audio_summary, presentation_summary, and document_summary
    2. Identify and reconcile any conflicting information
    3. Fill in gaps by cross-referencing different sources
    4. Create a unified, coherent narrative
    5. Highlight the most important findings
    6. Flag any missing critical information
    
    Produce a comprehensive, well-structured summary that captures all essential information
    about the company and investment opportunity.""",
    description="Aggregates and synthesizes content from all document processors",
    output_key="aggregated_content"
)

# Combine Sources Agent
combine_sources_agent = Agent(
    name="combine_sources_agent",
    model="gemini-2.5-pro",
    instruction="""You are responsible for creating a standardized BasicInfo structure from aggregated content.
    
    Using the aggregated_content and company registration details, create a comprehensive BasicInfo object that includes:
    1. Company name and basic details
    2. Founder profile information
    3. Industry and sub-industry classification
    4. Company stage and founding information
    5. Location and team size
    6. Website and contact information
    7. Company description and pitch summary
    8. Key highlights and achievements
    
    Ensure all information is accurate, consistent, and properly formatted.
    Output should be a valid JSON structure matching the BasicInfo schema.""",
    description="Combines all sources into standardized BasicInfo format",
    output_key="basic_info"
)

# ============================================================================
# MAIN SUMMARIZE AGENT ORCHESTRATION
# ============================================================================

# Main Summarize Agent using Sequential processing
summarize_agent = SequentialAgent(
    name="summarize_agent",
    description="Main agent that orchestrates document processing and summarization",
    sub_agents=[
        # Stage 1: Parallel document processing
        ParallelAgent(
            name="parallel_document_processors",
            description="Process all document types in parallel",
            sub_agents=[
                video_audio_extractor,
                presentation_parser,
                document_parser
            ]
        ),
        # Stage 2: Aggregate all content
        content_aggregator,
        # Stage 3: Create standardized output
        combine_sources_agent
    ]
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def process_pitch_materials(
    company_name: str,
    document_paths: List[str],
    company_details: Optional[Dict[str, Any]] = None
) -> BasicInfo:
    """
    Process pitch materials and company details to generate BasicInfo.
    
    Args:
        company_name: Name of the company
        document_paths: List of paths to pitch materials
        company_details: Optional company registration details
        
    Returns:
        BasicInfo object with extracted information
    """
    # Process documents
    documents = []
    for path in document_paths:
        if Path(path).exists():
            doc = DocumentProcessor.process_document(path)
            documents.append(doc)
    
    # Combine documents
    combined_content = ContentCombiner.combine_documents(documents)
    
    # Add company details if provided
    if company_details:
        combined_content['company_details'] = company_details
    
    # TODO: Run through summarize_agent to get BasicInfo
    # This would involve setting up the agent runner and session
    
    # For now, return a mock BasicInfo
    return BasicInfo(
        company_name=company_name,
        industry="Technology",
        stage=CompanyStage.SEED,
        headquarters_location="San Francisco, CA",
        team_size=10,
        description="AI-powered platform",
        pitch_summary="Revolutionary AI solution for enterprise",
        key_highlights=["Fast growth", "Strong team", "Large market"]
    )


# ============================================================================
# ROOT AGENT DEFINITION (for ADK discovery)
# ============================================================================

root_agent = summarize_agent

if __name__ == "__main__":
    # Example usage
    logger.info("Liora Summarize Agent initialized")
    logger.info(f"Sub-agents: {[agent.name for agent in summarize_agent.sub_agents]}")
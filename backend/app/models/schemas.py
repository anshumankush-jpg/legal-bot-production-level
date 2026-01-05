"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class IngestTextRequest(BaseModel):
    """Request schema for text ingestion."""
    text: str = Field(..., description="Text content to ingest")
    source_name: str = Field(..., description="Name/identifier for the source")
    tags: Optional[List[str]] = Field(default=[], description="Optional tags")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class IngestTextResponse(BaseModel):
    """Response schema for text ingestion."""
    doc_id: str
    chunks: int
    source_name: str


class IngestFileResponse(BaseModel):
    """Response schema for file ingestion."""
    doc_id: str
    chunks: int
    source_name: str
    file_type: str


class IngestImageResponse(BaseModel):
    """Response schema for image ingestion."""
    doc_id: str
    chunks: int
    source_name: str
    extracted_text_preview: str = Field(..., description="First 200 chars of extracted text")


class QueryRequest(BaseModel):
    """Request schema for query/answer."""
    question: str = Field(..., description="User's question")
    top_k: Optional[int] = Field(default=None, description="Number of chunks to retrieve")
    language: Optional[str] = Field(default="en", description="Language code (en, fr, es, hi, pa, zh)")
    country: Optional[str] = Field(default=None, description="Country code (CA, US)")
    province: Optional[str] = Field(default=None, description="Province/State name")
    offense_type: Optional[str] = Field(default=None, description="Type of offense (speeding, dui, distracted, etc.)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context about the user's situation")


class SourceInfo(BaseModel):
    """Information about a retrieved source."""
    doc_id: Optional[str]
    chunk_id: Optional[str]
    source_name: Optional[str]
    source_type: Optional[str]
    score: float
    snippet: str


class QueryResponse(BaseModel):
    """Response schema for query/answer."""
    answer: str
    sources: List[SourceInfo]


class LegalCitation(BaseModel):
    """Citation information for legal sources."""
    doc_id: str
    law_name: str = ""
    section: str = ""
    citation: str
    jurisdiction: str = ""
    country: str = ""
    page: int = 0
    source_path: str = ""
    relevance_score: float = 0.0


class LegalChatRequest(BaseModel):
    """Request schema for legal chat."""
    question: str = Field(..., description="User's legal question")
    country: Optional[str] = Field(default=None, description="Country (Canada, USA)")
    jurisdiction: Optional[str] = Field(default=None, description="Specific jurisdiction (Ontario, California, etc.)")
    max_results: Optional[int] = Field(default=8, description="Maximum number of document chunks to retrieve")


class LegalChatResponse(BaseModel):
    """Response schema for legal chat."""
    answer: str
    citations: List[LegalCitation]
    jurisdiction: Optional[str] = None
    country: Optional[str] = None
    chunks_used: int = 0


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    index_size: int
    index_dimension: int


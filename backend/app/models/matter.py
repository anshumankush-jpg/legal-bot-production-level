"""Matter/Case data models."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MatterType(str, Enum):
    """Types of legal matters."""
    TRAFFIC_TICKET = "traffic_ticket"
    PARKING_TICKET = "parking_ticket"
    SMALL_CLAIM = "small_claim"
    BYLAW_FINE = "bylaw_fine"
    REGULATORY_FINE = "regulatory_fine"
    OTHER = "other"


class MatterStatus(str, Enum):
    """Status of a matter."""
    NEW = "new"
    PARSED = "parsed"
    REVIEWING = "reviewing"
    OPTIONS_EXPLAINED = "options_explained"
    WAITING_FOR_DISCLOSURE = "waiting_for_disclosure"
    DOCUMENTS_GENERATED = "documents_generated"
    REMINDER_SET = "reminder_set"
    COURT_SCHEDULED = "court_scheduled"
    CLOSED = "closed"


class Matter(BaseModel):
    """Legal matter/case model."""
    matter_id: str = Field(..., description="Unique matter identifier")
    user_id: Optional[str] = Field(None, description="User identifier (or session_id)")
    session_id: Optional[str] = Field(None, description="Session identifier for anonymous users")
    jurisdiction: Dict[str, str] = Field(..., description="Jurisdiction: {country, region, region_code}")
    matter_type: MatterType = Field(..., description="Type of matter")
    status: MatterStatus = Field(default=MatterStatus.NEW, description="Current status")
    raw_documents: List[str] = Field(default=[], description="List of document IDs ingested")
    structured_data: Dict[str, Any] = Field(default={}, description="Parsed ticket/summons fields")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    class Config:
        use_enum_values = True


class CreateMatterRequest(BaseModel):
    """Request to create a new matter."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    jurisdiction: Dict[str, str]
    matter_type: MatterType
    structured_data: Optional[Dict[str, Any]] = None


class UpdateMatterRequest(BaseModel):
    """Request to update a matter."""
    status: Optional[MatterStatus] = None
    structured_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MatterResponse(BaseModel):
    """Response model for matter."""
    matter_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    jurisdiction: Dict[str, str]
    matter_type: str
    status: str
    raw_documents: List[str]
    structured_data: Dict[str, Any]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


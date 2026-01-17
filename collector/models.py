"""Data models for court/ticket lookup dataset."""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
import hashlib


class Portal(BaseModel):
    """Represents a single court/ticket portal."""
    name: str
    url: str
    authority: str  # e.g., City of Toronto, Ontario Court of Justice
    portal_type: Literal["case_lookup", "pay_ticket", "request_trial", "court_directory"]
    requires: List[str] = Field(default_factory=list)  # ["ticket_number", "offence_number", "name", "dob", "plate"]
    notes: str = ""


class JurisdictionRecord(BaseModel):
    """Complete record for a jurisdiction's court/ticket portals."""
    id: str
    country: Literal["Canada", "USA"]
    province_state: str
    city_or_county: str
    jurisdiction_level: Literal["city", "county", "province_state", "state", "federal"]
    ticket_types: List[str] = Field(default_factory=list)  # ["traffic", "parking", "bylaw", "criminal", "municipal"]
    portals: List[Portal] = Field(default_factory=list)
    language: List[str] = Field(default_factory=lambda: ["en"])
    last_verified_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    verification_status: Literal["verified", "unverified", "broken"] = "unverified"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    
    @classmethod
    def generate_id(cls, country: str, province_state: str, city_or_county: str, ticket_type: str = "") -> str:
        """Generate a stable hash ID for a record."""
        key = f"{country}:{province_state}:{city_or_county}:{ticket_type}".lower()
        return hashlib.sha256(key.encode()).hexdigest()[:16]


class SeedSource(BaseModel):
    """Seed source for a province/state."""
    region_name: str
    region_code: str  # e.g., "ON", "TX"
    country: Literal["Canada", "USA"]
    official_directory_urls: List[str] = Field(default_factory=list)
    search_patterns: List[str] = Field(default_factory=list)
    top_cities: List[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    """Result of portal verification."""
    url: str
    status_code: Optional[int] = None
    is_official: bool = False  # .gov, .ca, official court domain
    title: str = ""
    has_keywords: bool = False
    is_blocked: bool = False  # captcha, 403, etc.
    verification_status: Literal["verified", "unverified", "broken"] = "unverified"
    confidence: float = 0.0
    notes: str = ""

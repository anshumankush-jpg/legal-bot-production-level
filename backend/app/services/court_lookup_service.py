"""Court and ticket lookup service for LEGID.

Integrates with the court/ticket portal dataset to provide
jurisdiction-specific portal information.
"""
import logging
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Import the collector's lookup API
try:
    import sys
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from collector.lookup_api import JurisdictionLookup
    from collector.normalizers import normalize_city, normalize_province_state
    COLLECTOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Court lookup collector not available: {e}")
    COLLECTOR_AVAILABLE = False
    JurisdictionLookup = None
    normalize_city = lambda x: x.strip().title()
    normalize_province_state = lambda x, c: x.strip().title()


class CourtLookupService:
    """Service for looking up court and ticket portals."""
    
    def __init__(self):
        """Initialize the court lookup service."""
        self.lookup_api: Optional[JurisdictionLookup] = None
        self._initialized = False
        
        if COLLECTOR_AVAILABLE:
            self._initialize()
    
    def _initialize(self):
        """Initialize the lookup API."""
        try:
            dataset_path = Path(__file__).parent.parent.parent.parent / "collector" / "output" / "all.json"
            if not dataset_path.exists():
                logger.warning(f"Court lookup dataset not found: {dataset_path}")
                logger.info("Run: python -m collector.cli collect all")
                return
            
            self.lookup_api = JurisdictionLookup(dataset_path)
            self._initialized = True
            logger.info("Court lookup service initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize court lookup service: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if the service is available."""
        return self._initialized and self.lookup_api is not None
    
    def lookup(
        self,
        city: Optional[str] = None,
        province_state: Optional[str] = None,
        country: Optional[str] = None,
        ticket_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lookup court portals by jurisdiction.
        
        Args:
            city: City name
            province_state: Province or state name
            country: "Canada" or "USA"
            ticket_type: Type of ticket
        
        Returns:
            List of matching jurisdiction records
        """
        if not self.is_available():
            return []
        
        try:
            return self.lookup_api.lookup_jurisdiction(
                country=country,
                province_state=province_state,
                city=city,
                ticket_type=ticket_type
            )
        except Exception as e:
            logger.error(f"Error in court lookup: {e}")
            return []
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Free-text search for court portals.
        
        Args:
            query: Search query (e.g., "Toronto traffic ticket")
        
        Returns:
            List of matching records
        """
        if not self.is_available():
            return []
        
        try:
            return self.lookup_api.search(query)
        except Exception as e:
            logger.error(f"Error in court search: {e}")
            return []
    
    def extract_jurisdiction_from_text(self, text: str) -> Dict[str, Optional[str]]:
        """Extract jurisdiction information from text (e.g., OCR output).
        
        Args:
            text: Text to analyze (e.g., ticket OCR text)
        
        Returns:
            Dict with country, province_state, city fields
        """
        result = {
            "country": None,
            "province_state": None,
            "city": None
        }
        
        text_lower = text.lower()
        
        # Detect country
        if any(word in text_lower for word in ["canada", "canadian", "ontario", "quebec", "british columbia", "alberta"]):
            result["country"] = "Canada"
        elif any(word in text_lower for word in ["usa", "united states", "california", "texas", "new york", "florida"]):
            result["country"] = "USA"
        
        # Common Canadian provinces
        province_patterns = {
            "Ontario": [r"\bontario\b", r"\b(on)\b", r"\bont\b"],
            "Quebec": [r"\bquebec\b", r"\bquébec\b", r"\b(qc)\b"],
            "British Columbia": [r"\bbritish columbia\b", r"\b(bc)\b", r"\bb\.c\.\b"],
            "Alberta": [r"\balberta\b", r"\b(ab)\b", r"\balb\b"],
            "Manitoba": [r"\bmanitoba\b", r"\b(mb)\b"],
            "Saskatchewan": [r"\bsaskatchewan\b", r"\b(sk)\b"],
            "Nova Scotia": [r"\bnova scotia\b", r"\b(ns)\b"],
            "New Brunswick": [r"\bnew brunswick\b", r"\b(nb)\b"],
            "Newfoundland and Labrador": [r"\bnewfoundland\b", r"\b(nl)\b"],
            "Prince Edward Island": [r"\bprince edward island\b", r"\b(pe)\b", r"\bpei\b"]
        }
        
        # Common US states
        state_patterns = {
            "California": [r"\bcalifornia\b", r"\b(ca)\b", r"\bcalif\b"],
            "Texas": [r"\btexas\b", r"\b(tx)\b"],
            "New York": [r"\bnew york\b", r"\b(ny)\b"],
            "Florida": [r"\bflorida\b", r"\b(fl)\b"],
            "Illinois": [r"\billinois\b", r"\b(il)\b"]
        }
        
        # Try to match province/state
        patterns = province_patterns if result["country"] == "Canada" else state_patterns
        for name, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, text_lower):
                    result["province_state"] = name
                    break
            if result["province_state"]:
                break
        
        # Common cities
        city_patterns = [
            "Toronto", "Vancouver", "Montreal", "Ottawa", "Calgary", "Edmonton",
            "Winnipeg", "Quebec City", "Hamilton", "Kitchener", "London",
            "Victoria", "Halifax", "Oshawa", "Windsor", "Saskatoon",
            # USA cities
            "Los Angeles", "San Francisco", "San Diego", "New York", "Chicago",
            "Houston", "Dallas", "Austin", "Miami", "Orlando", "Seattle",
            "Boston", "Philadelphia", "Phoenix", "Denver"
        ]
        
        for city in city_patterns:
            if city.lower() in text_lower:
                result["city"] = city
                break
        
        return result
    
    def extract_ticket_info(self, text: str) -> Dict[str, Any]:
        """Extract ticket information from text (OCR output).
        
        Args:
            text: OCR text from ticket
        
        Returns:
            Dict with extracted information
        """
        info = {
            "ticket_number": None,
            "offence_number": None,
            "citation_number": None,
            "date": None,
            "jurisdiction": self.extract_jurisdiction_from_text(text)
        }
        
        # Extract ticket/citation numbers
        # Common patterns: 
        # - Ticket #: 123456789
        # - Citation No: ABC123456
        # - Offence #: 1234567890
        
        ticket_patterns = [
            r"ticket\s*#?\s*:?\s*([A-Z0-9]{6,})",
            r"citation\s*#?\s*:?\s*([A-Z0-9]{6,})",
            r"ticket\s*number\s*:?\s*([A-Z0-9]{6,})",
            r"citation\s*number\s*:?\s*([A-Z0-9]{6,})"
        ]
        
        for pattern in ticket_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                number = match.group(1)
                info["ticket_number"] = number
                info["citation_number"] = number
                break
        
        # Extract offence number (Ontario-specific)
        offence_patterns = [
            r"offence\s*#?\s*:?\s*([A-Z0-9]{6,})",
            r"offence\s*number\s*:?\s*([A-Z0-9]{6,})"
        ]
        
        for pattern in offence_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["offence_number"] = match.group(1)
                break
        
        # Extract date
        date_patterns = [
            r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
            r"(\w{3,}\s+\d{1,2},?\s+\d{4})"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                info["date"] = match.group(1)
                break
        
        return info
    
    def format_lookup_response(
        self,
        ticket_info: Dict[str, Any],
        jurisdictions: List[Dict[str, Any]]
    ) -> str:
        """Format a response with ticket lookup information.
        
        Args:
            ticket_info: Extracted ticket information
            jurisdictions: Matching jurisdiction records
        
        Returns:
            Formatted response text
        """
        response_parts = []
        
        # Add ticket info summary
        jur = ticket_info.get("jurisdiction", {})
        if jur.get("city") or jur.get("province_state"):
            location = []
            if jur.get("city"):
                location.append(jur["city"])
            if jur.get("province_state"):
                location.append(jur["province_state"])
            if jur.get("country"):
                location.append(jur["country"])
            
            response_parts.append(f"**Detected Location:** {', '.join(location)}")
        
        if ticket_info.get("ticket_number"):
            response_parts.append(f"**Ticket Number:** {ticket_info['ticket_number']}")
        
        if ticket_info.get("date"):
            response_parts.append(f"**Date:** {ticket_info['date']}")
        
        # Add portal information
        if jurisdictions:
            response_parts.append("\n**📍 Case Lookup Portals:**\n")
            
            for i, record in enumerate(jurisdictions[:3], 1):  # Show top 3
                response_parts.append(f"{i}. **{record['city_or_county']}, {record['province_state']}**")
                
                for portal in record['portals']:
                    icon = {
                        "case_lookup": "🔍",
                        "pay_ticket": "💳",
                        "request_trial": "⚖️",
                        "court_directory": "📋"
                    }.get(portal['portal_type'], "🔗")
                    
                    response_parts.append(f"   {icon} [{portal['name']}]({portal['url']})")
                    
                    if portal.get('requires'):
                        response_parts.append(f"      *Requires: {', '.join(portal['requires'])}*")
                    
                    if portal.get('notes'):
                        response_parts.append(f"      *{portal['notes']}*")
                
                response_parts.append("")  # Blank line
        
        else:
            response_parts.append("\n*No specific court lookup portals found for this jurisdiction.*")
            response_parts.append("I recommend contacting the local municipal court or provincial/state court directly.")
        
        return "\n".join(response_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dataset statistics.
        
        Returns:
            Statistics dict
        """
        if not self.is_available():
            return {"error": "Service not available"}
        
        try:
            return self.lookup_api.get_stats()
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}


# Singleton instance
_court_lookup_service: Optional[CourtLookupService] = None


def get_court_lookup_service() -> CourtLookupService:
    """Get or create the court lookup service singleton."""
    global _court_lookup_service
    if _court_lookup_service is None:
        _court_lookup_service = CourtLookupService()
    return _court_lookup_service

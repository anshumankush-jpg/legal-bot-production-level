"""Lookup API for finding jurisdiction portals."""
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from .models import JurisdictionRecord, Portal
from .normalizers import normalize_city, normalize_province_state
from .config import OUTPUT_DIR

logger = logging.getLogger(__name__)


class JurisdictionLookup:
    """API for looking up court/ticket portals by jurisdiction."""
    
    def __init__(self, dataset_path: Optional[Path] = None):
        """Initialize lookup API.
        
        Args:
            dataset_path: Path to combined dataset JSON file.
                         If None, uses default output/all.json
        """
        if dataset_path is None:
            dataset_path = OUTPUT_DIR / "all.json"
        
        self.dataset_path = dataset_path
        self.records: List[JurisdictionRecord] = []
        self._index: Dict[str, List[JurisdictionRecord]] = {}
        
        self.load_dataset()
    
    def load_dataset(self):
        """Load dataset from JSON file."""
        if not self.dataset_path.exists():
            logger.warning(f"Dataset not found: {self.dataset_path}")
            logger.info("Run collector CLI to generate dataset first")
            return
        
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.records = [JurisdictionRecord(**record) for record in data]
            
            # Build search index
            self._build_index()
            
            logger.info(f"Loaded {len(self.records)} jurisdiction records")
        
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            self.records = []
    
    def _build_index(self):
        """Build search index for faster lookups."""
        self._index = {}
        
        for record in self.records:
            # Index by city
            city_key = record.city_or_county.lower()
            if city_key not in self._index:
                self._index[city_key] = []
            self._index[city_key].append(record)
            
            # Index by province/state + city
            region_city_key = f"{record.province_state.lower()}:{city_key}"
            if region_city_key not in self._index:
                self._index[region_city_key] = []
            self._index[region_city_key].append(record)
            
            # Index by country + province/state + city
            full_key = f"{record.country.lower()}:{region_city_key}"
            if full_key not in self._index:
                self._index[full_key] = []
            self._index[full_key].append(record)
    
    def lookup_jurisdiction(
        self,
        country: Optional[str] = None,
        province_state: Optional[str] = None,
        city: Optional[str] = None,
        ticket_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lookup jurisdiction portals.
        
        Args:
            country: "Canada" or "USA"
            province_state: Province or state name
            city: City or county name
            ticket_type: Type of ticket (traffic, parking, etc.)
        
        Returns:
            List of matching records with portals, sorted by confidence
        """
        if not self.records:
            return []
        
        # Normalize inputs
        if city:
            city = normalize_city(city)
        if province_state and country:
            province_state = normalize_province_state(province_state, country)
        
        # Build search key
        results = []
        
        if city and province_state and country:
            # Most specific search
            key = f"{country.lower()}:{province_state.lower()}:{city.lower()}"
            results = self._index.get(key, [])
        
        elif city and province_state:
            # Search by province/state + city
            key = f"{province_state.lower()}:{city.lower()}"
            results = self._index.get(key, [])
        
        elif city:
            # Search by city only (may return multiple matches)
            key = city.lower()
            results = self._index.get(key, [])
        
        elif province_state and country:
            # Search for province/state-wide portals
            results = [
                r for r in self.records
                if r.country.lower() == country.lower()
                and r.province_state.lower() == province_state.lower()
                and r.jurisdiction_level in ["province_state", "state"]
            ]
        
        else:
            # Too vague, return empty
            return []
        
        # Filter by ticket type if specified
        if ticket_type:
            results = [
                r for r in results
                if ticket_type.lower() in [t.lower() for t in r.ticket_types]
            ]
        
        # Sort by confidence (highest first)
        results = sorted(results, key=lambda r: r.confidence, reverse=True)
        
        # Convert to dicts for JSON serialization
        return [self._format_result(r) for r in results]
    
    def _format_result(self, record: JurisdictionRecord) -> Dict[str, Any]:
        """Format a record for API response."""
        return {
            "id": record.id,
            "country": record.country,
            "province_state": record.province_state,
            "city_or_county": record.city_or_county,
            "jurisdiction_level": record.jurisdiction_level,
            "ticket_types": record.ticket_types,
            "portals": [
                {
                    "name": p.name,
                    "url": p.url,
                    "authority": p.authority,
                    "portal_type": p.portal_type,
                    "requires": p.requires,
                    "notes": p.notes
                }
                for p in record.portals
            ],
            "language": record.language,
            "verification_status": record.verification_status,
            "confidence": record.confidence,
            "last_verified_at": record.last_verified_at
        }
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Free-text search across all records.
        
        Args:
            query: Search query (e.g., "Toronto traffic ticket")
        
        Returns:
            List of matching records
        """
        query_lower = query.lower()
        results = []
        
        for record in self.records:
            score = 0.0
            
            # Match city
            if record.city_or_county.lower() in query_lower:
                score += 0.5
            
            # Match province/state
            if record.province_state.lower() in query_lower:
                score += 0.3
            
            # Match ticket types
            for ticket_type in record.ticket_types:
                if ticket_type.lower() in query_lower:
                    score += 0.2
                    break
            
            # Match portal names
            for portal in record.portals:
                if any(word in query_lower for word in portal.name.lower().split()):
                    score += 0.1
                    break
            
            if score > 0:
                results.append((score * record.confidence, record))
        
        # Sort by score
        results = sorted(results, key=lambda x: x[0], reverse=True)
        
        return [self._format_result(r[1]) for r in results[:20]]  # Top 20
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        if not self.records:
            return {
                "total_records": 0,
                "verified": 0,
                "unverified": 0,
                "broken": 0
            }
        
        return {
            "total_records": len(self.records),
            "by_country": {
                "Canada": len([r for r in self.records if r.country == "Canada"]),
                "USA": len([r for r in self.records if r.country == "USA"])
            },
            "by_verification": {
                "verified": len([r for r in self.records if r.verification_status == "verified"]),
                "unverified": len([r for r in self.records if r.verification_status == "unverified"]),
                "broken": len([r for r in self.records if r.verification_status == "broken"])
            },
            "average_confidence": sum(r.confidence for r in self.records) / len(self.records)
        }


# Singleton instance
_lookup_instance: Optional[JurisdictionLookup] = None


def get_lookup_api(dataset_path: Optional[Path] = None) -> JurisdictionLookup:
    """Get or create the lookup API singleton."""
    global _lookup_instance
    if _lookup_instance is None:
        _lookup_instance = JurisdictionLookup(dataset_path)
    return _lookup_instance


def lookup_jurisdiction(**kwargs) -> List[Dict[str, Any]]:
    """Convenience function for jurisdiction lookup."""
    api = get_lookup_api()
    return api.lookup_jurisdiction(**kwargs)

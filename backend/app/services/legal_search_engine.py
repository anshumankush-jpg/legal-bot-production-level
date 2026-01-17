"""Legal search engine service for LEGID.

Provides semantic search across:
- Legal documents
- Court lookup dataset
- Case law
- Statutes and regulations
"""
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LegalSearchEngine:
    """Search engine for legal information and court lookups."""
    
    def __init__(self):
        """Initialize the search engine."""
        self.dataset_chunks: List[Dict[str, Any]] = []
        self._initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize and chunk the court lookup dataset."""
        try:
            # Load court lookup dataset
            dataset_path = Path(__file__).parent.parent.parent.parent / "collector" / "output" / "all.json"
            
            if dataset_path.exists():
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                
                # Create searchable chunks from the dataset
                self.dataset_chunks = self._create_chunks(records)
                logger.info(f"Legal search engine initialized with {len(self.dataset_chunks)} chunks")
                self._initialized = True
            else:
                logger.warning("Court lookup dataset not found")
        
        except Exception as e:
            logger.error(f"Failed to initialize legal search engine: {e}")
    
    def _create_chunks(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create searchable text chunks from court lookup records.
        
        Each chunk contains:
        - Searchable text
        - Metadata (country, province_state, city, portals)
        - Source type
        """
        chunks = []
        
        for record in records:
            # Create a chunk for each jurisdiction
            chunk_text_parts = []
            
            # Add location information
            chunk_text_parts.append(f"Location: {record['city_or_county']}, {record['province_state']}, {record['country']}")
            
            # Add ticket types
            if record.get('ticket_types'):
                chunk_text_parts.append(f"Ticket Types: {', '.join(record['ticket_types'])}")
            
            # Add portal information
            for portal in record.get('portals', []):
                chunk_text_parts.append(f"\nPortal: {portal['name']}")
                chunk_text_parts.append(f"Authority: {portal['authority']}")
                chunk_text_parts.append(f"Type: {portal['portal_type']}")
                chunk_text_parts.append(f"URL: {portal['url']}")
                
                if portal.get('requires'):
                    chunk_text_parts.append(f"Requirements: {', '.join(portal['requires'])}")
                
                if portal.get('notes'):
                    chunk_text_parts.append(f"Notes: {portal['notes']}")
            
            chunk = {
                "text": "\n".join(chunk_text_parts),
                "metadata": {
                    "source_type": "court_lookup",
                    "country": record['country'],
                    "province_state": record['province_state'],
                    "city_or_county": record['city_or_county'],
                    "jurisdiction_level": record['jurisdiction_level'],
                    "ticket_types": record.get('ticket_types', []),
                    "verification_status": record.get('verification_status', 'unverified'),
                    "confidence": record.get('confidence', 0.5)
                },
                "portals": record.get('portals', []),
                "record_id": record.get('id')
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search across legal information.
        
        Args:
            query: Search query
            filters: Optional filters (country, province_state, city, ticket_type)
            top_k: Number of results to return
        
        Returns:
            List of matching chunks
        """
        if not self._initialized or not self.dataset_chunks:
            return []
        
        query_lower = query.lower()
        results = []
        
        for chunk in self.dataset_chunks:
            # Calculate relevance score
            score = 0.0
            
            # Text match
            if query_lower in chunk['text'].lower():
                score += 1.0
            
            # Word matches
            query_words = query_lower.split()
            chunk_text_lower = chunk['text'].lower()
            
            for word in query_words:
                if len(word) > 3 and word in chunk_text_lower:
                    score += 0.2
            
            # Metadata matches
            metadata = chunk['metadata']
            
            if filters:
                # Apply filters
                if filters.get('country') and metadata['country'].lower() != filters['country'].lower():
                    continue
                if filters.get('province_state') and metadata['province_state'].lower() != filters['province_state'].lower():
                    continue
                if filters.get('city') and filters['city'].lower() not in metadata['city_or_county'].lower():
                    continue
                if filters.get('ticket_type'):
                    if not any(filters['ticket_type'].lower() in t.lower() for t in metadata['ticket_types']):
                        continue
            
            # Boost verified results
            if metadata.get('verification_status') == 'verified':
                score *= 1.5
            
            # Apply confidence weighting
            score *= metadata.get('confidence', 0.5)
            
            if score > 0:
                results.append({
                    "score": score,
                    "chunk": chunk
                })
        
        # Sort by score
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        return [r['chunk'] for r in results[:top_k]]
    
    def search_by_location(
        self,
        city: Optional[str] = None,
        province_state: Optional[str] = None,
        country: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search by location.
        
        Args:
            city: City name
            province_state: Province or state
            country: Country
        
        Returns:
            Matching chunks
        """
        filters = {}
        if city:
            filters['city'] = city
        if province_state:
            filters['province_state'] = province_state
        if country:
            filters['country'] = country
        
        query = " ".join(filter(None, [city, province_state, country]))
        
        return self.search(query, filters=filters)
    
    def get_all_locations(self) -> Dict[str, List[str]]:
        """Get all available locations in the dataset.
        
        Returns:
            Dict with countries, provinces/states, cities
        """
        if not self._initialized:
            return {}
        
        locations = {
            "countries": set(),
            "provinces_states": {},
            "cities": {}
        }
        
        for chunk in self.dataset_chunks:
            metadata = chunk['metadata']
            country = metadata['country']
            province_state = metadata['province_state']
            city = metadata['city_or_county']
            
            locations["countries"].add(country)
            
            if country not in locations["provinces_states"]:
                locations["provinces_states"][country] = set()
            locations["provinces_states"][country].add(province_state)
            
            if province_state not in locations["cities"]:
                locations["cities"][province_state] = set()
            locations["cities"][province_state].add(city)
        
        # Convert sets to sorted lists
        return {
            "countries": sorted(list(locations["countries"])),
            "provinces_states": {
                k: sorted(list(v)) for k, v in locations["provinces_states"].items()
            },
            "cities": {
                k: sorted(list(v)) for k, v in locations["cities"].items()
            }
        }
    
    def is_available(self) -> bool:
        """Check if the search engine is available."""
        return self._initialized and len(self.dataset_chunks) > 0


# Singleton instance
_search_engine: Optional[LegalSearchEngine] = None


def get_legal_search_engine() -> LegalSearchEngine:
    """Get or create the legal search engine singleton."""
    global _search_engine
    if _search_engine is None:
        _search_engine = LegalSearchEngine()
    return _search_engine

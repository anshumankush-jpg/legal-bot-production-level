"""
Legal Retrieval Module - Specialized retrieval for legal documents.

Provides legal-specific search capabilities with jurisdiction-aware filtering
and metadata extraction for RAG-based legal Q&A.
"""

import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from dataclasses import dataclass

from app.embeddings.embedding_service import get_embedding_service
from app.vector_store.faiss_store import get_vector_store
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """Structured representation of a retrieved legal document chunk."""
    text: str
    law_name: str = ""
    section: str = ""
    citation: str = ""
    source_path: str = ""
    jurisdiction: str = ""
    country: str = ""
    score: float = 0.0
    page: int = 0
    doc_id: str = ""


class LegalRetrievalService:
    """
    Specialized retrieval service for legal documents.

    Provides jurisdiction-aware search with legal metadata extraction.
    """

    def __init__(self):
        """Initialize the legal retrieval service."""
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store(dim=settings.EMBEDDING_DIMENSIONS)
        logger.info("Legal retrieval service initialized")

    def load_legal_index(self) -> bool:
        """
        Load the legal index and verify it's ready for search.

        Returns:
            True if index is loaded and ready, False otherwise
        """
        try:
            stats = self.vector_store.get_stats()
            if stats['total_vectors'] > 0:
                logger.info(f"Legal index loaded: {stats['total_vectors']} vectors, {stats['dimension']} dimensions")
                return True
            else:
                logger.warning("Legal index is empty - no documents have been indexed yet")
                return False
        except Exception as e:
            logger.error(f"Failed to load legal index: {e}")
            return False

    def embed_query(self, query: str) -> np.ndarray:
        """
        Convert query to embedding using the same model as document indexing.

        Args:
            query: User's legal question

        Returns:
            numpy array with query embedding
        """
        try:
            # Use the same embedding service and model as documents
            embedding = self.embedding_service.embed_text(query)
            logger.debug(f"Query embedded with shape: {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"Failed to embed query '{query}': {e}")
            raise

    def _extract_legal_metadata(self, doc: Dict) -> Dict[str, str]:
        """
        Extract legal-specific metadata from document.

        Args:
            doc: Document dict from vector store

        Returns:
            Dict with legal metadata fields
        """
        metadata = {
            'law_name': '',
            'section': '',
            'jurisdiction': doc.get('organization', ''),
            'country': '',
            'source_path': doc.get('source_name', ''),
            'page': doc.get('page', 0),
            'doc_id': doc.get('id', '')
        }

        # Determine country from jurisdiction
        jurisdiction = metadata['jurisdiction'].lower()
        if jurisdiction in ['canada', 'ontario', 'british_columbia', 'quebec', 'alberta',
                           'nova_scotia', 'new_brunswick', 'manitoba', 'saskatchewan',
                           'prince_edward_island', 'newfoundland', 'northwest_territories',
                           'nunavut', 'yukon']:
            metadata['country'] = 'Canada'
        elif jurisdiction in ['usa', 'united_states', 'california', 'texas', 'florida',
                             'new_york', 'pennsylvania', 'illinois', 'ohio', 'georgia',
                             'north_carolina', 'new_jersey', 'virginia', 'washington',
                             'arizona', 'massachusetts', 'tennessee', 'indiana', 'missouri',
                             'maryland', 'wisconsin', 'colorado', 'minnesota', 'south_carolina',
                             'alabama', 'louisiana', 'kentucky', 'oregon', 'oklahoma', 'connecticut',
                             'utah', 'iowa', 'nevada', 'arkansas', 'mississippi', 'kansas',
                             'new_mexico', 'nebraska', 'west_virginia', 'idaho', 'hawaii',
                             'new_hampshire', 'maine', 'montana', 'rhode_island', 'delaware',
                             'south_dakota', 'north_dakota', 'alaska', 'vermont', 'wyoming']:
            metadata['country'] = 'USA'

        # Extract law name and section from filename or content
        source_name = metadata['source_path'].lower()

        # Common legal document patterns
        if 'highway' in source_name or 'traffic' in source_name:
            metadata['law_name'] = 'Highway Traffic Act' if 'canada' in jurisdiction else 'Traffic Code'
        elif 'criminal' in source_name:
            metadata['law_name'] = 'Criminal Code' if 'canada' in jurisdiction else 'Criminal Code'

        # Extract section numbers from content (simple pattern matching)
        text = doc.get('content', '')
        import re

        # Look for section patterns
        section_patterns = [
            r'section\s+(\d+)',
            r'article\s+(\d+)',
            r'§\s*(\d+)',
            r's\.?\s*(\d+)'
        ]

        for pattern in section_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata['section'] = match.group(1)
                break

        return metadata

    def _build_citation(self, metadata: Dict) -> str:
        """
        Build a proper legal citation string.

        Args:
            metadata: Legal metadata dict

        Returns:
            Formatted citation string
        """
        parts = []

        if metadata.get('law_name'):
            parts.append(metadata['law_name'])

        if metadata.get('section'):
            parts.append(f"Section {metadata['section']}")

        if metadata.get('jurisdiction'):
            parts.append(metadata['jurisdiction'])

        if metadata.get('country'):
            parts.append(metadata['country'])

        if metadata.get('page', 0) > 0:
            parts.append(f"Page {metadata['page']}")

        return ", ".join(parts) if parts else metadata.get('source_path', 'Unknown Source')

    def search_legal_index(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict[str, str]] = None
    ) -> List[RetrievedChunk]:
        """
        Search the legal index with jurisdiction-aware filtering.

        Args:
            query: Legal question to search for
            k: Number of results to return
            filters: Optional filters like {'country': 'Canada', 'jurisdiction': 'Ontario'}

        Returns:
            List of RetrievedChunk objects with legal metadata
        """
        try:
            # Step 1: Embed the query
            query_embedding = self.embed_query(query)

            # Step 2: Search the vector store
            search_results = self.vector_store.search(
                query_vector=query_embedding[0].tolist(),
                top_k=k * 2,  # Get more results for filtering
                search_text=None,  # FAISS doesn't use text search
                filters=None  # FAISS doesn't support complex filters
            )

            if not search_results:
                logger.info(f"No results found for query: {query}")
                return []

            # Step 3: Apply filters and convert to RetrievedChunk objects
            filtered_chunks = []

            for score, doc in search_results:
                # Extract legal metadata
                legal_metadata = self._extract_legal_metadata(doc)

                # Apply filters if specified
                if filters:
                    skip = False
                    for filter_key, filter_value in filters.items():
                        if filter_key.lower() == 'country' and legal_metadata.get('country', '').lower() != filter_value.lower():
                            skip = True
                            break
                        elif filter_key.lower() == 'jurisdiction' and legal_metadata.get('jurisdiction', '').lower() != filter_value.lower():
                            skip = True
                            break
                    if skip:
                        continue

                # Build citation
                citation = self._build_citation(legal_metadata)

                # Create RetrievedChunk
                chunk = RetrievedChunk(
                    text=doc.get('content', ''),
                    law_name=legal_metadata.get('law_name', ''),
                    section=legal_metadata.get('section', ''),
                    citation=citation,
                    source_path=legal_metadata.get('source_path', ''),
                    jurisdiction=legal_metadata.get('jurisdiction', ''),
                    country=legal_metadata.get('country', ''),
                    score=score,
                    page=legal_metadata.get('page', 0),
                    doc_id=legal_metadata.get('doc_id', '')
                )

                filtered_chunks.append(chunk)

                # Limit to k results after filtering
                if len(filtered_chunks) >= k:
                    break

            logger.info(f"Legal search returned {len(filtered_chunks)} filtered results for query: {query}")
            return filtered_chunks

        except Exception as e:
            logger.error(f"Error during legal search for query '{query}': {e}")
            return []


# Global singleton instance
_legal_retrieval_service: Optional[LegalRetrievalService] = None


def get_legal_retrieval_service() -> LegalRetrievalService:
    """Get or create the global legal retrieval service instance."""
    global _legal_retrieval_service
    if _legal_retrieval_service is None:
        _legal_retrieval_service = LegalRetrievalService()
    return _legal_retrieval_service


def initialize_legal_index() -> bool:
    """
    Initialize and verify the legal index is ready.

    Returns:
        True if index is ready, False otherwise
    """
    service = get_legal_retrieval_service()
    return service.load_legal_index()
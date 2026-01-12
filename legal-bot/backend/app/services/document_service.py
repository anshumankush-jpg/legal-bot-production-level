"""Document management service for organizing and tracking documents."""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for managing document metadata and organization."""
    
    def __init__(self):
        """Initialize document service."""
        self.documents_file = Path(settings.DOC_STORE_PATH) / "documents.json"
        self.documents_file.parent.mkdir(parents=True, exist_ok=True)
        self.documents: Dict[str, Dict] = {}
        self._load_documents()
    
    def _load_documents(self):
        """Load documents from storage."""
        if self.documents_file.exists():
            try:
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                logger.info(f"Loaded {len(self.documents)} documents from storage")
            except Exception as e:
                logger.error(f"Error loading documents: {e}")
                self.documents = {}
        else:
            logger.info("No existing documents file, starting fresh")
    
    def _save_documents(self):
        """Save documents to storage."""
        try:
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.documents)} documents to storage")
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
            raise
    
    def register_document(
        self,
        doc_id: str,
        source_name: str,
        source_type: str,
        organization: Optional[str] = None,
        subject: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """Register a new document."""
        self.documents[doc_id] = {
            'doc_id': doc_id,
            'source_name': source_name,
            'source_type': source_type,
            'organization': organization,
            'subject': subject,
            'tags': tags or [],
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'chunk_count': 0,
            'status': 'indexed'
        }
        self._save_documents()
        logger.info(f"Registered document: {doc_id}")
    
    def update_document(self, doc_id: str, **updates):
        """Update document metadata."""
        if doc_id in self.documents:
            self.documents[doc_id].update(updates)
            self.documents[doc_id]['updated_at'] = datetime.utcnow().isoformat()
            self._save_documents()
            logger.info(f"Updated document: {doc_id}")
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document by ID."""
        return self.documents.get(doc_id)
    
    def list_documents(
        self,
        organization: Optional[str] = None,
        subject: Optional[str] = None,
        source_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """List documents with optional filters."""
        results = list(self.documents.values())
        
        if organization:
            results = [d for d in results if d.get('organization') == organization]
        if subject:
            results = [d for d in results if d.get('subject') == subject]
        if source_type:
            results = [d for d in results if d.get('source_type') == source_type]
        if tags:
            results = [d for d in results if any(tag in d.get('tags', []) for tag in tags)]
        
        # Sort by updated_at descending
        results.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return results
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document metadata."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save_documents()
            logger.info(f"Deleted document: {doc_id}")
            return True
        return False


# Global singleton instance
_document_service: Optional[DocumentService] = None


def get_document_service() -> DocumentService:
    """Get or create the global document service instance."""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service


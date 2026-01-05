"""Service for managing legal matters/cases."""
import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from app.models.matter import Matter, MatterStatus, MatterType, CreateMatterRequest, UpdateMatterRequest
from app.core.config import settings

logger = logging.getLogger(__name__)


class MatterService:
    """Service for managing matters with GCP-friendly storage."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize matter service.
        
        Args:
            storage_path: Path to store matters (JSON file or directory)
                        For GCP, this could be Cloud Storage or Firestore
        """
        self.storage_path = Path(storage_path or f"{settings.DOC_STORE_PATH}/matters.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.matters: Dict[str, Matter] = {}
        self._load_matters()
    
    def _load_matters(self):
        """Load matters from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for matter_id, matter_data in data.items():
                        # Convert datetime strings back to datetime
                        matter_data['created_at'] = datetime.fromisoformat(matter_data['created_at'])
                        matter_data['updated_at'] = datetime.fromisoformat(matter_data['updated_at'])
                        self.matters[matter_id] = Matter(**matter_data)
                logger.info(f"Loaded {len(self.matters)} matters from storage")
            except Exception as e:
                logger.error(f"Error loading matters: {e}")
                self.matters = {}
        else:
            logger.info("No existing matters file, starting fresh")
    
    def _save_matters(self):
        """Save matters to storage."""
        try:
            # Convert to JSON-serializable format
            data = {}
            for matter_id, matter in self.matters.items():
                matter_dict = matter.dict()
                matter_dict['created_at'] = matter.created_at.isoformat()
                matter_dict['updated_at'] = matter.updated_at.isoformat()
                data[matter_id] = matter_dict
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.matters)} matters to storage")
        except Exception as e:
            logger.error(f"Error saving matters: {e}")
            raise
    
    def create_matter(self, request: CreateMatterRequest) -> Matter:
        """
        Create a new matter.
        
        Args:
            request: Matter creation request
            
        Returns:
            Created matter
        """
        matter_id = str(uuid.uuid4())
        
        matter = Matter(
            matter_id=matter_id,
            user_id=request.user_id,
            session_id=request.session_id,
            jurisdiction=request.jurisdiction,
            matter_type=request.matter_type,
            status=MatterStatus.NEW,
            structured_data=request.structured_data or {},
            raw_documents=[],
            metadata={}
        )
        
        self.matters[matter_id] = matter
        self._save_matters()
        
        logger.info(f"Created matter {matter_id} of type {request.matter_type}")
        return matter
    
    def get_matter(self, matter_id: str) -> Optional[Matter]:
        """Get matter by ID."""
        return self.matters.get(matter_id)
    
    def update_matter(self, matter_id: str, request: UpdateMatterRequest) -> Optional[Matter]:
        """
        Update a matter.
        
        Args:
            matter_id: Matter ID
            request: Update request
            
        Returns:
            Updated matter or None if not found
        """
        matter = self.matters.get(matter_id)
        if not matter:
            return None
        
        if request.status:
            matter.status = request.status
        if request.structured_data:
            matter.structured_data.update(request.structured_data)
        if request.metadata:
            matter.metadata.update(request.metadata)
        
        matter.updated_at = datetime.utcnow()
        self._save_matters()
        
        logger.info(f"Updated matter {matter_id}")
        return matter
    
    def add_document(self, matter_id: str, document_id: str) -> bool:
        """Add a document ID to a matter."""
        matter = self.matters.get(matter_id)
        if not matter:
            return False
        
        if document_id not in matter.raw_documents:
            matter.raw_documents.append(document_id)
            matter.updated_at = datetime.utcnow()
            self._save_matters()
        
        return True
    
    def list_matters(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        matter_type: Optional[MatterType] = None,
        status: Optional[MatterStatus] = None
    ) -> List[Matter]:
        """
        List matters with optional filters.
        
        Args:
            user_id: Filter by user ID
            session_id: Filter by session ID
            matter_type: Filter by matter type
            status: Filter by status
            
        Returns:
            List of matching matters
        """
        results = list(self.matters.values())
        
        if user_id:
            results = [m for m in results if m.user_id == user_id]
        if session_id:
            results = [m for m in results if m.session_id == session_id]
        if matter_type:
            results = [m for m in results if m.matter_type == matter_type]
        if status:
            results = [m for m in results if m.status == status]
        
        # Sort by updated_at descending
        results.sort(key=lambda x: x.updated_at, reverse=True)
        
        return results


# Global singleton instance
_matter_service: Optional[MatterService] = None


def get_matter_service() -> MatterService:
    """Get or create the global matter service instance."""
    global _matter_service
    if _matter_service is None:
        _matter_service = MatterService()
    return _matter_service


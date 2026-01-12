"""Endpoints for document management."""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.services.document_service import get_document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("")
async def list_documents(
    organization: Optional[str] = Query(None, description="Filter by organization"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    tags: Optional[str] = Query(None, description="Comma-separated tags")
):
    """List documents with optional filters."""
    try:
        document_service = get_document_service()
        tag_list = tags.split(',') if tags else None
        documents = document_service.list_documents(
            organization=organization,
            subject=subject,
            source_type=source_type,
            tags=tag_list
        )
        return {"documents": documents, "count": len(documents)}
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Get document by ID."""
    try:
        document_service = get_document_service()
        document = document_service.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document metadata."""
    try:
        document_service = get_document_service()
        success = document_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"status": "success", "message": f"Document {doc_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


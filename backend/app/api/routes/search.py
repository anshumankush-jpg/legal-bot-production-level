"""
Search Routes for LegalAI
User-scoped search across conversations, messages, and attachments
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from datetime import datetime

from app.middleware.auth_middleware import get_current_user
from app.services.search_service import get_search_service, SearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SearchResult(BaseModel):
    """Single search result"""
    result_type: str  # 'conversation' | 'message' | 'attachment'
    conversation_id: Optional[str]
    message_id: Optional[str]
    attachment_id: Optional[str]
    title: str
    snippet: str
    created_at: datetime
    relevance_score: float = 1.0


class SearchResponse(BaseModel):
    """Search results"""
    query: str
    total_results: int
    results: List[SearchResult]
    took_ms: int


# ============================================================================
# SEARCH ROUTES
# ============================================================================

@router.get("", response_model=SearchResponse)
async def search_user_data(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search across user's conversations, messages, and attachments.
    
    SECURITY:
    - user_id from server session (NEVER from client)
    - Searches ONLY within authenticated user's data
    - Cannot access other users' conversations
    
    ChatGPT behavior:
    - User types in search bar
    - Results show matching conversations and messages
    - Clicking result navigates to conversation
    """
    start_time = datetime.utcnow()
    
    # Search with user_id scoping
    results = await search_service.search(
        query=q,
        user_id=user['user_id'],  # From session - strict scoping
        limit=limit,
        offset=offset
    )
    
    end_time = datetime.utcnow()
    took_ms = int((end_time - start_time).total_seconds() * 1000)
    
    return SearchResponse(
        query=q,
        total_results=len(results),
        results=results,
        took_ms=took_ms
    )

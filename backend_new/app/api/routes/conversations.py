"""
Conversation management API routes.
Handles CRUD operations for conversations (chats).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from app.services.auth_service import AuthService, get_current_user
from app.services.bigquery_service import BigQueryService
from app.core.config import settings

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

bq_service = BigQueryService()

# ============================================================================
# SCHEMAS
# ============================================================================

class CreateConversationRequest(BaseModel):
    title: Optional[str] = None
    law_type: Optional[str] = None
    law_category: Optional[str] = None
    jurisdiction: Optional[str] = None

class UpdateConversationRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None  # active, archived, deleted

class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: str
    title: Optional[str]
    law_type: Optional[str]
    law_category: Optional[str]
    jurisdiction: Optional[str]
    status: str
    message_count: int
    created_at: str
    updated_at: str

# ============================================================================
# ROUTES
# ============================================================================

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation (New Chat)."""
    
    conversation_id = f"conv_{uuid.uuid4().hex}"
    now = datetime.utcnow().isoformat()
    
    # Default title if not provided
    title = request.title or f"New Chat - {datetime.now().strftime('%b %d, %Y')}"
    
    conversation_data = {
        "conversation_id": conversation_id,
        "user_id": current_user['user_id'],
        "title": title,
        "law_type": request.law_type,
        "law_category": request.law_category,
        "jurisdiction": request.jurisdiction,
        "status": "active",
        "message_count": 0,
        "created_at": now,
        "updated_at": now
    }
    
    await bq_service.insert(
        f"{settings.BIGQUERY_DATASET}.conversations",
        conversation_data
    )
    
    return ConversationResponse(**conversation_data)


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, description="Number of conversations to return"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """List all conversations for current user."""
    
    # Build query
    query = f"""
    SELECT *
    FROM `{settings.BIGQUERY_DATASET}.conversations`
    WHERE user_id = @user_id
    """
    
    params = {"user_id": current_user['user_id']}
    
    if status:
        query += " AND status = @status"
        params["status"] = status
    
    query += " ORDER BY updated_at DESC LIMIT @limit OFFSET @offset"
    params["limit"] = limit
    params["offset"] = offset
    
    conversations = await bq_service.query(query, params)
    
    return [ConversationResponse(**conv) for conv in conversations]


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific conversation."""
    
    conversation = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.conversations`
        WHERE conversation_id = @conversation_id AND user_id = @user_id
        """,
        {
            "conversation_id": conversation_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationResponse(**conversation)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a conversation (title, status, etc.)."""
    
    # Verify ownership
    conversation = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.conversations`
        WHERE conversation_id = @conversation_id AND user_id = @user_id
        """,
        {
            "conversation_id": conversation_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Build update data
    update_data = {"updated_at": datetime.utcnow().isoformat()}
    
    if request.title is not None:
        update_data["title"] = request.title
    
    if request.status is not None:
        if request.status not in ["active", "archived", "deleted"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
        update_data["status"] = request.status
    
    # Update in BigQuery
    await bq_service.update(
        f"{settings.BIGQUERY_DATASET}.conversations",
        update_data,
        f"conversation_id = '{conversation_id}'"
    )
    
    # Fetch updated conversation
    updated_conversation = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.conversations`
        WHERE conversation_id = @conversation_id
        """,
        {"conversation_id": conversation_id}
    )
    
    return ConversationResponse(**updated_conversation)


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    permanent: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation (soft delete by default)."""
    
    # Verify ownership
    conversation = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.conversations`
        WHERE conversation_id = @conversation_id AND user_id = @user_id
        """,
        {
            "conversation_id": conversation_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    if permanent:
        # Hard delete: remove conversation and all messages
        await bq_service.delete(
            f"{settings.BIGQUERY_DATASET}.conversations",
            f"conversation_id = '{conversation_id}'"
        )
        
        await bq_service.delete(
            f"{settings.BIGQUERY_DATASET}.messages",
            f"conversation_id = '{conversation_id}'"
        )
        
        return {
            "success": True,
            "message": "Conversation permanently deleted",
            "conversation_id": conversation_id
        }
    else:
        # Soft delete: mark as deleted
        await bq_service.update(
            f"{settings.BIGQUERY_DATASET}.conversations",
            {
                "status": "deleted",
                "updated_at": datetime.utcnow().isoformat()
            },
            f"conversation_id = '{conversation_id}'"
        )
        
        return {
            "success": True,
            "message": "Conversation moved to trash",
            "conversation_id": conversation_id
        }


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, description="Number of messages to return"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """Get all messages in a conversation."""
    
    # Verify ownership
    conversation = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.conversations`
        WHERE conversation_id = @conversation_id AND user_id = @user_id
        """,
        {
            "conversation_id": conversation_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    messages = await bq_service.query(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.messages`
        WHERE conversation_id = @conversation_id AND deleted = FALSE
        ORDER BY created_at ASC
        LIMIT @limit OFFSET @offset
        """,
        {
            "conversation_id": conversation_id,
            "limit": limit,
            "offset": offset
        }
    )
    
    return {
        "success": True,
        "conversation_id": conversation_id,
        "messages": messages,
        "count": len(messages)
    }


@router.post("/search")
async def search_conversations(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Number of results"),
    current_user: dict = Depends(get_current_user)
):
    """Search across conversations and messages."""
    
    # Search in conversation titles and message content
    search_query = f"""
    SELECT DISTINCT c.*
    FROM `{settings.BIGQUERY_DATASET}.conversations` c
    LEFT JOIN `{settings.BIGQUERY_DATASET}.messages` m
    ON c.conversation_id = m.conversation_id
    WHERE c.user_id = @user_id
    AND c.status != 'deleted'
    AND (
        LOWER(c.title) LIKE @search_pattern
        OR LOWER(m.content) LIKE @search_pattern
    )
    ORDER BY c.updated_at DESC
    LIMIT @limit
    """
    
    search_pattern = f"%{query.lower()}%"
    
    results = await bq_service.query(
        search_query,
        {
            "user_id": current_user['user_id'],
            "search_pattern": search_pattern,
            "limit": limit
        }
    )
    
    return {
        "success": True,
        "query": query,
        "results": [ConversationResponse(**conv) for conv in results],
        "count": len(results)
    }

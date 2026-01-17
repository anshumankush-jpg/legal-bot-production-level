"""
Message management API routes.
Handles sending/receiving messages within conversations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime

from app.services.auth_service import get_current_user
from app.services.bigquery_service import BigQueryService
from app.services.llm_service import LLMService
from app.core.config import settings

router = APIRouter(prefix="/api/messages", tags=["messages"])

bq_service = BigQueryService()
llm_service = LLMService()

# ============================================================================
# SCHEMAS
# ============================================================================

class SendMessageRequest(BaseModel):
    conversation_id: str
    message: str
    law_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    created_at: str
    citations: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None

class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    conversation_updated: bool

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_conversation_context(conversation_id: str, limit: int = 10) -> List[Dict]:
    """Get recent messages from conversation for context."""
    messages = await bq_service.query(
        f"""
        SELECT role, content
        FROM `{settings.BIGQUERY_DATASET}.messages`
        WHERE conversation_id = @conversation_id
        AND deleted = FALSE
        ORDER BY created_at DESC
        LIMIT @limit
        """,
        {
            "conversation_id": conversation_id,
            "limit": limit
        }
    )
    
    # Reverse to chronological order
    return list(reversed(messages))

async def get_user_preferences(user_id: str) -> Dict:
    """Get user preferences for personalization."""
    prefs = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.user_preferences`
        WHERE user_id = @user_id
        """,
        {"user_id": user_id}
    )
    
    return prefs or {
        "response_style": "detailed",
        "language": "en"
    }

async def update_conversation_timestamp(conversation_id: str, title: Optional[str] = None):
    """Update conversation's updated_at timestamp and optionally title."""
    update_data = {"updated_at": datetime.utcnow().isoformat()}
    
    if title:
        update_data["title"] = title
    
    await bq_service.update(
        f"{settings.BIGQUERY_DATASET}.conversations",
        update_data,
        f"conversation_id = '{conversation_id}'"
    )
    
    # Increment message count
    await bq_service.execute(
        f"""
        UPDATE `{settings.BIGQUERY_DATASET}.conversations`
        SET message_count = message_count + 2
        WHERE conversation_id = '{conversation_id}'
        """
    )

def generate_conversation_title(first_message: str) -> str:
    """Generate a title from the first message."""
    # Simple implementation - take first 50 chars
    title = first_message[:50]
    if len(first_message) > 50:
        title += "..."
    return title

# ============================================================================
# ROUTES
# ============================================================================

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message and get AI response.
    This is the main chat endpoint.
    """
    
    # Verify conversation ownership
    conversation = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.conversations`
        WHERE conversation_id = @conversation_id AND user_id = @user_id
        """,
        {
            "conversation_id": request.conversation_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get user preferences for personalization
    preferences = await get_user_preferences(current_user['user_id'])
    
    # Get conversation context (last 10 messages)
    context = await get_conversation_context(request.conversation_id, limit=10)
    
    # Create user message
    user_message_id = f"msg_{uuid.uuid4().hex}"
    user_message_data = {
        "message_id": user_message_id,
        "conversation_id": request.conversation_id,
        "user_id": current_user['user_id'],
        "role": "user",
        "content": request.message,
        "created_at": datetime.utcnow().isoformat(),
        "citations": json.dumps([]),
        "metadata": json.dumps(request.metadata or {}),
        "deleted": False
    }
    
    await bq_service.insert(
        f"{settings.BIGQUERY_DATASET}.messages",
        user_message_data
    )
    
    # Generate AI response using LLM service
    llm_response = await llm_service.generate_response(
        message=request.message,
        context=context,
        user_role=current_user['role'],
        law_type=request.law_type or conversation.get('law_type'),
        jurisdiction=request.jurisdiction or conversation.get('jurisdiction'),
        response_style=preferences.get('response_style', 'detailed'),
        language=preferences.get('language', 'en')
    )
    
    # Create assistant message
    assistant_message_id = f"msg_{uuid.uuid4().hex}"
    assistant_message_data = {
        "message_id": assistant_message_id,
        "conversation_id": request.conversation_id,
        "user_id": current_user['user_id'],
        "role": "assistant",
        "content": llm_response['answer'],
        "created_at": datetime.utcnow().isoformat(),
        "citations": json.dumps(llm_response.get('citations', [])),
        "metadata": json.dumps({
            "confidence": llm_response.get('confidence', 0.8),
            "chunks_used": llm_response.get('chunks_used', 0),
            "model": llm_response.get('model', 'gpt-4')
        }),
        "deleted": False
    }
    
    await bq_service.insert(
        f"{settings.BIGQUERY_DATASET}.messages",
        assistant_message_data
    )
    
    # Update conversation timestamp
    # If this is the first message, generate a title
    if conversation.get('message_count', 0) == 0:
        title = generate_conversation_title(request.message)
        await update_conversation_timestamp(request.conversation_id, title=title)
    else:
        await update_conversation_timestamp(request.conversation_id)
    
    # Return both messages
    return ChatResponse(
        user_message=MessageResponse(
            message_id=user_message_id,
            conversation_id=request.conversation_id,
            user_id=current_user['user_id'],
            role="user",
            content=request.message,
            created_at=user_message_data['created_at'],
            citations=[],
            metadata=request.metadata
        ),
        assistant_message=MessageResponse(
            message_id=assistant_message_id,
            conversation_id=request.conversation_id,
            user_id=current_user['user_id'],
            role="assistant",
            content=llm_response['answer'],
            created_at=assistant_message_data['created_at'],
            citations=llm_response.get('citations', []),
            metadata={
                "confidence": llm_response.get('confidence', 0.8),
                "chunks_used": llm_response.get('chunks_used', 0)
            }
        ),
        conversation_updated=True
    )


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific message."""
    
    message = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.messages`
        WHERE message_id = @message_id AND user_id = @user_id AND deleted = FALSE
        """,
        {
            "message_id": message_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Parse JSON fields
    message['citations'] = json.loads(message.get('citations', '[]'))
    message['metadata'] = json.loads(message.get('metadata', '{}'))
    
    return MessageResponse(**message)


@router.patch("/{message_id}")
async def edit_message(
    message_id: str,
    content: str,
    current_user: dict = Depends(get_current_user)
):
    """Edit a user message (only user messages can be edited)."""
    
    message = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.messages`
        WHERE message_id = @message_id AND user_id = @user_id AND deleted = FALSE
        """,
        {
            "message_id": message_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if message['role'] != 'user':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only user messages can be edited"
        )
    
    # Update message
    await bq_service.update(
        f"{settings.BIGQUERY_DATASET}.messages",
        {
            "content": content,
            "edited_at": datetime.utcnow().isoformat()
        },
        f"message_id = '{message_id}'"
    )
    
    return {
        "success": True,
        "message": "Message updated",
        "message_id": message_id
    }


@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Soft delete a message."""
    
    message = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.messages`
        WHERE message_id = @message_id AND user_id = @user_id
        """,
        {
            "message_id": message_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Soft delete
    await bq_service.update(
        f"{settings.BIGQUERY_DATASET}.messages",
        {"deleted": True},
        f"message_id = '{message_id}'"
    )
    
    return {
        "success": True,
        "message": "Message deleted",
        "message_id": message_id
    }


@router.post("/{message_id}/regenerate")
async def regenerate_response(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Regenerate assistant response for a message."""
    
    # Get the original message
    message = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.messages`
        WHERE message_id = @message_id AND user_id = @user_id
        """,
        {
            "message_id": message_id,
            "user_id": current_user['user_id']
        }
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if message['role'] != 'assistant':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only regenerate assistant messages"
        )
    
    # Get the conversation
    conversation = await bq_service.query_one(
        f"""
        SELECT *
        FROM `{settings.BIGQUERY_DATASET}.conversations`
        WHERE conversation_id = @conversation_id
        """,
        {"conversation_id": message['conversation_id']}
    )
    
    # Get user preferences
    preferences = await get_user_preferences(current_user['user_id'])
    
    # Get context (messages before this one)
    context = await bq_service.query(
        f"""
        SELECT role, content
        FROM `{settings.BIGQUERY_DATASET}.messages`
        WHERE conversation_id = @conversation_id
        AND created_at < @created_at
        AND deleted = FALSE
        ORDER BY created_at ASC
        """,
        {
            "conversation_id": message['conversation_id'],
            "created_at": message['created_at']
        }
    )
    
    # Get the user message that prompted this response
    user_message = context[-1]['content'] if context else ""
    
    # Generate new response
    llm_response = await llm_service.generate_response(
        message=user_message,
        context=context[:-1] if context else [],  # Exclude the prompt message
        user_role=current_user['role'],
        law_type=conversation.get('law_type'),
        jurisdiction=conversation.get('jurisdiction'),
        response_style=preferences.get('response_style', 'detailed'),
        language=preferences.get('language', 'en')
    )
    
    # Update the message
    await bq_service.update(
        f"{settings.BIGQUERY_DATASET}.messages",
        {
            "content": llm_response['answer'],
            "citations": json.dumps(llm_response.get('citations', [])),
            "metadata": json.dumps({
                "confidence": llm_response.get('confidence', 0.8),
                "chunks_used": llm_response.get('chunks_used', 0),
                "regenerated": True,
                "regenerated_at": datetime.utcnow().isoformat()
            })
        },
        f"message_id = '{message_id}'"
    )
    
    # Return updated message
    updated_message = await bq_service.query_one(
        f"SELECT * FROM `{settings.BIGQUERY_DATASET}.messages` WHERE message_id = '{message_id}'"
    )
    
    updated_message['citations'] = json.loads(updated_message.get('citations', '[]'))
    updated_message['metadata'] = json.loads(updated_message.get('metadata', '{}'))
    
    return {
        "success": True,
        "message": MessageResponse(**updated_message)
    }

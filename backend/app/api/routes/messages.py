"""
Messages management endpoints for LEGID
Handles message CRUD and chat streaming
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.api.routes.auth_v2 import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])

# Request/Response Models
class MessageCreate(BaseModel):
    conversation_id: str
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    attachments: Optional[List[dict]] = None
    metadata: Optional[dict] = None

class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    attachments: Optional[List[dict]] = None
    metadata: Optional[dict] = None
    created_at: str

# Mock database
MOCK_MESSAGES = {}

@router.get("", response_model=List[MessageResponse])
async def list_messages(
    conversationId: str = Query(...),
    current_user: dict = Depends(get_current_user),
    limit: int = 100
):
    """Get messages for a conversation"""
    try:
        user_id = current_user['user_id']
        
        # Filter messages for this conversation
        messages = [
            msg for msg in MOCK_MESSAGES.values()
            if msg['conversation_id'] == conversationId and msg['user_id'] == user_id
        ]

        # Sort by created_at asc
        messages.sort(key=lambda x: x['created_at'])

        # Limit
        messages = messages[:limit]

        return [
            MessageResponse(
                message_id=msg['message_id'],
                conversation_id=msg['conversation_id'],
                user_id=msg['user_id'],
                role=msg['role'],
                content=msg['content'],
                attachments=msg.get('attachments'),
                metadata=msg.get('metadata'),
                created_at=msg['created_at'].isoformat()
            )
            for msg in messages
        ]

    except Exception as e:
        logger.error(f"Failed to list messages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list messages")

@router.post("", response_model=MessageResponse)
async def create_message(
    request: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new message"""
    try:
        user_id = current_user['user_id']
        
        message = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": request.conversation_id,
            "user_id": user_id,
            "role": request.role,
            "content": request.content,
            "attachments": request.attachments,
            "metadata": request.metadata,
            "created_at": datetime.now()
        }

        # Store in mock database
        MOCK_MESSAGES[message['message_id']] = message

        return MessageResponse(
            message_id=message['message_id'],
            conversation_id=message['conversation_id'],
            user_id=message['user_id'],
            role=message['role'],
            content=message['content'],
            attachments=message.get('attachments'),
            metadata=message.get('metadata'),
            created_at=message['created_at'].isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to create message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create message")

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a message"""
    try:
        msg = MOCK_MESSAGES.get(message_id)
        
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")

        # Verify ownership
        if msg['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete message
        del MOCK_MESSAGES[message_id]

        return {"success": True, "message": "Message deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete message")

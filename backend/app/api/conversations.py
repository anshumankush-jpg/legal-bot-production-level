"""Conversation and message API endpoints."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.db_models import User, Conversation, Message

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# ============================================
# REQUEST/RESPONSE SCHEMAS
# ============================================

class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    created_at: str
    updated_at: str
    message_count: int = 0
    last_message_preview: Optional[str] = None


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    role: Optional[str] = "user"


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str
    meta_data: dict = {}


# ============================================
# CONVERSATION ENDPOINTS
# ============================================

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    conversation = Conversation(
        user_id=current_user.id,
        title=request.title or "New Chat"
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        message_count=0
    )


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List user's conversations."""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(
        Conversation.updated_at.desc()
    ).limit(limit).offset(offset).all()
    
    result = []
    for conv in conversations:
        # Get message count and last message
        message_count = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).count()
        
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.desc()).first()
        
        result.append(ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            message_count=message_count,
            last_message_preview=last_message.content[:100] if last_message else None
        ))
    
    return result


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get message count
    message_count = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).count()
    
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        message_count=message_count
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted"}


@router.patch("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation title."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    conversation.title = title
    conversation.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Title updated", "title": title}


# ============================================
# MESSAGE ENDPOINTS
# ============================================

@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: str,
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a conversation and get AI response."""
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.content
    )
    
    db.add(user_message)
    db.flush()
    
    # Generate AI response (placeholder - integrate with your LLM)
    # TODO: Replace with actual LLM call
    assistant_response = await generate_ai_response(request.content, conversation_id, db)
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_response
    )
    
    db.add(assistant_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    
    # Update title if this is the first message
    message_count = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).count()
    
    if message_count == 0 and not conversation.title:
        # Generate title from first message (simple version)
        conversation.title = request.content[:50] + ("..." if len(request.content) > 50 else "")
    
    db.commit()
    db.refresh(assistant_message)
    
    return MessageResponse(
        id=assistant_message.id,
        conversation_id=assistant_message.conversation_id,
        role=assistant_message.role,
        content=assistant_message.content,
        created_at=assistant_message.created_at.isoformat(),
        meta_data=assistant_message.meta_data
    )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get messages in a conversation."""
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.asc()
    ).limit(limit).offset(offset).all()
    
    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.isoformat(),
            meta_data=msg.meta_data
        )
        for msg in messages
    ]


# ============================================
# HELPER FUNCTIONS
# ============================================

async def generate_ai_response(user_message: str, conversation_id: str, db: Session) -> str:
    """
    Generate AI response using your LLM service.
    TODO: Replace with actual LLM integration (OpenAI, etc.)
    """
    try:
        # Import your existing LLM client
        from app.llm_client import get_llm_client
        
        # Get conversation history
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
        
        # Build context
        context = []
        for msg in messages[-10:]:  # Last 10 messages
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current message
        context.append({
            "role": "user",
            "content": user_message
        })
        
        # Get LLM response
        llm_client = get_llm_client()
        response = llm_client.chat(context)
        
        return response
    
    except Exception as e:
        # Fallback response
        return f"I'm here to help! You said: {user_message}"

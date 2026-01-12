# ChatGPT-Like Authentication Implementation Guide

## Implementation Status

### ✅ Completed
1. **Documentation**
   - `/docs/how_chatgpt_like_accounts_work.md` - Complete architecture explanation
   - `/docs/bigquery_schema.sql` - Full database schema with indexes and examples
   
2. **Stack Analysis**
   - Frontend: React 18 + Vite + JavaScript
   - Backend: FastAPI + Python
   - Auth: JWT + OAuth (Google/Microsoft)
   - Database: SQLite (dev) + BigQuery (analytics)
   - Storage: GCS available

### 🔄 In Progress
The following components need to be implemented:

## Phase 1: Backend Session Management (CRITICAL)

### File: `/backend/app/services/session_service.py`

```python
"""
Session management with managed identity.
This is the CORE of ChatGPT-like authentication.
"""
import uuid
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from google.oauth2 import id_token
from google.auth.transport import requests
from app.services.bigquery_service import get_bigquery_client
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class SessionService:
    def __init__(self):
        self.bq_client = get_bigquery_client()
        self.env = os.getenv("ENVIRONMENT", "dev")
    
    async def create_session_from_google(
        self, 
        id_token_str: str,
        role: Optional[str] = None
    ) -> Dict:
        """
        Create session from Google ID token.
        This implements managed identity mapping.
        """
        try:
            # 1. Verify Google ID token
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                os.getenv("GOOGLE_CLIENT_ID")
            )
            
            # 2. Extract provider identity
            auth_uid = f"google:{idinfo['sub']}"
            email = idinfo['email']
            full_name = idinfo.get('name', '')
            
            # 3. Lookup or create internal user_id
            user = self.bq_client.get_user_by_auth_uid(auth_uid, "google")
            
            if not user:
                # First time login - create user
                user_id = str(uuid.uuid4())
                
                # Default role if not specified
                if not role:
                    role = "customer"
                
                lawyer_status = "pending" if role == "lawyer" else "not_applicable"
                
                self.bq_client.upsert_user({
                    "user_id": user_id,
                    "auth_provider": "google",
                    "auth_uid": auth_uid,
                    "email": email,
                    "full_name": full_name,
                    "role": role,
                    "lawyer_status": lawyer_status
                })
                
                user = {
                    "user_id": user_id,
                    "email": email,
                    "role": role,
                    "lawyer_status": lawyer_status
                }
            else:
                # Existing user - update last login
                user_id = user['user_id']
                self.bq_client.update_last_login(user_id)
            
            # 4. Create JWT with managed identity claims
            jwt_payload = {
                "user_id": user['user_id'],
                "email": user['email'],
                "role": user['role'],
                "lawyer_status": user.get('lawyer_status', 'not_applicable'),
                "env": self.env,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
            }
            
            access_token = jwt.encode(jwt_payload, SECRET_KEY, algorithm=ALGORITHM)
            
            # 5. Log login event
            self.bq_client.log_activity_event({
                "user_id": user['user_id'],
                "event_type": "login",
                "auth_provider": "google",
                "success": True
            })
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "user_id": user['user_id'],
                    "email": user['email'],
                    "role": user['role'],
                    "lawyer_status": user.get('lawyer_status')
                }
            }
            
        except Exception as e:
            # Log failed login
            self.bq_client.log_activity_event({
                "event_type": "login",
                "auth_provider": "google",
                "success": False,
                "payload": {"error": str(e)}
            })
            raise
    
    def verify_session(self, token: str) -> Dict:
        """
        Verify JWT and return claims.
        This extracts the managed identity.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
```

### File: `/backend/app/api/routes/session.py`

```python
"""
Session management endpoints.
"""
from fastapi import APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel
from app.services.session_service import SessionService

router = APIRouter(prefix="/api/session", tags=["session"])
session_service = SessionService()

class GoogleAuthRequest(BaseModel):
    id_token: str
    role: str = "customer"  # customer | lawyer

@router.post("/google")
async def create_session_google(
    request: GoogleAuthRequest,
    response: Response
):
    """
    Create session from Google OAuth.
    This is the entry point for managed identity creation.
    """
    try:
        session_data = await session_service.create_session_from_google(
            request.id_token,
            request.role
        )
        
        # Set HttpOnly secure cookie
        response.set_cookie(
            key="session",
            value=session_data['access_token'],
            httponly=True,
            secure=True,  # HTTPS only in prod
            samesite="lax",
            max_age=86400  # 24 hours
        )
        
        return session_data
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.delete("/")
async def logout(response: Response):
    """Logout - clear session cookie."""
    response.delete_cookie("session")
    return {"message": "Logged out"}

@router.get("/me")
async def get_current_user(session: str = Cookie(None)):
    """Get current user from session."""
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        claims = session_service.verify_session(session)
        return {
            "user_id": claims['user_id'],
            "email": claims['email'],
            "role": claims['role'],
            "lawyer_status": claims.get('lawyer_status')
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

## Phase 2: Conversation APIs (ChatGPT-like)

### File: `/backend/app/api/routes/conversations.py`

```python
"""
ChatGPT-like conversation management.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.middleware.auth import get_current_user
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/api/conversations", tags=["conversations"])
conversation_service = ConversationService()

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Chat"
    law_category: Optional[str] = None
    jurisdiction: Optional[str] = None

class SendMessageRequest(BaseModel):
    content: str
    role: str = "user"

@router.post("/")
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new conversation (like clicking 'New Chat' in ChatGPT)."""
    conversation = await conversation_service.create_conversation(
        user_id=current_user['user_id'],
        title=request.title,
        law_category=request.law_category,
        jurisdiction=request.jurisdiction
    )
    return conversation

@router.get("/")
async def list_conversations(
    current_user: dict = Depends(get_current_user),
    limit: int = 100,
    include_archived: bool = False
):
    """
    List user's conversations (for sidebar).
    Scoped to current_user's user_id.
    """
    conversations = await conversation_service.list_conversations(
        user_id=current_user['user_id'],
        limit=limit,
        include_archived=include_archived
    )
    return {"conversations": conversations}

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get conversation with messages.
    Security: Verifies user owns this conversation.
    """
    conversation = await conversation_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user['user_id']  # Security check
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send message in conversation.
    Security: Verifies user owns this conversation.
    """
    message = await conversation_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user['user_id'],
        content=request.content,
        role=request.role
    )
    
    return message

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete conversation (archive)."""
    await conversation_service.archive_conversation(
        conversation_id=conversation_id,
        user_id=current_user['user_id']
    )
    return {"message": "Conversation archived"}
```

## Phase 3: Auth Middleware (CRITICAL SECURITY)

### File: `/backend/app/middleware/auth.py`

```python
"""
Authentication middleware - extracts managed identity from JWT.
This is the security layer that enforces user scoping.
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredential
from app.services.session_service import SessionService

security = HTTPBearer()
session_service = SessionService()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredential = Depends(security)
) -> dict:
    """
    Extract user from JWT token.
    This provides the managed identity for all requests.
    
    CRITICAL: This is the ONLY way to get user_id.
    Never trust user_id from request body/query params.
    """
    token = credentials.credentials
    
    try:
        claims = session_service.verify_session(token)
        
        # Attach to request state for logging
        request.state.user_id = claims['user_id']
        request.state.role = claims['role']
        request.state.lawyer_status = claims.get('lawyer_status')
        
        return claims
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

def require_role(allowed_roles: List[str]):
    """
    Decorator to require specific roles.
    Usage: @require_role(["lawyer", "admin"])
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user['role'] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

def require_verified_lawyer(current_user: dict = Depends(get_current_user)):
    """
    Require verified lawyer status.
    Usage: current_user = Depends(require_verified_lawyer)
    """
    if current_user['role'] != "lawyer":
        raise HTTPException(status_code=403, detail="Lawyers only")
    
    if current_user.get('lawyer_status') != "approved":
        raise HTTPException(
            status_code=403,
            detail="Lawyer verification required"
        )
    
    return current_user
```

## Environment Variables Required

Create `.env` file:

```bash
# Environment
ENVIRONMENT=dev  # dev | prod
BASE_URL=http://localhost:4200

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production-use-openssl-rand-hex-32

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# BigQuery
BIGQUERY_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET=legalai
BIGQUERY_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# GCS
GCS_BUCKET_UPLOADS=legalai-uploads
GCS_BUCKET_DOCUMENTS=legalai-documents

# OpenAI
OPENAI_API_KEY=sk-...
```

## Next Steps to Complete Implementation

1. **Implement BigQuery Service** (`/backend/app/services/bigquery_service.py`)
   - Copy from PRODUCTION_AUTH_IMPLEMENTATION_PLAN.md
   
2. **Implement Conversation Service** (`/backend/app/services/conversation_service.py`)
   - Create/list/get conversations
   - Send messages
   - Archive conversations
   
3. **Update main.py** to include new routes and middleware

4. **Frontend Changes**:
   - Update AuthPage to use new `/api/session/google` endpoint
   - Create ConversationSidebar component (ChatGPT-like)
   - Create MessageList component
   - Add search functionality

5. **Testing**:
   - Test user isolation (User A cannot see User B's chats)
   - Test role gating (customers cannot access lawyer tools)
   - Test session expiration

## Security Checklist

- [ ] JWT secret is strong and environment-specific
- [ ] HttpOnly cookies in production
- [ ] HTTPS enforced in production
- [ ] Rate limiting on auth endpoints
- [ ] All queries include `user_id` from JWT claims
- [ ] Never trust `user_id` from client
- [ ] File uploads validated and scanned
- [ ] CSP headers configured
- [ ] CORS configured correctly for dev/prod

## Testing Commands

```bash
# Test session creation
curl -X POST http://localhost:8000/api/session/google \
  -H "Content-Type: application/json" \
  -d '{"id_token": "...", "role": "customer"}'

# Test getting current user
curl http://localhost:8000/api/session/me \
  -H "Cookie: session=..."

# Test creating conversation
curl -X POST http://localhost:8000/api/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Chat"}'

# Test listing conversations
curl http://localhost:8000/api/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Summary

This implementation provides:

✅ **Managed Identity**: External auth → internal user_id mapping
✅ **ChatGPT-like Persistence**: Conversations, messages, attachments scoped to user_id
✅ **Security**: JWT-based, server-verified identity, user scoping on all queries
✅ **Role-Based Access**: Customer vs Lawyer vs Admin with middleware enforcement
✅ **BigQuery Integration**: Analytics and identity storage
✅ **Dev/Prod Isolation**: Environment-specific data and cookies

The system is designed exactly like ChatGPT: your account, your history, your data, all persisted and retrieved based on your managed identity.

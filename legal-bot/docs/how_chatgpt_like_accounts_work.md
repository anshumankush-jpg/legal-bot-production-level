# How ChatGPT-Like Accounts Work in LegalAI

## Overview
This document explains how LegalAI implements ChatGPT-style authentication, managed identity, and personal data persistence.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHATGPT-LIKE AUTH FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. USER AUTHENTICATION                                          │
│     ┌──────────────┐                                            │
│     │ User clicks  │                                            │
│     │ "Continue    │                                            │
│     │ with Google" │                                            │
│     └──────┬───────┘                                            │
│            │                                                     │
│            ▼                                                     │
│     ┌──────────────┐                                            │
│     │ Google Auth  │ Returns: auth_uid + email + ID token      │
│     │ Provider     │                                            │
│     └──────┬───────┘                                            │
│            │                                                     │
│            ▼                                                     │
│  2. SERVER SESSION CREATION (MANAGED IDENTITY)                  │
│     ┌──────────────────────────────────────────┐               │
│     │ POST /api/session                         │               │
│     │                                           │               │
│     │ 1. Verify ID token with provider SDK     │               │
│     │ 2. Extract auth_uid + email               │               │
│     │ 3. Lookup/Create internal user_id (UUID) │               │
│     │ 4. Upsert to BigQuery identity_users      │               │
│     │ 5. Issue signed JWT with claims:          │               │
│     │    - user_id                               │               │
│     │    - email                                 │               │
│     │    - role (customer|lawyer|admin)         │               │
│     │    - lawyer_status                         │               │
│     │    - env (dev|prod)                        │               │
│     │ 6. Set HttpOnly secure cookie             │               │
│     └───────────────┬────────────────────────────┘               │
│                     │                                            │
│                     ▼                                            │
│  3. USER SEES THEIR PORTAL                                      │
│     ┌──────────────────────────────────────────┐               │
│     │ Customer → /app (chat + basic tools)     │               │
│     │ Lawyer (pending) → /lawyer/onboarding    │               │
│     │ Lawyer (approved) → /lawyer/dashboard    │               │
│     │ Admin → /admin/review                     │               │
│     └──────────────────────────────────────────┘               │
│                                                                   │
│  4. ALL REQUESTS CARRY MANAGED IDENTITY                         │
│     ┌──────────────────────────────────────────┐               │
│     │ Every API call:                           │               │
│     │ - Cookie/JWT verified by middleware       │               │
│     │ - user_id extracted from claims           │               │
│     │ - NEVER trusted from client payload       │               │
│     │ - All queries scoped: WHERE user_id = X   │               │
│     └──────────────────────────────────────────┘               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Managed Identity

**External Identity** (from auth provider):
- Google UID: `google:108123456789`
- Microsoft UID: `microsoft:abc123def456`
- Email/Password UID: `email:user@example.com`

**Internal Managed Identity** (our system):
- `user_id`: `550e8400-e29b-41d4-a716-446655440000` (UUID v4)
- Stable, never changes
- Decoupled from auth provider
- Used for ALL data scoping

**Why Managed Identity?**
- User can switch auth providers (Google → Microsoft) but keep same history
- We control the identity lifecycle
- Security: server-issued, cryptographically signed
- Multi-tenant isolation: all data queries use `user_id`

### 2. Session Claims (JWT Payload)

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "customer",
  "lawyer_status": "not_applicable",
  "env": "prod",
  "iat": 1704067200,
  "exp": 1704153600
}
```

**Critical Security Rule:**
- Backend ALWAYS reads `user_id` from verified JWT claims
- Backend NEVER accepts `user_id` from request body/query params
- Client cannot impersonate another user

### 3. ChatGPT-Like Data Model

#### Conversations (Chats)
```python
{
  "conversation_id": "uuid",
  "user_id": "uuid",  # ← Scoped to user
  "title": "Traffic ticket question",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:15:00Z",
  "is_archived": false
}
```

#### Messages
```python
{
  "message_id": "uuid",
  "conversation_id": "uuid",
  "user_id": "uuid",  # ← Scoped to user
  "role": "user",  # user|assistant|system
  "content": "What are penalties for speeding?",
  "created_at": "2024-01-01T10:00:00Z",
  "metadata": {
    "model": "gpt-4o-mini",
    "tokens": 150,
    "citations": [...]
  }
}
```

#### Attachments (Files/Images)
```python
{
  "attachment_id": "uuid",
  "user_id": "uuid",  # ← Scoped to user
  "conversation_id": "uuid",  # nullable
  "file_name": "ticket.pdf",
  "file_type": "application/pdf",
  "gcs_url": "gs://legalai-uploads/user_id/file.pdf",
  "sha256": "abc123...",
  "created_at": "2024-01-01T10:00:00Z"
}
```

## How It Works: Step-by-Step

### Scenario: User Logs In and Chats

**Step 1: Login**
```
User clicks "Continue with Google"
→ Google returns: auth_uid="google:12345", email="user@gmail.com"
→ Frontend sends ID token to: POST /api/session
```

**Step 2: Backend Creates Session**
```python
# Backend (FastAPI)
@app.post("/api/session")
async def create_session(id_token: str):
    # 1. Verify token with Google SDK
    decoded = verify_google_token(id_token)
    auth_uid = f"google:{decoded['sub']}"
    email = decoded['email']
    
    # 2. Lookup or create user_id
    user = bigquery_client.get_user_by_auth_uid(auth_uid, "google")
    if not user:
        user_id = str(uuid.uuid4())
        bigquery_client.upsert_user({
            "user_id": user_id,
            "auth_provider": "google",
            "auth_uid": auth_uid,
            "email": email,
            "role": "customer",  # Default, can be changed
            "lawyer_status": "not_applicable"
        })
    else:
        user_id = user['user_id']
    
    # 3. Issue JWT with claims
    jwt_payload = {
        "user_id": user_id,
        "email": email,
        "role": user['role'],
        "lawyer_status": user['lawyer_status'],
        "env": "prod"
    }
    token = create_jwt(jwt_payload)
    
    # 4. Set secure cookie
    response.set_cookie(
        "session",
        token,
        httponly=True,
        secure=True,  # HTTPS only in prod
        samesite="lax"
    )
    
    return {"user_id": user_id, "role": user['role']}
```

**Step 3: User Creates New Chat**
```
User clicks "New Chat" in sidebar
→ Frontend: POST /api/conversations
→ Backend extracts user_id from JWT
→ Creates conversation row with that user_id
```

```python
@app.post("/api/conversations")
async def create_conversation(request: Request):
    # Extract user_id from verified JWT (middleware)
    user_id = request.state.user_id  # From JWT claims
    
    conversation_id = str(uuid.uuid4())
    
    # Save to database
    db.execute("""
        INSERT INTO conversations (conversation_id, user_id, title, created_at)
        VALUES (?, ?, ?, ?)
    """, (conversation_id, user_id, "New Chat", datetime.now()))
    
    return {"conversation_id": conversation_id}
```

**Step 4: User Sends Message**
```
User types: "What are penalties for speeding in Ontario?"
→ Frontend: POST /api/conversations/{id}/messages
→ Backend:
   1. Verifies user_id from JWT
   2. Checks user owns this conversation
   3. Appends message
   4. Calls LLM
   5. Saves assistant response
```

```python
@app.post("/api/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    request: Request
):
    user_id = request.state.user_id  # From JWT
    
    # Security check: verify user owns this conversation
    conv = db.execute("""
        SELECT * FROM conversations 
        WHERE conversation_id = ? AND user_id = ?
    """, (conversation_id, user_id)).fetchone()
    
    if not conv:
        raise HTTPException(403, "Not your conversation")
    
    # Save user message
    message_id = str(uuid.uuid4())
    db.execute("""
        INSERT INTO messages (message_id, conversation_id, user_id, role, content)
        VALUES (?, ?, ?, 'user', ?)
    """, (message_id, conversation_id, user_id, message.content))
    
    # Generate response
    response = await llm_client.chat(message.content)
    
    # Save assistant message
    assistant_id = str(uuid.uuid4())
    db.execute("""
        INSERT INTO messages (message_id, conversation_id, user_id, role, content)
        VALUES (?, ?, ?, 'assistant', ?)
    """, (assistant_id, conversation_id, user_id, response))
    
    return {"message_id": assistant_id, "content": response}
```

**Step 5: User Uploads File**
```
User uploads "ticket.pdf"
→ Frontend: POST /api/uploads (gets signed URL)
→ Frontend: PUT to GCS with file
→ Frontend: POST /api/attachments (saves metadata)
```

```python
@app.post("/api/uploads")
async def create_upload_url(
    file_name: str,
    file_type: str,
    request: Request
):
    user_id = request.state.user_id
    
    # Generate GCS path: user_id/timestamp_filename
    gcs_path = f"{user_id}/{int(time.time())}_{file_name}"
    
    # Create signed upload URL
    signed_url = gcs_client.generate_signed_url(
        bucket="legalai-uploads",
        path=gcs_path,
        method="PUT",
        expiration=3600  # 1 hour
    )
    
    return {
        "upload_url": signed_url,
        "gcs_path": gcs_path
    }

@app.post("/api/attachments")
async def save_attachment(
    attachment: AttachmentCreate,
    request: Request
):
    user_id = request.state.user_id
    
    attachment_id = str(uuid.uuid4())
    db.execute("""
        INSERT INTO attachments 
        (attachment_id, user_id, conversation_id, file_name, file_type, gcs_url, sha256)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        attachment_id, user_id, attachment.conversation_id,
        attachment.file_name, attachment.file_type,
        attachment.gcs_url, attachment.sha256
    ))
    
    return {"attachment_id": attachment_id}
```

**Step 6: User Searches History**
```
User types "speeding" in search bar
→ Frontend: GET /api/search?q=speeding
→ Backend searches ONLY within user's conversations/messages
```

```python
@app.get("/api/search")
async def search(q: str, request: Request):
    user_id = request.state.user_id
    
    # Search scoped to user_id
    results = db.execute("""
        SELECT 
            m.message_id,
            m.conversation_id,
            m.content,
            c.title,
            m.created_at
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.conversation_id
        WHERE m.user_id = ?  -- ← USER SCOPING
          AND (
            m.content LIKE ? 
            OR c.title LIKE ?
          )
        ORDER BY m.created_at DESC
        LIMIT 50
    """, (user_id, f"%{q}%", f"%{q}%")).fetchall()
    
    return {"results": results}
```

**Step 7: User Logs Out and Logs Back In**
```
User logs out → cookie cleared
User logs back in → same user_id retrieved
→ Sidebar loads: GET /api/conversations
→ Shows all their previous chats
```

```python
@app.get("/api/conversations")
async def list_conversations(request: Request):
    user_id = request.state.user_id
    
    # Load user's conversations
    conversations = db.execute("""
        SELECT * FROM conversations
        WHERE user_id = ?  -- ← USER SCOPING
        ORDER BY updated_at DESC
    """, (user_id,)).fetchall()
    
    return {"conversations": conversations}
```

## Role-Based Access Control

### Customer vs Lawyer vs Admin

**Middleware checks claims:**
```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Extract JWT from cookie
    token = request.cookies.get("session")
    if not token:
        return JSONResponse({"error": "Unauthorized"}, 401)
    
    # Verify and decode
    try:
        claims = verify_jwt(token)
        request.state.user_id = claims['user_id']
        request.state.role = claims['role']
        request.state.lawyer_status = claims['lawyer_status']
    except:
        return JSONResponse({"error": "Invalid token"}, 401)
    
    return await call_next(request)

def require_role(allowed_roles: List[str]):
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            if request.state.role not in allowed_roles:
                raise HTTPException(403, "Forbidden")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_verified_lawyer(func):
    async def wrapper(request: Request, *args, **kwargs):
        if request.state.role != "lawyer":
            raise HTTPException(403, "Lawyers only")
        if request.state.lawyer_status != "approved":
            raise HTTPException(403, "Verification required")
        return await func(request, *args, **kwargs)
    return wrapper

# Usage
@app.get("/lawyer/dashboard")
@require_verified_lawyer
async def lawyer_dashboard(request: Request):
    # Only approved lawyers can access
    pass

@app.get("/admin/lawyers")
@require_role(["admin"])
async def admin_review(request: Request):
    # Only admins can access
    pass
```

## Security Guarantees

### 1. User Isolation
- All queries include `WHERE user_id = ?`
- User A cannot read User B's data
- Enforced at database level

### 2. Managed Identity
- `user_id` comes from server-verified JWT
- Client cannot forge or modify
- Cryptographically signed

### 3. Role Enforcement
- Middleware checks role + lawyer_status
- UI hides links, but server blocks requests
- Defense in depth

### 4. File Security
- Files stored in GCS with user_id prefix
- Signed URLs expire after 1 hour
- SHA256 checksums prevent tampering

## Dev vs Prod Isolation

### Environment Separation
```python
# config.py
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")  # dev|prod
BASE_URL = {
    "dev": "http://localhost:4200",
    "prod": "https://legalai.work"
}[ENVIRONMENT]

# All identity records include env column
bigquery_client.upsert_user({
    ...
    "env": ENVIRONMENT
})

# All queries filter by env
WHERE user_id = ? AND env = ?
```

### Separate Cookies
```python
# Dev
response.set_cookie(
    "session",
    token,
    domain="localhost",
    ...
)

# Prod
response.set_cookie(
    "session",
    token,
    domain=".legalai.work",
    secure=True,  # HTTPS only
    ...
)
```

## Summary

**How ChatGPT-like accounts work:**

1. **Login** → Auth provider returns external UID
2. **Session** → Backend maps to internal `user_id` (UUID)
3. **Managed Identity** → Server-issued JWT with claims
4. **Data Scoping** → All queries: `WHERE user_id = ?`
5. **Persistence** → Conversations, messages, files saved with `user_id`
6. **Next Login** → Same `user_id` retrieved, shows same history
7. **Role Gating** → Middleware checks claims for access control

**Key Principle:**
> The server controls identity. The client presents credentials. The server issues a signed session. All data is scoped to that session's `user_id`. The client can never impersonate another user.

This is exactly how ChatGPT works: your account, your history, your data.

# How ChatGPT-Like Accounts Work in LegalAI

## Overview

LegalAI implements a ChatGPT-style authentication and data persistence system where:
- Users log in once and see all their history (chats, uploads, searches)
- Each user has a stable internal identity (user_id) separate from auth providers
- All data is strictly scoped to the authenticated user
- Role-based access controls separate Customer, Lawyer, and Admin experiences

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER JOURNEY                               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: AUTHENTICATION (External Identity)                         │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  User clicks "Continue with Google" or enters email/pwd    │    │
│  │  → Firebase Auth returns: auth_uid, email, ID token        │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: SESSION CREATION (Managed Identity)                        │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Client → POST /api/session { idToken }                    │    │
│  │  Backend:                                                   │    │
│  │    1. Verify ID token with Firebase SDK (never trust client)│   │
│  │    2. Extract: auth_uid, provider, email                   │    │
│  │    3. Lookup or create internal user_id (UUID)             │    │
│  │    4. Upsert to BigQuery: identity_users                   │    │
│  │    5. Issue secure session cookie with claims:             │    │
│  │       { user_id, email, role, lawyer_status, env }         │    │
│  │    6. Return: { user_id, role, needs_onboarding }          │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: ROLE SELECTION (First-Time Users)                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  If new user:                                               │    │
│  │    → Show: "Join as Customer" or "Join as Lawyer"          │    │
│  │    → POST /api/auth/set-role { role }                      │    │
│  │    → Update identity_users.role                            │    │
│  │    → If lawyer: lawyer_status = 'pending'                  │    │
│  │                redirect to /lawyer/onboarding              │    │
│  │    → If customer: redirect to /app                         │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: AUTHENTICATED REQUESTS (Server-Verified Identity)          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Every API request:                                         │    │
│  │    → Includes session cookie (HttpOnly, Secure)            │    │
│  │    → Backend middleware verifies signature                 │    │
│  │    → Extracts user_id, role, lawyer_status from claims     │    │
│  │    → NEVER accepts user_id from client payload             │    │
│  │    → All queries scoped: WHERE user_id = session.user_id   │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: DATA PERSISTENCE (User-Scoped Storage)                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Conversations: conversation_id + user_id                   │    │
│  │  Messages: message_id + conversation_id + user_id          │    │
│  │  Attachments: attachment_id + user_id + conversation_id    │    │
│  │  Search: ONLY within user's data                           │    │
│  │  History: Loaded by user_id on login                       │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Managed Identity Concept

### External vs Internal Identity

| Type | What It Is | Where It Lives | Trust Level |
|------|-----------|----------------|-------------|
| **External Identity** | Provider's UID (Google UID, Microsoft UID, Firebase UID) | Firebase Auth | Verified by provider |
| **Internal Identity** | Our stable `user_id` (UUID v4) | BigQuery + Session Claims | Verified by our backend |

### Why Managed Identity?

**Problem**: If we use provider UIDs directly:
- User switching from Google to Email login would create 2 accounts
- No stable identifier across providers
- Cannot add custom claims (role, lawyer_status)
- Harder to manage data consistency

**Solution**: Managed Identity
- We create ONE internal `user_id` per unique email
- Map external auth identities to internal `user_id`
- Store mapping in BigQuery: `identity_users` table
- All app data references `user_id`, not provider UID

### Security Properties

1. **Server-Verified Sessions**:
   - Client sends ID token from provider
   - Backend verifies cryptographically
   - Backend issues OUR session with OUR claims
   - Session is signed (JWT) or encrypted (cookie session)

2. **Never Trust Client**:
   - NEVER accept `user_id` from client request body
   - ALWAYS derive `user_id` from server-verified session
   - Client can't impersonate other users

3. **Scoped Queries**:
   ```sql
   -- BAD (trusts client)
   SELECT * FROM conversations WHERE conversation_id = @id
   
   -- GOOD (scoped to session user)
   SELECT * FROM conversations 
   WHERE conversation_id = @id 
     AND user_id = @session_user_id
   ```

---

## Authentication Flow (Step-by-Step)

### Login Flow

```
1. USER ACTION
   ├─ Clicks "Continue with Google"
   └─ OR enters email/password

2. FIREBASE AUTH (Client-Side)
   ├─ Opens OAuth popup (Google/Microsoft)
   ├─ OR signs in with email/password
   └─ Returns: { user: { uid, email }, credential: { idToken } }

3. SESSION CREATION (Server-Side)
   POST /api/session
   Headers: { "Authorization": "Bearer <idToken>" }
   
   Backend:
   ├─ Verify ID token with Firebase Admin SDK
   ├─ Extract: auth_uid, provider, email, email_verified
   ├─ Query BigQuery:
   │  SELECT user_id FROM identity_users 
   │  WHERE auth_uid = @uid AND auth_provider = @provider AND env = @env
   ├─ If NOT found:
   │  ├─ Generate new user_id = UUID()
   │  ├─ Check if email exists with different provider:
   │  │  └─ If yes: link to existing user_id
   │  └─ INSERT into identity_users
   ├─ If found: UPDATE last_login_at
   ├─ Create session payload:
   │  { user_id, email, role, lawyer_status, exp: now+7days }
   ├─ Sign as JWT OR encrypt as session cookie
   ├─ Set cookie:
   │  Set-Cookie: session=<signed_token>; 
   │               HttpOnly; Secure; SameSite=Strict; Max-Age=604800
   └─ Return: { user_id, email, role, lawyer_status }

4. CLIENT REDIRECT
   ├─ If needs_onboarding: → /auth/role-selection
   ├─ If role='lawyer' && lawyer_status='pending': → /lawyer/onboarding
   ├─ If role='lawyer' && lawyer_status='approved': → /lawyer/dashboard
   ├─ If role='customer': → /app
   └─ Else: → /app
```

### Subsequent Requests

```
1. CLIENT REQUEST
   GET /api/conversations
   Cookie: session=<signed_token>

2. BACKEND MIDDLEWARE
   ├─ Extract session cookie
   ├─ Verify signature/decrypt
   ├─ Extract claims: { user_id, role, lawyer_status }
   ├─ Attach to request context: req.user = { user_id, ... }
   └─ Pass to route handler

3. ROUTE HANDLER
   ├─ Read user_id from req.user (NEVER from request body)
   ├─ Query database with user_id scoping:
   │  SELECT * FROM conversations WHERE user_id = req.user.user_id
   └─ Return scoped data
```

---

## Chat History Persistence

### Data Model

#### 1. Conversations Table
```sql
CREATE TABLE conversations (
  conversation_id STRING PRIMARY KEY,  -- UUID
  user_id STRING NOT NULL,             -- References identity_users.user_id
  title STRING,                        -- Auto-generated from first message
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  is_archived BOOLEAN DEFAULT FALSE,
  metadata JSON                        -- { model, tokens, custom_instructions, etc. }
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, updated_at;
```

#### 2. Messages Table
```sql
CREATE TABLE messages (
  message_id STRING PRIMARY KEY,       -- UUID
  conversation_id STRING NOT NULL,     -- FK to conversations
  user_id STRING NOT NULL,             -- Redundant but ensures scoping
  role STRING NOT NULL,                -- 'user' | 'assistant' | 'system' | 'tool'
  content TEXT,                        -- Message text
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  metadata JSON                        -- { model, tokens, citations, tool_calls, etc. }
)
PARTITION BY DATE(created_at)
CLUSTER BY conversation_id, user_id;
```

#### 3. Attachments Table
```sql
CREATE TABLE attachments (
  attachment_id STRING PRIMARY KEY,
  user_id STRING NOT NULL,
  conversation_id STRING,              -- Nullable (can upload without conversation)
  file_name STRING,
  file_type STRING,                    -- 'image/png', 'application/pdf', etc.
  file_size INT64,
  gcs_url STRING,                      -- gs://bucket/path/to/file
  sha256 STRING,                       -- Checksum for deduplication
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  metadata JSON                        -- { ocr_text, extracted_info, etc. }
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id;
```

### ChatGPT-Like Behavior

#### New Chat
```typescript
// Client: User clicks "New Chat"
POST /api/conversations
Headers: { Cookie: session=... }
Body: {}  // No user_id in body!

// Backend derives user_id from session
conversation_id = UUID()
INSERT INTO conversations (conversation_id, user_id, title, created_at)
VALUES (conversation_id, session.user_id, 'New chat', NOW())

// Return conversation_id to client
{ conversation_id, title: 'New chat' }
```

#### Send Message
```typescript
// Client sends first message
POST /api/conversations/{conversation_id}/messages
Body: { content: "What are my rights if I'm pulled over?" }

// Backend
1. Verify conversation belongs to session.user_id:
   SELECT user_id FROM conversations WHERE conversation_id = @id
   IF user_id != session.user_id: RETURN 403 Forbidden

2. Insert user message:
   message_id = UUID()
   INSERT INTO messages (message_id, conversation_id, user_id, role, content)
   VALUES (message_id, conversation_id, session.user_id, 'user', content)

3. Generate AI response (using LegalAI backend)

4. Insert assistant message:
   INSERT INTO messages (message_id, conversation_id, user_id, role, content, metadata)
   VALUES (UUID(), conversation_id, session.user_id, 'assistant', ai_response, { model, tokens, citations })

5. Update conversation title if first message:
   IF (SELECT COUNT(*) FROM messages WHERE conversation_id = @id) == 2:
     UPDATE conversations SET title = GENERATE_TITLE(content) WHERE conversation_id = @id

6. Update conversation.updated_at:
   UPDATE conversations SET updated_at = NOW() WHERE conversation_id = @id
```

#### Load History (Sidebar)
```typescript
// Client loads sidebar on login
GET /api/conversations?limit=50&offset=0

// Backend
SELECT conversation_id, title, updated_at, metadata
FROM conversations
WHERE user_id = session.user_id
  AND is_archived = FALSE
ORDER BY updated_at DESC
LIMIT 50 OFFSET 0

// Returns:
[
  { conversation_id, title: "Traffic rights question", updated_at: "2026-01-15T10:30:00Z" },
  { conversation_id, title: "DUI defense options", updated_at: "2026-01-14T15:20:00Z" },
  ...
]
```

#### Load Conversation Messages
```typescript
// Client clicks conversation in sidebar
GET /api/conversations/{conversation_id}

// Backend
1. Verify ownership:
   SELECT user_id FROM conversations WHERE conversation_id = @id
   IF user_id != session.user_id: RETURN 403

2. Load messages:
   SELECT message_id, role, content, created_at, metadata
   FROM messages
   WHERE conversation_id = @id
     AND user_id = session.user_id
   ORDER BY created_at ASC

3. Return conversation + messages:
   {
     conversation_id,
     title,
     messages: [
       { role: 'user', content: "What are my rights...", created_at: ... },
       { role: 'assistant', content: "You have the right to...", created_at: ..., metadata: { citations } }
     ]
   }
```

---

## File Uploads & Attachments

### Upload Flow

```
1. CLIENT REQUESTS SIGNED URL
   POST /api/uploads/signed-url
   Body: { fileName: "ticket.pdf", fileType: "application/pdf", fileSize: 52341 }
   
   Backend:
   ├─ Validate: fileType in allowed list, fileSize < 10MB
   ├─ Generate: attachment_id = UUID()
   ├─ Create GCS signed URL:
   │  path = "attachments/{session.user_id}/{attachment_id}/{fileName}"
   │  signedUrl = gcs.generateSignedUrl(path, expires=15min, method='PUT')
   ├─ Save attachment metadata (pending):
   │  INSERT INTO attachments (attachment_id, user_id, file_name, file_type, gcs_url, status='uploading')
   └─ Return: { attachment_id, signedUrl, expiresAt }

2. CLIENT UPLOADS DIRECTLY TO GCS
   PUT <signedUrl>
   Body: <file_bytes>
   Headers: { "Content-Type": "application/pdf" }

3. CLIENT CONFIRMS UPLOAD
   POST /api/uploads/{attachment_id}/confirm
   Body: { conversation_id: "...", sha256: "..." }
   
   Backend:
   ├─ Verify attachment belongs to session.user_id
   ├─ Verify file exists in GCS
   ├─ Optionally: run OCR, extract text, virus scan
   ├─ Update attachment:
   │  UPDATE attachments SET 
   │    conversation_id = @conversation_id, 
   │    sha256 = @sha256,
   │    status = 'completed'
   │  WHERE attachment_id = @id AND user_id = session.user_id
   └─ Return: { attachment_id, gcs_url }

4. ATTACHMENT LINKED TO CONVERSATION
   └─ Now visible in conversation context
```

### Retrieval

```typescript
// Client displays uploaded files in chat
GET /api/conversations/{conversation_id}/attachments

// Backend
SELECT attachment_id, file_name, file_type, gcs_url, created_at
FROM attachments
WHERE conversation_id = @id
  AND user_id = session.user_id
ORDER BY created_at ASC
```

---

## Search (User-Scoped)

### Search Implementation

```typescript
// Client: User types in search bar
GET /api/search?q=speeding+ticket&limit=10

// Backend
1. Parse query: q = "speeding ticket"

2. Build search query (scoped to session.user_id):
   SELECT 
     c.conversation_id,
     c.title,
     m.message_id,
     m.role,
     SUBSTR(m.content, 0, 200) AS snippet,
     m.created_at
   FROM conversations c
   JOIN messages m ON c.conversation_id = m.conversation_id
   WHERE c.user_id = @session_user_id
     AND m.user_id = @session_user_id
     AND (
       LOWER(m.content) LIKE CONCAT('%', LOWER(@query), '%')
       OR LOWER(c.title) LIKE CONCAT('%', LOWER(@query), '%')
     )
   ORDER BY m.created_at DESC
   LIMIT 10

3. Optionally: search attachments OCR text too:
   UNION
   SELECT 
     a.conversation_id,
     a.file_name AS title,
     a.attachment_id AS message_id,
     'attachment' AS role,
     JSON_EXTRACT(a.metadata, '$.ocr_text') AS snippet,
     a.created_at
   FROM attachments a
   WHERE a.user_id = @session_user_id
     AND JSON_EXTRACT(a.metadata, '$.ocr_text') LIKE CONCAT('%', @query, '%')

4. Return search results with conversation context
```

### Security Note
- Search ALWAYS includes `user_id = session.user_id` filter
- User can ONLY search their own data
- No cross-user information leakage

---

## Role Separation & Authorization

### Roles

| Role | Access Level | Routes Allowed |
|------|-------------|----------------|
| **customer** | Basic chat + limited tools | `/app/*`, `/api/chat`, `/api/conversations`, `/api/search` |
| **lawyer** (pending) | Onboarding only | `/lawyer/onboarding`, `/lawyer/status` |
| **lawyer** (approved) | Full lawyer tools + leads | `/lawyer/dashboard`, `/tools/*`, `/leads/*`, all customer routes |
| **lawyer** (rejected) | Onboarding + status | `/lawyer/onboarding`, `/lawyer/status` |
| **admin** | Everything + review panel | `/*`, `/admin/*` |

### Middleware Implementation

```typescript
// Route protection example
@router.get("/tools/document-generator")
async def document_generator(
  lawyer = Depends(require_verified_lawyer)  // Middleware
):
  # Only executes if session.role == 'lawyer' AND session.lawyer_status == 'approved'
  return { "message": f"Welcome {lawyer['email']}" }
```

### Frontend Guards

```typescript
// Angular route guard
export class LawyerGuard implements CanActivate {
  canActivate(route): Observable<boolean> {
    return this.auth.getCurrentUser().pipe(
      map(user => {
        if (user.role !== 'lawyer') {
          this.router.navigate(['/app']);
          return false;
        }
        if (user.lawyer_status !== 'approved') {
          this.router.navigate(['/lawyer/onboarding']);
          return false;
        }
        return true;
      })
    );
  }
}
```

---

## Dev vs Prod Isolation

### Problem
User logs in on `dev.legalai.work` but gets redirected to `legalai.work`.

### Solution

#### 1. Environment-Specific Redirect URIs

```typescript
// Backend config
const REDIRECT_URIS = {
  dev: {
    frontend: process.env.DEV_FRONTEND_URL,  // http://localhost:4200
    oauth: {
      google: process.env.GOOGLE_OAUTH_REDIRECT_DEV,
      microsoft: process.env.MICROSOFT_OAUTH_REDIRECT_DEV
    }
  },
  prod: {
    frontend: process.env.PROD_FRONTEND_URL,  // https://legalai.work
    oauth: {
      google: process.env.GOOGLE_OAUTH_REDIRECT_PROD,
      microsoft: process.env.MICROSOFT_OAUTH_REDIRECT_PROD
    }
  }
};

// Use correct redirect based on request origin
function getRedirectUri(req: Request): string {
  const origin = req.headers.get('origin');
  const env = origin.includes('localhost') || origin.includes('dev.') ? 'dev' : 'prod';
  return REDIRECT_URIS[env].frontend;
}
```

#### 2. Domain-Specific Cookies

```typescript
// Dev: Set cookie for localhost
Set-Cookie: session=<token>; Domain=localhost; HttpOnly; SameSite=Lax

// Prod: Set cookie for .legalai.work
Set-Cookie: session=<token>; Domain=.legalai.work; HttpOnly; Secure; SameSite=Strict
```

#### 3. Environment Column in BigQuery

```sql
-- All tables include env column
CREATE TABLE identity_users (
  user_id STRING,
  email STRING,
  env STRING,  -- 'dev' | 'prod'
  ...
)
CLUSTER BY env;

-- Queries always filter by env
SELECT * FROM identity_users 
WHERE email = @email AND env = @current_env
```

#### 4. Separate Firebase Projects (Recommended)

```
Firebase Project: legalai-dev
  → Web app: localhost:4200, dev.legalai.work
  → OAuth redirect: http://localhost:4200/auth/callback

Firebase Project: legalai-prod
  → Web app: legalai.work
  → OAuth redirect: https://legalai.work/auth/callback
```

---

## Security Best Practices

### 1. Session Security
- **HttpOnly**: Prevent JS access to session cookie
- **Secure**: Only send over HTTPS in production
- **SameSite=Strict**: Prevent CSRF attacks
- **Short expiry**: 7 days, require re-authentication

### 2. Rate Limiting
```typescript
// Apply to auth endpoints
@ratelimit(10, per_minute=True)
@router.post("/api/session")
async def create_session(): ...
```

### 3. Input Validation
```typescript
// Validate all file uploads
allowed_types = ['image/png', 'image/jpeg', 'application/pdf']
max_size = 10 * 1024 * 1024  // 10 MB

if file.type not in allowed_types:
  raise HTTPException(400, "Invalid file type")
if file.size > max_size:
  raise HTTPException(400, "File too large")
```

### 4. Audit Logging
```sql
-- Log all security-sensitive events
INSERT INTO activity_events (user_id, event_type, metadata)
VALUES 
  (@user_id, 'login', { ip, user_agent }),
  (@user_id, 'file_upload', { attachment_id, file_type }),
  (@user_id, 'role_change', { old_role, new_role });
```

### 5. CSP Headers
```typescript
// Add security headers
app.use((req, res, next) => {
  res.setHeader("Content-Security-Policy", "default-src 'self'; img-src 'self' data: https://storage.googleapis.com");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Strict-Transport-Security", "max-age=31536000");
  next();
});
```

---

## Summary

**Key Principles**:
1. **Managed Identity**: Internal `user_id` separate from auth provider UIDs
2. **Server-Verified Sessions**: Never trust client-provided identity
3. **User Scoping**: All queries include `WHERE user_id = session.user_id`
4. **ChatGPT-Like UX**: Conversations, messages, and files persist across logins
5. **Role Separation**: Customer vs Lawyer vs Admin with different access levels
6. **Security First**: HttpOnly cookies, rate limiting, audit logs, scoped queries

**Data Flow**:
```
Login → Session (with user_id) → Scoped Queries → User-Specific Data → Sidebar/Search
```

This architecture ensures:
- Users only see their own data
- Roles determine feature access
- History persists across logins
- Security is enforced server-side
- Dev/prod environments are isolated

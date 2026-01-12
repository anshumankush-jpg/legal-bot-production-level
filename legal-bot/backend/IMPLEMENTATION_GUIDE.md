# Complete Implementation Guide: Legal Assistant System

This guide provides the complete implementation requirements for the legal assistant system, including backend API endpoints, frontend UI flow, and integration points.

## 📋 Table of Contents

1. [System Prompt](#system-prompt)
2. [Backend Requirements](#backend-requirements)
3. [Frontend Requirements](#frontend-requirements)
4. [Full UX Flow](#full-ux-flow)
5. [API Endpoints Reference](#api-endpoints-reference)

---

## 1. System Prompt

The system prompt has been updated in `backend/app/core/config.py` as `LEGAL_ASSISTANT_SYSTEM_PROMPT`. This prompt is automatically used for all legal queries.

**Key Features:**
- Emphasizes that the assistant is NOT a lawyer
- Provides structured options (FIGHT vs PAY)
- Includes mandatory disclaimers
- Supports multiple languages
- Handles ticket/summons parsing

---

## 2. Backend Requirements

### 2.1 Authentication & Session

**New Endpoints:**

```python
# POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
Response: {
  "access_token": "...",
  "user_id": "...",
  "preferred_language": "en",
  "country_code": "CA"
}

# GET /api/auth/me
Headers: Authorization: Bearer <token>
Response: {
  "user_id": "...",
  "email": "...",
  "preferred_language": "en",
  "country_code": "CA"
}
```

**Implementation Notes:**
- Use JWT tokens for authentication
- Store user sessions (can use in-memory dict for MVP, database for production)
- Include `user_id` in all authenticated requests

### 2.2 Language & Country Preferences

**New Endpoint:**

```python
# POST /api/user/preferences
Headers: Authorization: Bearer <token>
Body: {
  "language": "en",  # "en", "fr", "hi", "pa", "es", "ta", "zh"
  "country": "CA"    # "CA", "US"
}
Response: {
  "success": true,
  "preferred_language": "en",
  "country_code": "CA"
}
```

**User Profile Model Extension:**
```python
class UserProfile:
    user_id: str
    email: str
    preferred_language: str = "en"
    country_code: str = "CA"
    created_at: datetime
    updated_at: datetime
```

### 2.3 Document Ingest (Enhanced)

**Existing Endpoints (Enhanced):**

```python
# POST /api/ingest/file
Headers: Authorization: Bearer <token>
FormData:
  - file: <PDF or text file>
  - organization: "Ontario"
  - subject: "Traffic Law"
  - matter_id: "<optional>"
Response: {
  "doc_id": "...",
  "chunks": 1247,
  "source_name": "ticket.pdf"
}

# POST /api/ingest/image
Headers: Authorization: Bearer <token>
FormData:
  - file: <image file>
  - matter_id: "<optional>"
Response: {
  "doc_id": "...",
  "chunks": 45,
  "source_name": "ticket_image.jpg",
  "parsed_ticket": {
    "offence_code": "...",
    "offence_description": "...",
    "fine_amount": 150.00,
    "demerit_points": 3,
    "court_date": "2024-03-15",
    "court_location": "...",
    "pay_instructions": "..."
  }
}
```

**New Feature: Ticket Parsing**

Create `backend/app/services/ticket_parser.py`:

```python
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class ParsedTicket:
    offence_code: Optional[str] = None
    offence_description: Optional[str] = None
    fine_amount: Optional[float] = None
    demerit_points: Optional[int] = None
    court_date: Optional[str] = None
    court_time: Optional[str] = None
    court_location: Optional[str] = None
    pay_instructions: Optional[str] = None
    jurisdiction: Optional[str] = None

def parse_ticket(text: str, jurisdiction: Optional[str] = None) -> ParsedTicket:
    """
    Parse ticket/summons text to extract structured information.
    Uses regex patterns and keyword matching.
    """
    # Implementation: regex patterns for common ticket formats
    # Look for: offence codes, amounts, dates, locations
    pass
```

### 2.4 Enhanced Query Endpoint

**Updated: POST /api/query/answer**

```python
# POST /api/query/answer
Headers: Authorization: Bearer <token>
Body: {
  "question": "What are my options for this ticket?",
  "top_k": 10,
  "matter_id": "<optional - links to ticket>",
  "language": "en",  # Optional, defaults to user preference
  "country": "CA"    # Optional, defaults to user preference
}
Query Params:
  - hybrid: true
  - include_parent: true

Response: {
  "answer": "Based on your ticket...",
  "sources": [...],
  "parsed_ticket": {  # If matter_id provided
    "offence_code": "...",
    ...
  }
}
```

**Backend Processing:**
1. Get user language/country from body or user profile
2. Embed question
3. Retrieve top-K chunks from vector store
4. If `matter_id` provided, fetch parsed ticket data
5. Build prompt with:
   - System: `LEGAL_ASSISTANT_SYSTEM_PROMPT`
   - User message includes:
     - Language and country
     - Question
     - Parsed ticket JSON (if available)
     - Retrieved document chunks
6. Call OpenAI ChatCompletion
7. Return answer + sources

### 2.5 Lawyer Listing Endpoint

**New Endpoint:**

```python
# GET /api/lawyers
Query Params:
  - jurisdiction: "CA-ON" (optional)
Response: {
  "lawyers": [
    {
      "name": "John Doe",
      "city": "Toronto",
      "website": "https://...",
      "type": "lawyer"  # or "paralegal"
    },
    ...
  ]
}
```

**Implementation:**
- For MVP: Return static JSON or empty list
- For production: Integrate with law society APIs
- **Never make up lawyer names**

### 2.6 Safety Requirements

**Critical Rules:**
- ❌ Never hardcode payment URLs
- ❌ Never generate payment links
- ✅ Only echo payment sites from ticket text or official docs
- ✅ Always include disclaimer in responses
- ✅ Never guarantee outcomes

---

## 3. Frontend Requirements

### 3.1 Theme & Visual Style

**Color Scheme:**
```scss
$primary-color: #0B1F3B;  // Deep navy
$accent-color: #00BCD4;   // Teal/electric blue
$background: #F5F5F5;     // Light grey
$text-primary: #212121;   // Dark grey
```

**Typography:**
- Headings: Semi-bold, clean
- Body: Regular weight
- Legal-tech professional feel

### 3.2 Auth Login Screen

**Route:** `/login`

**Component:** `LoginComponent`

**Features:**
- Centered card layout
- App logo/title: "weknowrights.CA"
- Email + password fields
- Login button
- Error message display
- On success → redirect to `/welcome`

**API Call:**
```typescript
POST /api/auth/login
Body: { email, password }
```

### 3.3 Language & Country Selection

**Route:** `/welcome`

**Component:** `WelcomeComponent`

**Features:**
- Greeting: "Welcome to your Legal AI assistant"
- Grid/list of language options with country flags:

| Flag | Language | Code |
|------|----------|------|
| 🇨🇦 | English (Canada) | en-CA |
| 🇫🇷 | Français | fr-CA |
| 🇮🇳 | हिन्दी | hi |
| 🇨🇦 | ਪੰਜਾਬੀ (Punjabi) | pa |
| 🇪🇸 | Español | es |
| 🇮🇳 | தமிழ் (Tamil) | ta |
| 🇨🇳 | 中文 | zh |

- Each option is a Material card/button
- On click:
  - Save preferences via `POST /api/user/preferences`
  - Navigate to `/chat`

### 3.4 Chat Interface (Enhanced)

**Route:** `/chat`

**Component:** `ChatComponent` (enhanced)

**Layout:**
- **Desktop:** Two-column
  - Left: Chat area (full width on mobile)
  - Right: Actions panel
- **Mobile:** Single column with floating upload button

**Chat Area:**
- Greeting message at top:
  - "Hi, I am your Legal AI. I can help you understand your ticket, summons, or legal document."
- Conversation history
- Message bubbles (user/assistant)
- Source citations display
- Input box at bottom:
  - Placeholder: "Ask me anything about your ticket, summons, or legal document…"

**Actions Panel (Desktop):**
- Upload buttons:
  - "Upload PDF / Document"
  - "Upload Image of Ticket"
  - "Use Camera" (mobile only)
- Case summary card (when ticket parsed):
  - Offence
  - Demerit points
  - Fine amount
  - Court date/time
  - Jurisdiction

### 3.5 Upload Integration

**Enhanced Upload Component:**

**Features:**
- Drag-and-drop
- File selection
- Camera capture (mobile):
  ```html
  <input type="file" accept="image/*" capture="environment">
  ```
- Progress indicator
- Success confirmation
- After ticket upload:
  - Show mini summary card
  - Suggest: "Ask me: 'What are my options?'"

**API Integration:**
- PDF/text → `POST /api/ingest/file`
- Images → `POST /api/ingest/image`

### 3.6 Structured Answer Rendering

**Format AI responses with sections:**

```html
<div class="answer-sections">
  <h3>Offence & Demerit Points</h3>
  <p>...</p>
  
  <h3>Consequences</h3>
  <ul>...</ul>
  
  <h3>Option 1 – Fight / Appeal</h3>
  <p>...</p>
  
  <h3>Option 2 – Pay the Fine</h3>
  <p>...</p>
  
  <div class="disclaimer-box">
    <p>This tool provides general legal information, not legal advice...</p>
  </div>
</div>
```

**Styling:**
- Section headings: Bold, larger font
- Bullet points: Clean list styling
- Disclaimer: Subtle box at bottom

### 3.7 Lawyer/Paralegal List Section

**Component:** Collapsible section in chat or side panel

**Features:**
- Title: "Find a legal professional"
- If data available (from `/api/lawyers`):
  - List: Name, City, Website link
- If no data:
  - "To find a licensed lawyer or paralegal, use the official law society or bar association directory for your province/state."

### 3.8 Responsive Design

**Breakpoints:**
- Desktop (> 1024px): Two-column layout
- Tablet (768-1024px): Stacked layout
- Mobile (< 768px): Single column, floating buttons

### 3.9 Navigation

**Routes:**
- `/login` → Login page
- `/welcome` → Language selection
- `/chat` → Main chatbot (default)
- `/upload` → Standalone upload page
- `/documents` → Document library
- `/analytics` → Analytics dashboard

**Top Navigation:**
- Left: App logo/title
- Right: Icons/links:
  - Chat
  - Upload
  - Documents
  - Analytics
  - User avatar / language flag

---

## 4. Full UX Flow

### Flow Diagram

```
1. User opens app
   ↓
2. /login (if not authenticated)
   ↓
3. /welcome (language selection)
   ↓
4. /chat (main interface)
   ├─ Upload ticket/document
   ├─ Ask questions
   ├─ Get structured answers (FIGHT vs PAY)
   └─ View lawyer list
```

### Detailed Flow

**Step 1: Login**
- User enters email/password
- Backend validates → returns JWT token
- Frontend stores token
- Redirect to `/welcome`

**Step 2: Language Selection**
- Display language options with flags
- User selects language + country
- Save via `POST /api/user/preferences`
- Redirect to `/chat`

**Step 3: Chat Interface**
- Show greeting message
- User can:
  - Type questions
  - Upload documents (PDF, images)
  - Use camera (mobile)

**Step 4: Document Upload**
- User uploads ticket image
- Backend:
  - Runs OCR
  - Parses ticket data
  - Indexes document
- Frontend:
  - Shows "Ticket uploaded" confirmation
  - Displays parsed ticket summary
  - Suggests: "Ask me: 'What are my options?'"

**Step 5: Question & Answer**
- User asks: "What are my options?"
- Backend:
  - Retrieves relevant legal documents
  - Includes parsed ticket data
  - Calls LLM with `LEGAL_ASSISTANT_SYSTEM_PROMPT`
  - Returns structured answer
- Frontend:
  - Displays answer with sections:
    - Offence & Demerit Points
    - Consequences
    - Option 1: Fight
    - Option 2: Pay
  - Shows source citations
  - Displays disclaimer

**Step 6: Lawyer List (Optional)**
- User clicks "Find a legal professional"
- Frontend calls `GET /api/lawyers?jurisdiction=CA-ON`
- Displays list or fallback message

---

## 5. API Endpoints Reference

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | No | User login |
| GET | `/api/auth/me` | Yes | Get current user |

### User Preferences

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/user/preferences` | Yes | Update language/country |

### Document Ingestion

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/ingest/file` | Yes | Upload PDF/text |
| POST | `/api/ingest/image` | Yes | Upload image (OCR) |
| POST | `/api/ingest/text` | Yes | Upload text directly |

### Query

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/query/answer` | Yes | Get AI answer |
| POST | `/api/query/search` | Yes | Search documents |

### Lawyers

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/lawyers` | Yes | Get lawyer list |

### Documents

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/documents` | Yes | List documents |
| DELETE | `/api/documents/{id}` | Yes | Delete document |

### Analytics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/analytics/summary` | Yes | Get analytics |
| POST | `/api/analytics/feedback` | Yes | Submit feedback |

---

## 6. Implementation Priority

### Phase 1: Core Functionality (MVP)
1. ✅ System prompt updated
2. ⬜ Basic auth (simple token-based)
3. ⬜ Language preferences endpoint
4. ⬜ Enhanced query endpoint with language support
5. ⬜ Frontend login page
6. ⬜ Frontend language selection
7. ⬜ Enhanced chat with structured answers

### Phase 2: Ticket Parsing
1. ⬜ Ticket parser service
2. ⬜ OCR integration for images
3. ⬜ Parsed ticket data in query responses
4. ⬜ Frontend ticket summary display

### Phase 3: Advanced Features
1. ⬜ Lawyer listing endpoint
2. ⬜ Frontend lawyer list component
3. ⬜ Enhanced analytics
4. ⬜ Matter/case management

---

## 7. Security Checklist

- ✅ API keys never in frontend
- ✅ JWT tokens for authentication
- ✅ User data isolation
- ✅ Input validation
- ✅ Error handling (no sensitive data exposure)
- ✅ CORS configuration
- ✅ Rate limiting (future)

---

## 8. Testing Checklist

- [ ] Login flow works
- [ ] Language selection saves preferences
- [ ] Chat interface displays correctly
- [ ] Document upload works (PDF, images)
- [ ] Ticket parsing extracts correct data
- [ ] Query returns structured answers
- [ ] FIGHT vs PAY options displayed
- [ ] Disclaimers shown
- [ ] Lawyer list displays (or fallback)
- [ ] Responsive design works on mobile
- [ ] Error handling works

---

## 9. Next Steps

1. **Backend:**
   - Implement auth endpoints
   - Add language preferences
   - Create ticket parser
   - Enhance query endpoint

2. **Frontend:**
   - Create login component
   - Create welcome/language selection
   - Enhance chat component
   - Add structured answer rendering

3. **Integration:**
   - Test full flow
   - Verify API connections
   - Test on mobile devices

---

**This guide provides the complete blueprint for implementing the legal assistant system. Follow the phases in order for best results.**


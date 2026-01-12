# Legal Assistant API Integration Guide

## Overview

This guide provides comprehensive documentation for the end-to-end legal assistant application with integrated third-party legal APIs, chat history management, multilingual support, and role-based access control (RBAC).

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [API Integrations](#api-integrations)
4. [Setup Instructions](#setup-instructions)
5. [API Endpoints](#api-endpoints)
6. [Frontend Components](#frontend-components)
7. [RBAC System](#rbac-system)
8. [Chat History](#chat-history)
9. [Translation Service](#translation-service)
10. [Testing](#testing)

---

## Features

### ✅ Implemented Features

1. **Legal API Integrations**
   - Case Lookup (CaseText, LexisNexis, Westlaw)
   - Amendment Generation (LegalZoom)
   - Statute Search
   - Mock data available when API keys not configured

2. **Chat History Management**
   - Save chat messages with metadata
   - Search through chat history
   - Session management
   - Support for MongoDB, Firebase, and local storage

3. **Multilingual Support**
   - Translation API integration (Google Translate)
   - 30+ languages supported
   - Automatic language detection
   - Mock translation when API not configured

4. **Role-Based Access Control (RBAC)**
   - 4 user roles: Guest, Standard, Premium, Admin
   - Permission-based API access
   - JWT token authentication
   - Usage limits per role

5. **Frontend UI Components**
   - Case Lookup Modal
   - Amendment Generator Modal
   - Chat History Search Modal
   - Integrated with existing chat interface

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ CaseLookup   │  │ Amendment    │  │ ChatHistory  │     │
│  │ Component    │  │ Generator    │  │ Search       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  API Endpoints                        │  │
│  │  • /api/legal/case-lookup                           │  │
│  │  • /api/legal/generate-amendment                    │  │
│  │  • /api/legal/search-statutes                       │  │
│  │  • /api/translate                                   │  │
│  │  • /api/chat-history/*                              │  │
│  │  • /api/auth/*                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Service Layer                            │  │
│  │  ┌─────────────────┐  ┌─────────────────┐           │  │
│  │  │ Legal API       │  │ Translation     │           │  │
│  │  │ Integrations    │  │ Service         │           │  │
│  │  └─────────────────┘  └─────────────────┘           │  │
│  │  ┌─────────────────┐  ┌─────────────────┐           │  │
│  │  │ Chat History    │  │ RBAC            │           │  │
│  │  │ Service         │  │ Service         │           │  │
│  │  └─────────────────┘  └─────────────────┘           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services & Storage                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ CaseText API │  │ LegalZoom API│  │ Google       │     │
│  │ LexisNexis   │  │ Westlaw API  │  │ Translate    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ MongoDB      │  │ Firebase     │  │ Local JSON   │     │
│  │ (Optional)   │  │ (Optional)   │  │ Storage      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## API Integrations

### 1. Case Lookup APIs

#### CaseText API
- **Purpose**: Search legal cases by name, citation, or keywords
- **Features**: Jurisdiction filtering, year range, relevance scoring
- **Configuration**: Set `CASETEXT_API_KEY` in environment

#### LexisNexis API
- **Purpose**: Comprehensive legal case database
- **Features**: Advanced search, document retrieval
- **Configuration**: Set `LEXISNEXIS_API_KEY` in environment

#### Westlaw API
- **Purpose**: Legal research and case law
- **Features**: Citation lookup, headnotes
- **Configuration**: Set `WESTLAW_API_KEY` in environment

### 2. Amendment Generation

#### LegalZoom API
- **Purpose**: Generate legal document amendments
- **Supported Documents**: Contracts, wills, trusts, agreements
- **Configuration**: Set `LEGALZOOM_API_KEY` in environment

### 3. Translation API

#### Google Cloud Translation
- **Purpose**: Translate text between 30+ languages
- **Features**: Auto-detection, batch translation
- **Configuration**: Set `GOOGLE_TRANSLATE_API_KEY` in environment

---

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies

```bash
cd legal-bot/backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# OpenAI (Required for chat)
OPENAI_API_KEY=your_openai_api_key_here

# Legal APIs (Optional - mock data used if not configured)
CASETEXT_API_KEY=your_casetext_api_key
LEGALZOOM_API_KEY=your_legalzoom_api_key
LEXISNEXIS_API_KEY=your_lexisnexis_api_key
WESTLAW_API_KEY=your_westlaw_api_key

# Translation API (Optional)
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key
GOOGLE_CLOUD_PROJECT_ID=your_project_id

# Chat History Storage (Optional)
MONGODB_URI=mongodb://localhost:27017/
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# JWT Secret (Required for RBAC)
JWT_SECRET_KEY=your-secret-key-change-in-production

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### Start Backend Server

```bash
cd legal-bot/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

#### Install Dependencies

```bash
cd legal-bot/frontend
npm install
```

#### Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## API Endpoints

### Legal API Endpoints

#### 1. Case Lookup

**POST** `/api/legal/case-lookup`

Search for legal cases using integrated APIs.

**Request Body:**
```json
{
  "query": "Miranda v. Arizona",
  "jurisdiction": "US",
  "year_from": 1960,
  "year_to": 2024,
  "limit": 10
}
```

**Response:**
```json
{
  "success": true,
  "source": "CaseText",
  "results": [
    {
      "case_name": "Miranda v. Arizona",
      "citation": "384 U.S. 436 (1966)",
      "court": "Supreme Court of the United States",
      "year": 1966,
      "jurisdiction": "US",
      "summary": "Landmark case establishing Miranda rights...",
      "relevance_score": 0.95,
      "url": "https://..."
    }
  ],
  "total": 1
}
```

**RBAC**: Requires `PREMIUM` role or higher

#### 2. Generate Amendment

**POST** `/api/legal/generate-amendment`

Generate legal document amendments.

**Request Body:**
```json
{
  "document_type": "divorce",
  "case_details": {
    "amendment_text": "Change custody arrangement to joint custody",
    "party_a": "John Doe",
    "party_b": "Jane Doe",
    "effective_date": "2024-02-01"
  },
  "jurisdiction": "US-CA"
}
```

**Response:**
```json
{
  "success": true,
  "source": "LegalZoom",
  "document_id": "doc_12345",
  "content": "LEGAL AMENDMENT...",
  "download_url": "https://..."
}
```

**RBAC**: Requires `PREMIUM` role or higher

#### 3. Search Statutes

**POST** `/api/legal/search-statutes`

Search for statutes and regulations.

**Query Parameters:**
- `query`: Search query
- `jurisdiction`: Legal jurisdiction (default: "US")
- `law_type`: Type of law (optional)

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "title": "18 U.S.C. § 1001 - False Statements",
      "jurisdiction": "US",
      "type": "Criminal",
      "text": "Whoever, in any matter...",
      "effective_date": "1948-06-25",
      "url": "https://..."
    }
  ]
}
```

**RBAC**: Requires `STANDARD` role or higher

### Translation Endpoints

#### 1. Translate Text

**POST** `/api/translate`

Translate text to target language.

**Request Body:**
```json
{
  "text": "Hello, how can I help you?",
  "target_language": "es",
  "source_language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "translated_text": "Hola, ¿cómo puedo ayudarte?",
  "source_language": "en",
  "target_language": "es",
  "service": "Google Cloud Translation"
}
```

**RBAC**: Requires `STANDARD` role or higher

#### 2. Get Supported Languages

**GET** `/api/translate/languages`

Get list of supported languages.

**Response:**
```json
{
  "languages": {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    ...
  }
}
```

### Chat History Endpoints

#### 1. Save Message

**POST** `/api/chat-history/save`

Save a chat message to history.

**Request Body:**
```json
{
  "user_id": "user_123",
  "session_id": "session_456",
  "message": "What are my rights?",
  "response": "You have the right to...",
  "metadata": {
    "law_category": "Criminal Law",
    "jurisdiction": "US-CA"
  }
}
```

#### 2. Get Session History

**GET** `/api/chat-history/session/{user_id}/{session_id}`

Get all messages from a specific session.

**Query Parameters:**
- `limit`: Maximum number of messages (default: 50)

#### 3. Get User Sessions

**GET** `/api/chat-history/sessions/{user_id}`

Get all chat sessions for a user.

**Query Parameters:**
- `limit`: Maximum number of sessions (default: 20)

#### 4. Search Chat History

**POST** `/api/chat-history/search`

Search through chat history.

**Request Body:**
```json
{
  "user_id": "user_123",
  "search_query": "Miranda rights",
  "limit": 20
}
```

#### 5. Delete Session

**DELETE** `/api/chat-history/session/{user_id}/{session_id}`

Delete a chat session and all its messages.

### Authentication Endpoints

#### 1. Generate Token

**POST** `/api/auth/token`

Generate JWT authentication token.

**Query Parameters:**
- `user_id`: User identifier
- `role`: User role (guest, standard, premium, admin)

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "role": "standard",
  "permissions": ["chat:basic", "chat:advanced", ...],
  "limits": {
    "daily_messages": 100,
    "document_uploads": 5,
    "api_calls": 10
  }
}
```

#### 2. Verify Token

**GET** `/api/auth/verify`

Verify authentication token.

**Headers:**
- `Authorization`: Bearer {token}

#### 3. Check API Access

**GET** `/api/auth/check-access`

Check if user has access to a specific API.

**Query Parameters:**
- `api_name`: API name (case_lookup, amendment_generation, etc.)

**Headers:**
- `Authorization`: Bearer {token} (optional)

---

## Frontend Components

### 1. CaseLookup Component

**Location**: `frontend/src/components/CaseLookup.jsx`

**Features**:
- Search legal cases by query
- Filter by jurisdiction and year range
- Display case details with relevance scores
- Click to view full case or insert into chat

**Usage**:
```jsx
<CaseLookup 
  onClose={() => setShowCaseLookup(false)}
  onCaseSelected={(caseItem) => {
    // Handle case selection
  }}
/>
```

### 2. AmendmentGenerator Component

**Location**: `frontend/src/components/AmendmentGenerator.jsx`

**Features**:
- Select document type based on law category
- Enter amendment details and party information
- Generate legal amendments
- Copy or download generated documents

**Usage**:
```jsx
<AmendmentGenerator 
  onClose={() => setShowAmendmentGenerator(false)}
  lawCategory="Family Law"
/>
```

### 3. ChatHistorySearch Component

**Location**: `frontend/src/components/ChatHistorySearch.jsx`

**Features**:
- View all chat sessions
- Search through chat history
- Load previous conversations
- Delete old sessions

**Usage**:
```jsx
<ChatHistorySearch 
  userId="user_123"
  onClose={() => setShowChatHistory(false)}
  onMessageSelect={(message) => {
    // Handle message selection
  }}
/>
```

---

## RBAC System

### User Roles

#### 1. Guest
- **Permissions**: Basic chat only
- **Limits**: 10 messages/day, no document uploads
- **API Access**: None

#### 2. Standard
- **Permissions**: Advanced chat, document upload, translation
- **Limits**: 100 messages/day, 5 document uploads, 10 API calls
- **API Access**: Translation, basic search

#### 3. Premium
- **Permissions**: All features
- **Limits**: Unlimited
- **API Access**: All APIs (case lookup, amendments, statutes)

#### 4. Admin
- **Permissions**: All features + admin controls
- **Limits**: Unlimited
- **API Access**: All APIs + admin endpoints

### Permission Checks

All protected endpoints check user permissions:

```python
# Backend example
from app.services.rbac_service import get_rbac_service, UserRole

rbac = get_rbac_service()
user_role = UserRole.STANDARD

# Check API access
access_check = rbac.can_use_api(user_role, "case_lookup")
if not access_check["has_access"]:
    return {"error": "Access denied", "upgrade_info": ...}
```

---

## Chat History

### Storage Options

#### 1. Local Storage (Default)
- Files stored in `backend/data/chat_history/`
- One JSON file per user
- No external dependencies

#### 2. MongoDB
- Scalable document database
- Full-text search support
- Set `MONGODB_URI` in environment

#### 3. Firebase
- Cloud-based storage
- Real-time sync
- Set `FIREBASE_CREDENTIALS_PATH` in environment

### Automatic Saving

Chat messages are automatically saved after each interaction:

```javascript
// Frontend - automatically called after chat response
await fetch(`${API_URL}/api/chat-history/save`, {
  method: 'POST',
  body: JSON.stringify({
    user_id: userId,
    session_id: sessionId,
    message: question,
    response: answer,
    metadata: { law_category, jurisdiction, ... }
  })
});
```

---

## Translation Service

### Supported Languages

The system supports 30+ languages including:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Hindi (hi)
- Punjabi (pa)
- Chinese (zh)
- Arabic (ar)
- And many more...

### Usage Example

```python
from app.services.translation_service import get_translation_service

translation_service = get_translation_service()

# Translate text
result = await translation_service.translate_text(
    text="Hello, how can I help you?",
    target_language="es",
    source_language="en"
)

print(result["translated_text"])  # "Hola, ¿cómo puedo ayudarte?"
```

---

## Testing

### Backend Testing

#### Test Case Lookup

```bash
curl -X POST http://localhost:8000/api/legal/case-lookup \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Miranda v. Arizona",
    "jurisdiction": "US",
    "limit": 5
  }'
```

#### Test Amendment Generation

```bash
curl -X POST http://localhost:8000/api/legal/generate-amendment \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "contract",
    "case_details": {
      "amendment_text": "Change payment terms to net 60 days"
    },
    "jurisdiction": "US"
  }'
```

#### Test Translation

```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "target_language": "es"
  }'
```

#### Test Chat History

```bash
# Save message
curl -X POST http://localhost:8000/api/chat-history/save \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "session_id": "test_session",
    "message": "What are my rights?",
    "response": "You have the right to remain silent..."
  }'

# Search history
curl -X POST http://localhost:8000/api/chat-history/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "search_query": "rights",
    "limit": 10
  }'
```

#### Test RBAC

```bash
# Generate token
curl -X POST "http://localhost:8000/api/auth/token?user_id=test_user&role=premium"

# Verify token
curl -X GET http://localhost:8000/api/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Check API access
curl -X GET "http://localhost:8000/api/auth/check-access?api_name=case_lookup" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Frontend Testing

1. **Start the application**:
   ```bash
   # Terminal 1 - Backend
   cd legal-bot/backend
   python -m uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd legal-bot/frontend
   npm run dev
   ```

2. **Test Case Lookup**:
   - Click "🔍 Case Lookup" button
   - Enter search query: "Miranda v. Arizona"
   - Select jurisdiction: "United States"
   - Click "Search Cases"
   - Verify results are displayed

3. **Test Amendment Generator**:
   - Click "📝 Amendments" button
   - Select document type
   - Enter amendment details
   - Click "Generate Amendment"
   - Verify document is generated
   - Test copy and download buttons

4. **Test Chat History**:
   - Have a few chat conversations
   - Click "💬 History" button
   - Verify sessions are listed
   - Test search functionality
   - Test session deletion

---

## Troubleshooting

### Common Issues

#### 1. API Keys Not Working

**Problem**: Getting mock data instead of real API responses

**Solution**: 
- Verify API keys are set in `.env` file
- Restart backend server after adding keys
- Check API key validity with provider

#### 2. Chat History Not Saving

**Problem**: Chat history search returns empty results

**Solution**:
- Check backend logs for errors
- Verify storage directory exists: `backend/data/chat_history/`
- For MongoDB/Firebase: verify connection string

#### 3. RBAC Access Denied

**Problem**: Getting "Access denied" errors

**Solution**:
- Generate a token with appropriate role
- Include token in Authorization header
- Check role permissions in `rbac_service.py`

#### 4. Translation Not Working

**Problem**: Getting mock translations

**Solution**:
- Set `GOOGLE_TRANSLATE_API_KEY` in environment
- Enable Google Cloud Translation API in Google Cloud Console
- Verify billing is enabled for your project

---

## Production Deployment

### Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Use HTTPS for all API calls
- [ ] Enable CORS only for trusted domains
- [ ] Store API keys in secure environment variables
- [ ] Implement rate limiting
- [ ] Enable logging and monitoring
- [ ] Set up database backups (for MongoDB/Firebase)
- [ ] Use production-grade web server (Gunicorn/Nginx)

### Environment Variables for Production

```env
# Production settings
DEBUG=False
JWT_SECRET_KEY=<strong-random-secret>
ALLOWED_ORIGINS=https://yourdomain.com

# API Keys (from secure vault)
OPENAI_API_KEY=<from-vault>
CASETEXT_API_KEY=<from-vault>
LEGALZOOM_API_KEY=<from-vault>
GOOGLE_TRANSLATE_API_KEY=<from-vault>

# Database (production)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
```

---

## Support and Resources

### API Provider Documentation

- **CaseText**: https://casetext.com/api-docs
- **LegalZoom**: https://www.legalzoom.com/api
- **LexisNexis**: https://www.lexisnexis.com/api
- **Google Translate**: https://cloud.google.com/translate/docs

### Legal Disclaimer

⚠️ **Important**: This system provides general legal information only and is not a substitute for professional legal advice. Users should always consult with a licensed attorney for advice about their specific legal situation.

---

## License

This project is provided as-is for educational and demonstration purposes.

---

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Tests are included for new features
- Documentation is updated
- Security best practices are followed

---

**Last Updated**: January 2026
**Version**: 1.0.0

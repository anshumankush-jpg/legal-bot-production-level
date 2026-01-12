# 🚀 PLAZA-AI Legal Assistant - Working Features Guide

## ✅ What Actually Works (January 2026)

This guide documents **ONLY the features that are actually implemented and working** in the system.

---

## 🎯 Core Features

### 1. **Multi-Language Support** 🌐
- English 🇬🇧
- French 🇫🇷
- Spanish 🇪🇸
- Hindi 🇮🇳
- Punjabi 🇮🇳
- Chinese 🇨🇳
- Tamil 🇮🇳

**How it works:** User selects language during onboarding, all responses are in that language.

---

### 2. **Law Type Categorization** ⚖️

The system supports **14 specialized law types**:

1. **Constitutional Law** - Charter rights, constitutional challenges
2. **Criminal Law** - Criminal charges, arrests, trials, defenses
3. **Traffic Law** - Traffic tickets, speeding, DUI, license issues
4. **Business Litigation** - Commercial disputes, breach of contract
5. **Business Law** - Incorporation, contracts, M&A, franchising
6. **Family Law** - Divorce, custody, support, property division
7. **Employment Law** - Wrongful dismissal, harassment, discrimination
8. **Immigration Law** - Visas, work permits, citizenship, refugee claims
9. **Real Estate Law** - Property transactions, landlord-tenant disputes
10. **Civil Law** - Civil lawsuits, personal injury, negligence
11. **Administrative Law** - Government decisions, tribunals, appeals
12. **Tax Law** - Income tax, corporate tax, CRA/IRS disputes
13. **Wills, Estates, and Trusts** - Estate planning, probate, powers of attorney
14. **Health Law** - Medical malpractice, patient rights, healthcare compliance

**How it works:** User selects law type, system provides context-specific guidance.

---

### 3. **Document Upload & Processing** 📄

**Supported File Types:**
- PDF documents
- DOCX (Word documents)
- TXT (Text files)
- XLSX/XLS (Excel files)
- Images: JPG, JPEG, PNG, BMP, TIFF (with OCR)

**Features:**
- ✅ Drag & drop upload
- ✅ File picker upload
- ✅ Automatic text extraction
- ✅ OCR for images (Tesseract)
- ✅ Automatic offense number detection
- ✅ Chunking and indexing
- ✅ Vector embeddings (FAISS)

**API Endpoint:** `POST /api/artillery/upload`

**Example:**
```javascript
const formData = new FormData();
formData.append('file', file);
formData.append('user_id', 'user123');
formData.append('offence_number', 'HTA 128'); // Optional

fetch('http://localhost:8000/api/artillery/upload', {
  method: 'POST',
  body: formData
});
```

---

### 4. **RAG-Based Chat System** 💬

**Features:**
- ✅ Context-aware responses using uploaded documents
- ✅ Vector similarity search (FAISS)
- ✅ OpenAI GPT for answer generation
- ✅ Citation tracking
- ✅ Confidence scoring
- ✅ Multi-language responses

**API Endpoint:** `POST /api/artillery/chat`

**Request:**
```json
{
  "message": "What are the penalties for speeding 30 km/h over?",
  "offence_number": "HTA 128",
  "province": "Ontario",
  "country": "CA",
  "language": "en",
  "law_category": "Traffic Law",
  "law_type": "Traffic Law",
  "law_scope": "Provincial",
  "jurisdiction": "Canada - Ontario",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "Based on Ontario's Highway Traffic Act...",
  "citations": [
    {
      "text": "Section 128 of the HTA states...",
      "source": "HTA_Ontario.pdf",
      "page": 45,
      "score": 0.92
    }
  ],
  "chunks_used": 5,
  "confidence": 0.85
}
```

---

### 5. **Voice Chat** 🎤

**Features:**
- ✅ Speech-to-Text (OpenAI Whisper)
- ✅ Text-to-Speech (OpenAI TTS)
- ✅ Multi-language support
- ✅ Voice selection per language

**API Endpoints:**

**Transcribe Audio:**
```
POST /api/voice/transcribe
Content-Type: multipart/form-data
Body: audio file (webm, mp3, wav)

Response: { "text": "transcribed text" }
```

**Text-to-Speech:**
```
POST /api/voice/speak
Content-Type: application/json
Body: {
  "text": "Text to speak",
  "language": "en",
  "voice": "alloy"
}

Response: audio/mpeg stream
```

**Voice Mapping:**
- English: `alloy`
- Hindi: `nova`
- French: `shimmer`
- Spanish: `fable`
- Punjabi: `onyx`
- Chinese: `echo`

---

### 6. **Document Management** 📚

**Features:**
- ✅ List all uploaded documents
- ✅ View document metadata
- ✅ Delete documents
- ✅ Track chunk count per document

**API Endpoints:**

**List Documents:**
```
GET /api/artillery/documents?user_id=user123

Response: {
  "documents": [
    {
      "doc_id": "doc_user123_abc123",
      "filename": "traffic_ticket.pdf",
      "chunks_count": 15,
      "offence_number": "HTA 128"
    }
  ],
  "total": 1
}
```

**Delete Document:**
```
DELETE /api/artillery/documents/doc_user123_abc123?user_id=user123

Response: {
  "status": "success",
  "doc_id": "doc_user123_abc123",
  "chunks_deleted": 15,
  "message": "Document marked for deletion"
}
```

---

### 7. **Recent Legal Updates** 📰

**Features:**
- ✅ Fetch recent legal updates by law type and jurisdiction
- ✅ Display in sidebar
- ✅ Clickable links to official sources

**API Endpoint:**
```
POST /api/artillery/recent-updates
Content-Type: application/json
Body: {
  "law_type": "Traffic Law",
  "jurisdiction": "Ontario"
}

Response: {
  "updates": [
    {
      "title": "New Speed Limit Changes in Ontario",
      "date": "2026-01-05",
      "source": "Ontario Ministry of Transportation",
      "url": "https://www.ontario.ca/..."
    }
  ]
}
```

---

### 8. **Government Resources** 🏛️

**Features:**
- ✅ Official government links by law type and province
- ✅ Court information
- ✅ Legal aid resources
- ✅ Official forms and guides

**API Endpoint:**
```
GET /api/artillery/government-resources?law_type=Traffic%20Law&province=ON

Response: {
  "law_type": "Traffic Law",
  "province": "ON",
  "resources": [
    {
      "name": "Ontario Courts - Traffic Tickets",
      "url": "https://www.ontariocourts.ca/...",
      "description": "Official court information"
    }
  ]
}
```

---

### 9. **Vector Search** 🔍

**Features:**
- ✅ Semantic search across uploaded documents
- ✅ Similarity scoring
- ✅ Metadata filtering
- ✅ Score threshold filtering

**API Endpoint:**
```
POST /api/artillery/search
Content-Type: application/json
Body: {
  "query": "What are the penalties for DUI?",
  "k": 10,
  "filters": {},
  "score_threshold": 0.7
}

Response: {
  "results": [
    {
      "score": 0.92,
      "content": "Section 320.14 of the Criminal Code...",
      "metadata": {
        "filename": "criminal_code.pdf",
        "page": 234
      }
    }
  ],
  "total_found": 5,
  "query": "What are the penalties for DUI?"
}
```

---

## 🛠️ Technical Stack

### Backend (Python/FastAPI)
- **Framework:** FastAPI
- **Port:** 8000
- **Vector Store:** FAISS (local)
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2, 384 dimensions)
- **LLM:** OpenAI GPT (gpt-3.5-turbo or gpt-4)
- **OCR:** Tesseract OCR
- **Voice:** OpenAI Whisper (transcription) + OpenAI TTS (speech)

### Frontend (React/Vite)
- **Framework:** React 18
- **Build Tool:** Vite
- **Port:** 5173 (dev), 4200 (alternative)
- **Styling:** CSS Modules
- **State Management:** React Hooks (useState, useEffect)

---

## 📋 API Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/artillery/health` | GET | Artillery system health |
| `/api/artillery/upload` | POST | Upload documents/images |
| `/api/artillery/chat` | POST | Chat with RAG |
| `/api/artillery/search` | POST | Vector search |
| `/api/artillery/documents` | GET | List documents |
| `/api/artillery/documents/{doc_id}` | DELETE | Delete document |
| `/api/artillery/recent-updates` | POST | Get legal updates |
| `/api/artillery/government-resources` | GET | Get gov resources |
| `/api/voice/transcribe` | POST | Speech-to-text |
| `/api/voice/speak` | POST | Text-to-speech |

---

## 🚀 How to Run

### Backend
```bash
cd legal-bot/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd legal-bot/frontend
npm install
npm run dev
```

### Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔑 Required Configuration

### Environment Variables (backend/.env)
```env
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
OPENAI_CHAT_MODEL=gpt-3.5-turbo
EMBEDDING_PROVIDER=sentence_transformers
```

### Tesseract OCR (for image processing)
- **Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Install to:** `C:\Program Files\Tesseract-OCR\`

---

## ❌ Features NOT Implemented

These features are documented but **NOT actually working**:

- ❌ User authentication/login
- ❌ User profile management
- ❌ Analytics dashboard
- ❌ Lawyer directory
- ❌ Matters/workflow system
- ❌ Feedback system
- ❌ Angular frontend components

**Note:** If you see these features in documentation, they are **planned** but not implemented.

---

## 📊 User Flow

1. **Onboarding** → Select language, country, province
2. **Law Type Selection** → Choose from 14 law types
3. **Chat Interface** → Ask questions, upload documents
4. **Document Upload** → Drag & drop or file picker
5. **Get Answers** → RAG-based responses with citations
6. **Voice Chat** (optional) → Speak questions, hear answers
7. **View Resources** → Recent updates, government links

---

## 🎯 Use Cases

### Example 1: Traffic Ticket
1. User uploads traffic ticket (PDF or image)
2. System extracts offense number (e.g., "HTA 128")
3. User asks: "What are my options for fighting this ticket?"
4. System retrieves relevant sections from uploaded documents
5. OpenAI generates answer with citations
6. User sees answer in their selected language

### Example 2: Legal Research
1. User selects "Criminal Law" as law type
2. User asks: "What is the penalty for theft under $5000?"
3. System searches vector database
4. Returns relevant Criminal Code sections
5. Provides structured answer with sources

### Example 3: Voice Consultation
1. User enables voice chat
2. User speaks: "मुझे ट्रैफिक टिकट मिला है" (Hindi)
3. System transcribes using Whisper
4. Generates answer in Hindi
5. Speaks answer using TTS

---

## 🐛 Known Limitations

1. **No User Accounts** - All data is session-based
2. **Local Storage Only** - No cloud storage (yet)
3. **Single User Mode** - No multi-user support
4. **No Authentication** - Anyone can access
5. **Limited OCR** - Requires Tesseract installation
6. **OpenAI Dependency** - Requires API key for chat and voice

---

## 📞 Support

For issues or questions:
1. Check backend logs: `backend_detailed.log`
2. Check browser console for frontend errors
3. Verify OpenAI API key is set
4. Ensure Tesseract is installed for OCR

---

**Last Updated:** January 9, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅

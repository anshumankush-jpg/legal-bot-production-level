# 🚀 PLAZA-AI Legal Assistant - Quick Start Guide

## ⚠️ IMPORTANT: Read This First!

This project has **extensive documentation**, but much of it describes **planned features** that are not yet implemented. 

**To see what actually works right now, read:**
- ✅ **[WORKING_FEATURES_GUIDE.md](./WORKING_FEATURES_GUIDE.md)** - Complete guide to working features
- ✅ **[BACKEND_FRONTEND_ALIGNMENT.md](./BACKEND_FRONTEND_ALIGNMENT.md)** - Feature alignment analysis

---

## 🎯 What This System Does

PLAZA-AI is a **legal information assistant** that:

1. ✅ Accepts uploaded legal documents (PDF, DOCX, images)
2. ✅ Extracts and indexes content using OCR and vector embeddings
3. ✅ Answers legal questions using RAG (Retrieval Augmented Generation)
4. ✅ Provides citations from uploaded documents
5. ✅ Supports 7 languages (English, French, Spanish, Hindi, Punjabi, Chinese, Tamil)
6. ✅ Covers 14 law types (Traffic, Criminal, Business, Family, etc.)
7. ✅ Includes voice chat (speech-to-text, text-to-speech)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

**Backend:**
```bash
cd legal-bot/backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd legal-bot/frontend
npm install
```

**Tesseract OCR (for image processing):**
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Install to: `C:\Program Files\Tesseract-OCR\`

---

### Step 2: Configure OpenAI API Key

Create `backend/.env`:
```env
OPENAI_API_KEY=sk-your-api-key-here
LLM_PROVIDER=openai
OPENAI_CHAT_MODEL=gpt-3.5-turbo
EMBEDDING_PROVIDER=sentence_transformers
```

Get your API key from: https://platform.openai.com/api-keys

---

### Step 3: Start Servers

**Terminal 1 - Backend:**
```bash
cd legal-bot/backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd legal-bot/frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📱 How to Use

### 1. Complete Onboarding
- Select your language (English, French, Spanish, Hindi, Punjabi, Chinese, Tamil)
- Select your country (Canada or USA)
- Select your province/state

### 2. Choose Law Type
- Select from 14 law types (Traffic Law, Criminal Law, Business Law, etc.)
- Choose jurisdiction (Federal, Provincial/State, Municipal)

### 3. Upload Documents (Optional)
- Drag & drop or click to upload
- Supported: PDF, DOCX, TXT, Images (JPG, PNG, etc.)
- System will extract text and index it

### 4. Ask Questions
- Type your legal question
- System retrieves relevant information from uploaded documents
- Provides answer with citations
- Responses in your selected language

### 5. Use Voice Chat (Optional)
- Click microphone icon
- Speak your question
- System transcribes, answers, and speaks response

---

## 🔧 Backend API Endpoints

All endpoints use base URL: `http://localhost:8000`

### Core Endpoints
- `POST /api/artillery/upload` - Upload documents/images
- `POST /api/artillery/chat` - Chat with RAG system
- `POST /api/artillery/search` - Vector similarity search
- `GET /api/artillery/documents` - List uploaded documents
- `DELETE /api/artillery/documents/{doc_id}` - Delete document

### Voice Endpoints
- `POST /api/voice/transcribe` - Speech-to-text (Whisper)
- `POST /api/voice/speak` - Text-to-speech (OpenAI TTS)

### Info Endpoints
- `POST /api/artillery/recent-updates` - Get recent legal updates
- `GET /api/artillery/government-resources` - Get government resources
- `GET /api/artillery/health` - Health check

**Full API documentation:** http://localhost:8000/docs

---

## 📊 System Architecture

```
┌─────────────────────────────────────┐
│   React Frontend (Port 5173)        │
│   - Onboarding Wizard                │
│   - Law Type Selector                │
│   - Chat Interface                   │
│   - Voice Chat                       │
│   - Document Upload                  │
└─────────────────────────────────────┘
              ↓ HTTP API
┌─────────────────────────────────────┐
│   FastAPI Backend (Port 8000)       │
│   - Artillery RAG System             │
│   - FAISS Vector Store               │
│   - Sentence Transformers            │
│   - OpenAI GPT (LLM)                 │
│   - OpenAI Whisper (STT)             │
│   - OpenAI TTS (Text-to-Speech)      │
│   - Tesseract OCR                    │
└─────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI (Python)
- **Vector Store:** FAISS (local, free)
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2, 384 dim)
- **LLM:** OpenAI GPT-3.5-turbo or GPT-4
- **OCR:** Tesseract
- **Voice:** OpenAI Whisper + TTS

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **Styling:** CSS Modules
- **State:** React Hooks

---

## ✅ Working Features

| Feature | Status | Description |
|---------|--------|-------------|
| Document Upload | ✅ | PDF, DOCX, TXT, Images |
| OCR Processing | ✅ | Extract text from images |
| RAG Chat | ✅ | Context-aware answers |
| Citations | ✅ | Source tracking |
| Multi-Language | ✅ | 7 languages |
| Voice Chat | ✅ | STT + TTS |
| Law Types | ✅ | 14 categories |
| Recent Updates | ✅ | Legal news |
| Gov Resources | ✅ | Official links |
| Document Management | ✅ | List, delete |

---

## ❌ Features NOT Implemented

These are documented but **NOT working**:

- ❌ User authentication/login
- ❌ User profiles
- ❌ Analytics dashboard
- ❌ Lawyer directory
- ❌ Matters/workflow system
- ❌ Feedback system

**If you see these in other docs, they are planned but not built.**

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Install dependencies: `pip install -r requirements.txt`
- Check OpenAI API key in `.env`

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Install dependencies: `npm install`
- Clear cache: `npm cache clean --force`

### OCR not working
- Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Verify path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Chat not responding
- Check OpenAI API key is valid
- Check backend logs: `backend_detailed.log`
- Verify backend is running on port 8000

### Voice chat not working
- Check OpenAI API key (Whisper & TTS require OpenAI)
- Check browser microphone permissions
- Check browser console for errors

---

## 📚 Documentation

### Essential Docs (Read These)
- ✅ [WORKING_FEATURES_GUIDE.md](./WORKING_FEATURES_GUIDE.md) - What actually works
- ✅ [BACKEND_FRONTEND_ALIGNMENT.md](./BACKEND_FRONTEND_ALIGNMENT.md) - Feature alignment

### Reference Docs
- [PROJECT_README.md](./PROJECT_README.md) - Original project overview
- [SERVERS_RUNNING.md](./SERVERS_RUNNING.md) - Server status info
- Backend API Docs: http://localhost:8000/docs (when running)

### Ignore These (Planned Features)
- ❌ IMPLEMENTATION_GUIDE.md - Describes unimplemented features
- ❌ README_MATTERS.md - Matters system (not implemented)
- ❌ ANGULAR_*.md - Angular frontend (not used)

---

## 🎯 Example Use Cases

### Use Case 1: Traffic Ticket
1. Upload traffic ticket (PDF or photo)
2. System extracts offense number
3. Ask: "What are my options?"
4. Get answer with relevant law sections

### Use Case 2: Legal Research
1. Select "Criminal Law"
2. Ask: "What is the penalty for theft under $5000?"
3. Get answer with Criminal Code citations

### Use Case 3: Multilingual Support
1. Select Hindi as language
2. Ask question in Hindi
3. Get response in Hindi
4. Use voice chat for hands-free

---

## 💡 Tips

1. **Upload documents first** for better answers
2. **Be specific** in your questions
3. **Include details** like dates, locations, amounts
4. **Use voice chat** for hands-free operation
5. **Check citations** to verify information
6. **Try different languages** if needed

---

## 🔐 Security Notes

- No user authentication (all data is session-based)
- No data encryption (local development only)
- OpenAI API key stored in `.env` (keep private)
- Do not expose to public internet without security

---

## 📞 Support

**Check logs:**
- Backend: `backend_detailed.log`
- Frontend: Browser console (F12)

**Common issues:**
- Port conflicts: Change ports in code
- API key errors: Check `.env` file
- OCR errors: Install Tesseract
- CORS errors: Check backend CORS config

---

## 🎉 You're Ready!

1. ✅ Read [WORKING_FEATURES_GUIDE.md](./WORKING_FEATURES_GUIDE.md)
2. ✅ Configure OpenAI API key
3. ✅ Start backend and frontend
4. ✅ Open http://localhost:5173
5. ✅ Complete onboarding
6. ✅ Start asking questions!

---

**Last Updated:** January 9, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅

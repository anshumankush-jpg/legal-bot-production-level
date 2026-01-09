# 🚀 Legal Assistant - Quick Reference Card

## ⚡ Quick Commands

### Start the Application
```bash
# Backend (Terminal 1)
cd legal-bot/backend
python -m uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd legal-bot/frontend
npm run dev

# Open: http://localhost:5173
```

### Run Tests
```bash
cd legal-bot
python test_api_integrations.py
```

---

## 🎯 UI Buttons

| Button | Function | Location |
|--------|----------|----------|
| 🔍 Case Lookup | Search legal cases | Header |
| 📝 Amendments | Generate legal documents | Header |
| 💬 History | View/search chat history | Header |
| 📰 Recent Updates | View legal news | Header |
| 🎤 Voice Chat | Voice input/output | Input area |

---

## 🔌 API Endpoints

### Legal APIs
```bash
# Case Lookup
POST /api/legal/case-lookup
{"query": "Miranda v. Arizona", "jurisdiction": "US"}

# Amendment Generation
POST /api/legal/generate-amendment
{"document_type": "contract", "case_details": {...}}

# Statute Search
POST /api/legal/search-statutes?query=false+statements
```

### Chat History
```bash
# Save Message
POST /api/chat-history/save
{"user_id": "X", "session_id": "Y", "message": "...", "response": "..."}

# Search History
POST /api/chat-history/search
{"user_id": "X", "search_query": "Miranda", "limit": 20}

# Get Sessions
GET /api/chat-history/sessions/{user_id}

# Delete Session
DELETE /api/chat-history/session/{user_id}/{session_id}
```

### Translation
```bash
# Translate Text
POST /api/translate
{"text": "Hello", "target_language": "es"}

# Get Languages
GET /api/translate/languages
```

### Authentication
```bash
# Generate Token
POST /api/auth/token?user_id=test&role=premium

# Verify Token
GET /api/auth/verify
Authorization: Bearer {token}

# Check Access
GET /api/auth/check-access?api_name=case_lookup
```

---

## 👥 User Roles

| Role | Messages/Day | Uploads | APIs | Features |
|------|-------------|---------|------|----------|
| **Guest** | 10 | 0 | ❌ | Basic chat |
| **Standard** | 100 | 5 | Translation | Advanced chat, uploads |
| **Premium** | ∞ | ∞ | All | Full access |
| **Admin** | ∞ | ∞ | All | + Admin controls |

### Generate Premium Token
```bash
curl -X POST "http://localhost:8000/api/auth/token?user_id=test&role=premium"
```

---

## 🔑 Environment Variables

Create `backend/.env`:
```env
# Required
OPENAI_API_KEY=sk-...

# Optional (mock data used if not set)
CASETEXT_API_KEY=...
LEGALZOOM_API_KEY=...
LEXISNEXIS_API_KEY=...
WESTLAW_API_KEY=...
GOOGLE_TRANSLATE_API_KEY=...

# Optional (defaults provided)
JWT_SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017/
FIREBASE_CREDENTIALS_PATH=/path/to/creds.json
```

---

## 🗂️ File Locations

### Backend Services
```
backend/app/services/
├── legal_api_integrations.py   # Case lookup, amendments
├── chat_history_service.py     # Chat storage & search
├── translation_service.py      # Multilingual support
└── rbac_service.py             # Access control
```

### Frontend Components
```
frontend/src/components/
├── CaseLookup.jsx              # Case search modal
├── AmendmentGenerator.jsx      # Document generator
├── ChatHistorySearch.jsx       # History search
└── ChatInterface.jsx           # Main chat UI
```

### Documentation
```
legal-bot/
├── API_INTEGRATION_GUIDE.md           # Complete guide
├── QUICK_START_API_INTEGRATION.md     # 5-min setup
├── README_API_FEATURES.md             # User guide
├── API_INTEGRATION_COMPLETE.md        # Implementation summary
├── SYSTEM_ARCHITECTURE_DIAGRAM.txt    # Architecture
├── IMPLEMENTATION_SUMMARY.txt         # Summary
└── QUICK_REFERENCE.md                 # This file
```

---

## 🧪 Testing Checklist

### ✅ Backend Tests
- [ ] Run `python test_api_integrations.py`
- [ ] All services pass
- [ ] Mock data works

### ✅ API Tests
- [ ] Case lookup returns results
- [ ] Amendment generation works
- [ ] Chat history saves
- [ ] Translation works
- [ ] Token generation works

### ✅ UI Tests
- [ ] Case lookup modal opens
- [ ] Search returns results
- [ ] Amendment generator works
- [ ] Chat history displays
- [ ] Search highlights keywords

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Need 3.8+

# Reinstall dependencies
pip install -r requirements.txt

# Check port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Mac/Linux
```

### Frontend won't start
```bash
# Check Node version
node --version  # Need 16+

# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Getting mock data instead of real
- Add API keys to `.env`
- Restart backend
- Check backend logs

### Chat history not saving
```bash
# Create directory
mkdir -p backend/data/chat_history/

# Check permissions
ls -la backend/data/
```

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md) | Complete API reference |
| [QUICK_START_API_INTEGRATION.md](QUICK_START_API_INTEGRATION.md) | 5-minute setup |
| [README_API_FEATURES.md](README_API_FEATURES.md) | User guide with screenshots |
| [API_INTEGRATION_COMPLETE.md](API_INTEGRATION_COMPLETE.md) | Implementation details |
| [SYSTEM_ARCHITECTURE_DIAGRAM.txt](SYSTEM_ARCHITECTURE_DIAGRAM.txt) | System architecture |

---

## 💡 Tips & Tricks

### Development
- Use mock data for testing (no API costs)
- Generate Premium token for full access
- Check `backend_detailed.log` for debugging
- Use browser DevTools to monitor requests

### Production
- Add all API keys to `.env`
- Change `JWT_SECRET_KEY` to secure value
- Enable HTTPS
- Set up MongoDB/Firebase for scalability
- Configure rate limiting

### Customization
- Modify UI in `frontend/src/components/`
- Extend services in `backend/app/services/`
- Add endpoints in `backend/app/main.py`
- Update documentation

---

## 🎯 Common Use Cases

### 1. Search for a Legal Case
```
1. Click "🔍 Case Lookup"
2. Enter: "Miranda v. Arizona"
3. Select jurisdiction: "United States"
4. Click "Search Cases"
5. View results and click to insert
```

### 2. Generate Legal Amendment
```
1. Click "📝 Amendments"
2. Select document type: "Contract"
3. Enter details: "Change payment terms to net 60"
4. Click "Generate Amendment"
5. Copy or download document
```

### 3. Search Chat History
```
1. Click "💬 History"
2. Enter search: "Miranda rights"
3. View highlighted results
4. Click message to insert into chat
```

### 4. Get Premium Access
```bash
# Generate token
curl -X POST "http://localhost:8000/api/auth/token?user_id=test&role=premium"

# Copy token from response
# Use in Authorization header for API calls
```

---

## 🌟 Features Summary

✅ **Legal APIs**: Case lookup, amendments, statutes
✅ **Chat History**: Save, search, manage conversations
✅ **Multilingual**: 30+ languages supported
✅ **RBAC**: Role-based access with JWT
✅ **Voice Chat**: Speech input/output
✅ **Document Upload**: PDF, DOCX, images with OCR
✅ **Beautiful UI**: Modern, responsive design
✅ **Mock Data**: Works without API keys

---

## 📞 Getting Help

1. **Check Documentation**: See guides above
2. **Run Tests**: `python test_api_integrations.py`
3. **Check Logs**: `backend_detailed.log`
4. **Verify Setup**: Ensure all dependencies installed

---

## ✨ Quick Facts

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **Database**: Local JSON / MongoDB / Firebase
- **AI**: OpenAI GPT-4
- **APIs**: CaseText, LegalZoom, Google Translate
- **Auth**: JWT tokens
- **Storage**: FAISS vector database

---

**🎉 Ready to use! Open http://localhost:5173 and start exploring!**

---

*Version 1.0.0 • January 2026 • Production Ready*

# Quick Start Guide - API Integration Features

## 🚀 Get Started in 5 Minutes

This guide will help you quickly set up and test the new API integration features.

---

## Step 1: Install Dependencies

```bash
cd legal-bot/backend
pip install PyJWT httpx pymongo firebase-admin
```

---

## Step 2: Configure Environment (Optional)

The system works with **mock data** by default. To use real APIs, create `.env` file:

```env
# Minimum required for chat
OPENAI_API_KEY=your_openai_key_here

# Optional: Real legal APIs (mock data used if not set)
CASETEXT_API_KEY=your_key_here
LEGALZOOM_API_KEY=your_key_here
GOOGLE_TRANSLATE_API_KEY=your_key_here

# Optional: JWT secret (default provided)
JWT_SECRET_KEY=your-secret-key
```

---

## Step 3: Start the Backend

```bash
cd legal-bot/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## Step 4: Start the Frontend

```bash
cd legal-bot/frontend
npm install  # First time only
npm run dev
```

Open browser to: `http://localhost:5173`

---

## Step 5: Test the Features

### 🔍 Test Case Lookup

1. Complete onboarding (select language, country, law type)
2. Click **"🔍 Case Lookup"** button in the header
3. Enter search query: `Miranda v. Arizona`
4. Click **"Search Cases"**
5. You'll see mock results (or real results if API key configured)

### 📝 Test Amendment Generator

1. Click **"📝 Amendments"** button
2. Select document type (e.g., "CONTRACT")
3. Enter amendment details: `Change payment terms to net 60 days`
4. Click **"Generate Amendment"**
5. View, copy, or download the generated document

### 💬 Test Chat History

1. Have a few chat conversations
2. Click **"💬 History"** button
3. View your chat sessions
4. Use search to find specific messages
5. Click on a session to view all messages

### 🌐 Test Translation

The translation API is integrated but not exposed in UI yet. Test via API:

```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how can I help you?",
    "target_language": "es"
  }'
```

---

## 🧪 Quick API Tests

### Test Case Lookup API

```bash
curl -X POST http://localhost:8000/api/legal/case-lookup \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Miranda v. Arizona",
    "jurisdiction": "US",
    "limit": 5
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "source": "Mock Data (API not configured)",
  "results": [
    {
      "case_name": "Miranda v. Arizona",
      "citation": "384 U.S. 436 (1966)",
      "court": "Supreme Court of the United States",
      ...
    }
  ],
  "total": 3,
  "note": "Configure API keys to access real legal databases"
}
```

### Test Amendment Generation API

```bash
curl -X POST http://localhost:8000/api/legal/generate-amendment \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "contract",
    "case_details": {
      "amendment_text": "Change payment terms to net 60 days"
    }
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "source": "Mock Generator (API not configured)",
  "document_id": "mock_contract_1234567890",
  "content": "LEGAL AMENDMENT - CONTRACT\n\n...",
  "note": "Configure LegalZoom API key to generate real legal documents"
}
```

### Test Chat History API

```bash
# Save a message
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

### Test RBAC System

```bash
# Generate a token
curl -X POST "http://localhost:8000/api/auth/token?user_id=test_user&role=premium"

# Response:
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "role": "premium",
  "permissions": [...],
  "limits": {
    "daily_messages": -1,
    "document_uploads": -1,
    "api_calls": -1
  }
}

# Use the token
curl -X POST http://localhost:8000/api/legal/case-lookup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"query": "Miranda v. Arizona"}'
```

---

## 📊 Feature Overview

### What Works Out of the Box (No API Keys)

✅ **Case Lookup** - Returns mock landmark cases
✅ **Amendment Generator** - Generates mock legal documents
✅ **Chat History** - Local JSON storage
✅ **Translation** - Mock translations with language prefix
✅ **RBAC** - Full role-based access control
✅ **All UI Components** - Fully functional

### What Requires API Keys

🔑 **Real Case Lookup** - CaseText, LexisNexis, Westlaw APIs
🔑 **Real Amendment Generation** - LegalZoom API
🔑 **Real Translation** - Google Cloud Translation API
🔑 **Cloud Storage** - MongoDB or Firebase (optional)

---

## 🎯 User Roles & Permissions

### Guest Role (Default)
- ✅ Basic chat
- ❌ No document uploads
- ❌ No API access
- Limit: 10 messages/day

### Standard Role
- ✅ Basic & advanced chat
- ✅ Document uploads (5/day)
- ✅ Translation API
- ❌ Case lookup
- ❌ Amendment generation
- Limit: 100 messages/day

### Premium Role (Recommended for Testing)
- ✅ All features
- ✅ Unlimited messages
- ✅ Unlimited uploads
- ✅ All APIs (case lookup, amendments, statutes)
- ✅ Export chat history

### Admin Role
- ✅ All Premium features
- ✅ Admin controls
- ✅ Analytics access

**To test with Premium access**:
```bash
# Generate Premium token
curl -X POST "http://localhost:8000/api/auth/token?user_id=test_user&role=premium"
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Mac/Linux

# Kill process and restart
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### "Access Denied" errors
```bash
# Generate a Premium token
curl -X POST "http://localhost:8000/api/auth/token?user_id=test_user&role=premium"

# Use the token in Authorization header
# Or: The UI works without tokens (uses Standard role by default)
```

### Chat history not saving
```bash
# Check if directory exists
ls backend/data/chat_history/

# Create if missing
mkdir -p backend/data/chat_history/
```

---

## 📚 Next Steps

1. **Read Full Documentation**: See `API_INTEGRATION_GUIDE.md`
2. **Configure Real APIs**: Add API keys to `.env` file
3. **Customize UI**: Modify components in `frontend/src/components/`
4. **Add More Features**: Extend services in `backend/app/services/`
5. **Deploy to Production**: Follow deployment guide in documentation

---

## 💡 Tips

- **Mock Data is Useful**: Test UI/UX without API costs
- **Start with Premium Role**: Get full feature access for testing
- **Use Chat History**: Track your testing conversations
- **Check Backend Logs**: See detailed API call information
- **Browser DevTools**: Monitor network requests

---

## 🎉 You're Ready!

The system is now fully functional with:
- ✅ Legal case lookup
- ✅ Amendment generation
- ✅ Chat history with search
- ✅ Multilingual support
- ✅ Role-based access control
- ✅ Beautiful UI components

**Enjoy exploring the features!**

---

## 📞 Need Help?

Check the full documentation in `API_INTEGRATION_GUIDE.md` for:
- Detailed API reference
- Architecture diagrams
- Production deployment guide
- Security best practices
- Advanced configuration

---

**Happy Coding! 🚀**

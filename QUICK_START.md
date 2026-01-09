# 🚀 Quick Start Guide - Enhanced Legal Assistant

## Get Up and Running in 5 Minutes!

This guide will get your Enhanced Legal Assistant up and running quickly.

---

## Prerequisites

- ✅ Node.js 18+ installed
- ✅ Python 3.9+ installed
- ✅ OpenAI API key (for LLM responses)

---

## Step 1: Install Dependencies

### Backend
```bash
cd legal-bot/backend
pip install -r requirements.txt
```

### Frontend
```bash
cd legal-bot/frontend
npm install
```

---

## Step 2: Configure Environment

Create `.env` file in `legal-bot/backend/`:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (mock data used if not provided)
CASETEXT_API_KEY=
LEGALZOOM_API_KEY=
LEXISNEXIS_API_KEY=
WESTLAW_API_KEY=
```

---

## Step 3: Start the Application

### Terminal 1: Start Backend
```bash
cd legal-bot/backend
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Terminal 2: Start Frontend
```bash
cd legal-bot/frontend
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Step 4: Access the Application

Open your browser and go to:
```
http://localhost:5173
```

---

## Step 5: Test the Features

### 1. Start a New Chat
- Click **"New Chat"** in the navigation bar
- Select a law type (e.g., Traffic Law)
- Ask a question: "What are the penalties for speeding?"

### 2. Try Case Lookup
- Click **"🔍 Case Lookup"** in the header
- Search for: "Miranda"
- View the results

### 3. Generate an Amendment
- Click **"📝 Amendments"** in the header
- Select document type: "Contract"
- Fill in details and generate

### 4. Search Chat History
- Click **"Search Chats"** in navigation
- Enter a search term
- View highlighted results

---

## Troubleshooting

### Backend won't start?
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start?
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### "OpenAI API key not configured"?
- Make sure you created `.env` file in `backend/` directory
- Verify the API key is correct
- Restart the backend server

### Port already in use?
```bash
# Use different ports
# Backend:
python -m uvicorn app.main:app --reload --port 8001

# Frontend: Update vite.config.js
server: { port: 5174 }
```

---

## Quick Test Commands

### Test Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "backend_running": true,
  "openai_configured": true
}
```

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/artillery/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is criminal law?"}'
```

### Test Case Lookup
```bash
curl -X POST http://localhost:8000/api/legal/case-lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "Miranda", "limit": 5}'
```

---

## Default User Roles

The application supports 4 roles:

| Role | Access Level | Features |
|------|--------------|----------|
| **Guest** | Basic | Chat only |
| **Standard** | Medium | + Search, Translation |
| **Premium** | High | + Case Lookup, Amendments |
| **Enterprise** | Full | All features |

To test different roles:

```bash
# Generate a token
curl -X POST "http://localhost:8000/api/auth/token?user_id=test_user&role=premium"
```

---

## File Structure Overview

```
legal-bot/
├── backend/
│   ├── app/
│   │   ├── main.py              # Main FastAPI app
│   │   ├── services/            # Business logic
│   │   └── api/                 # API routes
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── EnhancedApp.jsx        # Main app
│   │   │   ├── NavigationBar.jsx      # Top nav
│   │   │   ├── ChatSidebar.jsx        # Left sidebar
│   │   │   ├── ChatInterface.jsx      # Chat area
│   │   │   ├── CaseLookup.jsx         # Case search
│   │   │   └── AmendmentGenerator.jsx # Amendment gen
│   │   └── App.jsx
│   └── package.json
│
├── ENHANCED_UI_GUIDE.md         # Full documentation
├── TESTING_GUIDE.md             # Testing procedures
├── IMPLEMENTATION_SUMMARY.md    # Project summary
└── QUICK_START.md               # This file
```

---

## Next Steps

1. ✅ Read `ENHANCED_UI_GUIDE.md` for detailed feature documentation
2. ✅ Review `TESTING_GUIDE.md` for testing procedures
3. ✅ Check `IMPLEMENTATION_SUMMARY.md` for project overview
4. ✅ Explore the API documentation at `http://localhost:8000/docs`

---

## Common Use Cases

### Use Case 1: Legal Research
1. Start new chat
2. Ask about a legal topic
3. Use Case Lookup to find relevant cases
4. Save the chat for later reference

### Use Case 2: Document Amendment
1. Start new chat about a contract issue
2. Use Amendment Generator
3. Fill in details
4. Download the generated amendment

### Use Case 3: Multi-language Support
1. Change language in preferences
2. Ask questions in your language
3. Get responses in the same language

---

## Performance Tips

1. **Clear old chats**: Keep only recent chats for better performance
2. **Use search**: Instead of scrolling, use the search feature
3. **Collapse sidebar**: On smaller screens, collapse the sidebar
4. **Close modals**: Close unused modals to free memory

---

## Keyboard Shortcuts

- `Ctrl/Cmd + K`: Open search
- `Ctrl/Cmd + N`: New chat
- `Ctrl/Cmd + /`: Toggle sidebar
- `Enter`: Send message
- `Shift + Enter`: New line in message

---

## Getting Help

1. **Documentation**: Check the guides in the root directory
2. **API Docs**: Visit `http://localhost:8000/docs`
3. **Console**: Check browser console for errors (F12)
4. **Logs**: Check backend terminal for error messages

---

## Production Deployment

### Build Frontend
```bash
cd legal-bot/frontend
npm run build
```

### Deploy Backend
```bash
# Using Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or using Docker
docker build -t legal-assistant .
docker run -p 8000:8000 legal-assistant
```

---

## Environment Variables

### Backend (.env)
```env
# Required
OPENAI_API_KEY=sk-...

# Optional
CASETEXT_API_KEY=
LEGALZOOM_API_KEY=
LEXISNEXIS_API_KEY=
WESTLAW_API_KEY=

# Server Config
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Database (if using)
DATABASE_URL=postgresql://...
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=LEGID Legal Assistant
```

---

## Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can access the UI in browser
- [ ] Can send chat messages
- [ ] Can search chats
- [ ] Can use Case Lookup
- [ ] Can generate amendments
- [ ] All features working

---

## 🎉 You're All Set!

Your Enhanced Legal Assistant is now running. Enjoy exploring all the features!

For detailed documentation, see:
- `ENHANCED_UI_GUIDE.md` - Complete feature guide
- `TESTING_GUIDE.md` - Testing procedures
- `IMPLEMENTATION_SUMMARY.md` - Project overview

---

**Happy Coding! 🚀**

Last Updated: January 9, 2026

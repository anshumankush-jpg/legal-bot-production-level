# ⚡ QUICK TEST - 3 Steps

## Step 1: Start Backend (if not running)
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Step 2: Open Frontend
- Open `frontend/legal-chat.html` in your browser
- OR double-click: `OPEN_FRONTEND.bat`

## Step 3: Ask Question
```
Can I use my phone while stopped at a red light?
```

---

## ✅ What You Should See NOW:

**GOOD (AI-Generated):**
- Conversational answer that flows naturally
- References specific laws from retrieved documents
- Mentions jurisdiction (PEI, Ontario, etc.)
- Varies based on what documents were retrieved

**BAD (Old Hardcoded - Should NOT appear):**
```
**Using a Phone While Driving - Canadian Law**

Based on Canadian traffic laws, here's what you need to know:

**The Law:**
Using a hand-held cell phone...
```

---

## ⚠️ If You See Document Excerpts:

That means **no LLM is configured**. To fix:

**Option 1: FREE (Ollama - 2 minutes):**
```bash
# Install Ollama: https://ollama.ai
ollama run llama3.2

# Backend will auto-detect and use it!
```

**Option 2: FREE (Gemini - 1 minute):**
1. Get key: https://makersuite.google.com/app/apikey
2. Set in backend: `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=your_key`

---

## 🎯 The Changes Are LIVE

All code changes are complete. Just:
1. Restart backend
2. Test in browser
3. You'll see AI answers (not templates)!

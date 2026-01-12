# 🎯 LeguBot Setup Guide - AI-Generated Answers

## ✅ What Changed?

**REMOVED:** Hardcoded answer templates that gave generic Canadian law responses  
**ADDED:** Real AI-generated answers grounded in your actual legal documents

---

## 🚀 Quick Setup (3 Options)

### Option 1: 100% FREE (Ollama - Recommended)

1. **Install Ollama** (local, no API needed):
   ```bash
   # Visit: https://ollama.ai and download installer
   # Or use package manager:
   # Windows: winget install Ollama.Ollama
   # Mac: brew install ollama
   ```

2. **Download and run the model**:
   ```bash
   ollama run llama3.2
   ```

3. **Configure backend**:
   ```bash
   cd backend
   # Create .env file if it doesn't exist:
   echo "LLM_PROVIDER=ollama" > .env
   echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
   echo "OLLAMA_MODEL=llama3.2" >> .env
   ```

4. **Start backend**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

✅ **Cost:** $0 (runs locally)  
✅ **Speed:** Fast (local processing)  
✅ **Privacy:** 100% (no data sent to cloud)

---

### Option 2: FREE Tier (Google Gemini)

1. **Get free API key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **Configure backend**:
   ```bash
   cd backend
   echo "LLM_PROVIDER=gemini" > .env
   echo "GEMINI_API_KEY=your_key_here" >> .env
   ```

3. **Start backend**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

✅ **Cost:** Free (15 requests/min, 1M tokens/day)  
✅ **Speed:** Very fast  
✅ **Quality:** Excellent

---

### Option 3: Paid (OpenAI - Best Quality)

1. **Get API key**:
   - Visit: https://platform.openai.com/api-keys
   - Create a new key
   - Add $5-10 credit

2. **Configure backend**:
   ```bash
   cd backend
   echo "LLM_PROVIDER=openai" > .env
   echo "OPENAI_API_KEY=your_key_here" >> .env
   ```

3. **Start backend**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

✅ **Cost:** ~$0.15 per 1M tokens (very cheap!)  
✅ **Speed:** Very fast  
✅ **Quality:** Best available

---

## 📝 Testing Your Setup

### 1. Open the frontend:
```bash
# Open frontend/legal-chat.html in your browser
# Or double-click: OPEN_FRONTEND.bat
```

### 2. Ask a test question:
```
"Can I use my phone while stopped at a red light?"
```

### 3. Expected behavior:

**✅ GOOD (AI-generated):**
```
Based on Canadian traffic laws, here's what you need to know about using 
your phone at a red light...

According to the Highway Traffic Act, Section 78.1 states that...

[Conversational, specific to jurisdiction, cites actual laws]
```

**❌ BAD (Hardcoded - OLD SYSTEM):**
```
**Using a Phone While Driving - Canadian Law**

Based on Canadian traffic laws, here's what you need to know:

**The Law:**
Using a hand-held cell phone...
[Generic template text]
```

---

## 🔧 Troubleshooting

### Issue: "All LLM providers failed"

**Solution 1: Check Ollama is running**
```bash
# Check if Ollama is running:
curl http://localhost:11434/api/version

# If not running, start it:
ollama serve
```

**Solution 2: Check API keys**
```bash
# Verify your .env file:
cat backend/.env

# Should show:
# LLM_PROVIDER=ollama (or gemini/openai)
# GEMINI_API_KEY=... (if using gemini)
# OPENAI_API_KEY=... (if using openai)
```

**Solution 3: Check logs**
```bash
# Watch backend logs:
tail -f backend/backend_detailed.log

# Look for:
# ✅ "LLM (ollama) generated answer in X.XXs"
# ❌ "ollama failed: ..." means Ollama not running
```

---

### Issue: Answers are still hardcoded templates

**Cause:** Backend using old fallback code  
**Solution:** Restart the backend server:
```bash
# Stop backend (Ctrl+C)
# Then restart:
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Issue: "No documents have been uploaded yet"

**Cause:** Vector database is empty  
**Solution:** Ingest your legal documents:
```bash
cd backend/scripts
python bulk_ingest_documents.py
```

---

## 📊 System Architecture

```
User Question
    ↓
Vector Search (FAISS) → Retrieves relevant legal docs
    ↓
AI Prompt Builder → Creates conversational prompt
    ↓
LLM Provider (Ollama/Gemini/OpenAI) → Generates answer
    ↓
Response Formatter → Adds citations
    ↓
User sees AI-generated answer ✅
```

**NO MORE HARDCODED TEMPLATES!** 🎉

---

## 🎓 How It Works Now

1. **User asks:** "Can I use my phone at a red light?"

2. **System retrieves:** Relevant sections from PEI Highway Traffic Act, Ontario HTA, etc.

3. **AI analyzes:** The retrieved documents and generates a conversational answer

4. **System returns:** 
   - Clear, conversational answer
   - Specific citations (jurisdiction, section, page)
   - Practical guidance
   - Legal disclaimer

---

## 📞 Support

If you're still seeing hardcoded answers or have issues:

1. Check `backend/backend_detailed.log` for errors
2. Verify Ollama/Gemini is configured and running
3. Restart backend server
4. Test with a simple question

**Expected log output:**
```
🔄 Trying LLM provider: ollama...
✅ LLM (ollama) generated answer in 2.34s: 587 characters
✅ Chat response generated in 3.12s
```

---

## 🎯 Summary

✅ **Hardcoded templates:** REMOVED  
✅ **AI-generated answers:** ENABLED  
✅ **Jurisdiction-aware:** YES (filters by province)  
✅ **Grounded in docs:** YES (uses retrieved legal text)  
✅ **Free option:** YES (Ollama local LLM)  
✅ **ChatGPT style:** YES (conversational answers)

**You now have a real AI legal assistant, not a template bot!** 🚀

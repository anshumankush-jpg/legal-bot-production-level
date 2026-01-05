# 🚀 START HERE - Quick Reference Card

> **Before you start:** Make sure you have your API keys ready (OpenAI or Azure OpenAI)

## Pre-Flight Checklist

### ✅ Step 0: Verify Setup
```bash
cd backend/scripts
python verify_setup.py
```
**Fixes needed?** 
- Missing packages → Run Step 1 first
- Missing API keys → Create `.env` file in `backend/` directory with your keys
  ```env
  OPENAI_API_KEY=your_key_here
  # OR for Azure:
  AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
  AZURE_OPENAI_API_KEY=your_key_here
  ```

---

### ✅ Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

---

### ✅ Step 2: Start Backend Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
**Keep this terminal open!** You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`

---

### ✅ Step 3: Test Setup (Optional)
**Open a NEW terminal:**
```bash
cd backend/scripts
python test_ingestion.py
```
**Expected:** All tests pass ✓

---

### ✅ Step 4: Bulk Ingest Documents
**In the same terminal:**
```bash
python bulk_ingest_documents.py
```
**What happens:**
1. Finds all PDF/HTML/JSON files
2. Shows count: "Found 107 documents"
3. Asks: "Do you want to proceed? (yes/no)"
4. Type `yes` and press Enter
5. Processes files (10-30 minutes for 100+ files)
6. Shows summary: "Successfully indexed: 105"

---

### ✅ Step 5: Test Queries

**Option A: Via API (Terminal)**

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/query/answer" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question": "What are the penalties for speeding in PEI?"}'
```

**Linux/Mac (curl):**
```bash
curl -X POST "http://localhost:8000/api/query/answer" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the penalties for speeding in PEI?"}'
```

**Option B: Via Frontend (Browser)**
1. Start frontend: `cd frontend && npm start`
2. Open: `http://localhost:4200/chat`
3. Ask your question in the chat interface

---

## 🎯 What You'll Get

After ingestion, queries will:
- ✅ Answer from YOUR actual legal documents
- ✅ Cite sources: `[Source: pei_highway_traffic_act.pdf, Page: 45]`
- ✅ Reference case studies when available
- ✅ Provide detailed answers (up to 2500 tokens)
- ✅ Distinguish jurisdictions (Ontario vs PEI, etc.)

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to API" | Make sure backend is running (Step 2) |
| "ModuleNotFoundError" | Run: `pip install -r requirements.txt` |
| "No documents found" | Check folder names match exactly |
| "I don't have information" | Wait a few seconds after ingestion |
| Rate limit errors | Increase delay in script or process in batches |

---

## 📚 More Help

- **Detailed Guide:** `QUICK_START_INGESTION.md`
- **Bulk Ingestion:** `scripts/BULK_INGESTION_GUIDE.md`
- **Backend Docs:** `README.md`
- **Azure Setup:** `README_AZURE.md`

---

## ⚡ Quick Commands Reference

```bash
# Verify setup
cd backend/scripts && python verify_setup.py

# Start backend
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test ingestion
cd backend/scripts && python test_ingestion.py

# Bulk ingest
cd backend/scripts && python bulk_ingest_documents.py

# Check health (Windows PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Check health (Linux/Mac)
curl http://localhost:8000/health

# Test query (Windows PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/api/query/answer" `
  -Method POST -ContentType "application/json" `
  -Body '{"question": "Your question here"}'

# Test query (Linux/Mac)
curl -X POST "http://localhost:8000/api/query/answer" \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

---

---

## 📝 Notes

- **Windows Users:** Use PowerShell for API commands (curl may not be available)
- **First Time?** Make sure you have a `.env` file in `backend/` with your API keys
- **Processing Time:** Large document sets (100+ files) may take 10-30 minutes
- **Keep Backend Running:** Don't close the terminal where the backend server is running

---

**Ready? Start with Step 0!** 🎯


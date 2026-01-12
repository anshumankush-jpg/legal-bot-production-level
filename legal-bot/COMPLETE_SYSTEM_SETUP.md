# 🔧 Complete System Setup & Configuration

## 📊 Current Configuration

### **Embedding Engine:**
- **Provider:** Sentence Transformers (local, free)
- **Model:** `all-MiniLM-L6-v2` (384 dimensions)
- **Status:** ✅ Installed and ready

### **Vector Database:**
- **Type:** FAISS (local file-based)
- **Location:** `backend/data/faiss/`
- **Status:** ✅ Configured

### **Chat/LLM:**
- **Provider:** OpenAI (GPT-4o)
- **API Key:** ✅ Set in `.env`
- **Status:** ✅ Ready

---

## 📁 Dataset Locations

The system searches for documents in these folders:

1. **`data/`** - Main data folder
   - `demerit_tables/` - Demerit points per jurisdiction
   - `fight_process_guides/` - How to dispute tickets
   - `example_tickets/` - Sample ticket data
   - `lawyers/` - Lawyer directory

2. **`us_state_codes/`** - US state legal codes
   - Washington, California, Texas, etc.

3. **`canada_traffic_acts/`** - Canadian traffic laws
   - Ontario, BC, Alberta, etc.

4. **`paralegal_advice_dataset/`** - Case studies and advice

5. **`CANADA TRAFFIC FILES/`** - Additional Canadian traffic data

6. **`canada criminal and federal law/`** - Canadian criminal law

---

## ✅ Setup Checklist

### Step 1: Update `.env` File

Add to `backend/.env`:

```env
# Embedding Provider - Sentence Transformers (FREE)
EMBEDDING_PROVIDER=sentence_transformers
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2

# OpenAI API Key (for chat responses)
OPENAI_API_KEY=your-openai-api-key-here

# LLM Provider (for generating answers)
LLM_PROVIDER=openai
OPENAI_CHAT_MODEL=gpt-4o
```

### Step 2: Restart Backend

Restart to load new settings:
- Kill old backend
- Start: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Step 3: Ingest All Documents

Run bulk ingestion to index all datasets:
```bash
python backend/scripts/bulk_ingest_documents.py
```

This will find and ingest:
- ✅ All JSON files in `data/` folder
- ✅ All PDF files in legal document folders
- ✅ All HTML files in state code folders
- ✅ All case studies in paralegal dataset

### Step 4: Verify Documents Are Indexed

Check health endpoint:
```bash
curl http://localhost:8000/health
```

Should show: `"index_size": > 0`

---

## 🎯 How It Works

### **Embedding Flow:**
```
Documents (PDF/HTML/JSON)
    ↓
Text Extraction
    ↓
Chunking (Split into pieces)
    ↓
Sentence Transformers (Local, FREE)
    ↓
FAISS Index (Local storage)
```

### **Query Flow:**
```
User Question
    ↓
Sentence Transformers Embedding (Local)
    ↓
FAISS Search (Find similar chunks)
    ↓
Retrieve Context
    ↓
OpenAI GPT-4o (Generate answer)
    ↓
Response to User
```

---

## 💡 Key Points

1. **Embeddings:** Sentence Transformers (local, free, offline)
2. **Database:** FAISS (local file storage)
3. **Chat:** OpenAI GPT-4o (for generating answers)
4. **Datasets:** All folders are searched automatically
5. **No Upload Needed:** Chatbot works from ingested datasets

---

## 🚀 After Setup

The chatbot will:
- ✅ Answer questions from all ingested datasets
- ✅ Reference US state codes
- ✅ Reference Canada traffic acts
- ✅ Use paralegal advice dataset
- ✅ Work without document uploads (uses ingested data)
- ✅ Still allow uploads for additional documents

---

**Everything is configured! Just update `.env`, restart, and ingest documents!** 🎯


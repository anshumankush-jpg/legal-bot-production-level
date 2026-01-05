# 🔍 Search Engine & Database Configuration

## Current Configuration

### **Search Engine (Embeddings):**
- **Provider:** Sentence Transformers
- **Model:** `all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Type:** Local (runs on your computer)
- **Cost:** FREE
- **Status:** ✅ Active

### **Vector Database:**
- **Type:** FAISS (Facebook AI Similarity Search)
- **Storage:** Local file-based
- **Location:** `backend/data/faiss/`
- **Files:**
  - `index.faiss` - Vector index
  - `metadata.jsonl` - Document metadata
- **Status:** ✅ Active

---

## How It Works

### **1. Document Ingestion:**
```
Document (PDF/HTML/JSON)
    ↓
Text Extraction
    ↓
Chunking (Split into pieces)
    ↓
Sentence Transformers (Local)
    → Converts text to 384-dim vectors
    ↓
FAISS Index (Local Storage)
    → Stores vectors + metadata
```

### **2. Query Processing:**
```
User Question
    ↓
Sentence Transformers (Local)
    → Converts question to 384-dim vector
    ↓
FAISS Search (Local)
    → Finds similar document chunks
    → Returns top-K results
    ↓
Retrieved Context
    ↓
OpenAI GPT-4o (API)
    → Generates answer from context
    ↓
Response to User
```

---

## Configuration Files

### **`backend/app/core/config.py`:**
```python
# Embedding Provider - Sentence Transformers (local, free)
EMBEDDING_PROVIDER: str = "sentence_transformers"
SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

# FAISS Configuration (local vector database)
FAISS_INDEX_PATH: str = "./data/faiss/index.faiss"
FAISS_METADATA_PATH: str = "./data/faiss/metadata.jsonl"
```

### **`backend/app/vector_store/__init__.py`:**
- Automatically selects FAISS (Azure is disabled)
- Creates FAISS store with correct dimensions

### **`backend/app/embeddings/embedding_service.py`:**
- Initializes Sentence Transformer model on startup
- Auto-detects embedding dimensions (384 for all-MiniLM-L6-v2)

---

## Benefits

### **Sentence Transformers:**
- ✅ FREE (no API costs)
- ✅ Works offline
- ✅ Fast local processing
- ✅ No rate limits
- ✅ Good quality for document search

### **FAISS:**
- ✅ FREE (local file storage)
- ✅ Fast similarity search
- ✅ No cloud dependencies
- ✅ Works offline
- ✅ Scales to millions of vectors

---

## Verification

### Check Configuration:
```python
from app.core.config import settings
print("Embedding Provider:", settings.EMBEDDING_PROVIDER)
print("Model:", settings.SENTENCE_TRANSFORMER_MODEL)
print("Dimensions:", settings.EMBEDDING_DIMENSIONS)
print("FAISS Index:", settings.FAISS_INDEX_PATH)
```

### Check Active Services:
```python
from app.embeddings.embedding_service import get_embedding_service
from app.vector_store import get_vector_store

embedding_service = get_embedding_service()
vector_store = get_vector_store()

print("Embedding Service:", type(embedding_service).__name__)
print("Vector Store:", type(vector_store).__name__)
```

---

## Summary

✅ **Search Engine:** Sentence Transformers (local, free)  
✅ **Database:** FAISS (local file storage)  
✅ **Status:** Both active and configured  
✅ **Cost:** FREE (no cloud services)  
✅ **Offline:** Works without internet (except for OpenAI chat)

**Everything runs locally except for the final answer generation (OpenAI API)!** 🚀


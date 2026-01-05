# 🔄 Switching to Sentence Transformers

## ✅ What Changed

### 1. **Added Sentence Transformers Support**
- ✅ New embedding provider option: `sentence_transformers`
- ✅ Local, free embeddings (no API costs!)
- ✅ Fast and works offline

### 2. **Configuration Updated**
- ✅ Added `EMBEDDING_PROVIDER` setting
- ✅ Added `SENTENCE_TRANSFORMER_MODEL` setting
- ✅ Auto-detects embedding dimensions

### 3. **Dependencies Installed**
- ✅ `sentence-transformers` package
- ✅ `torch` (PyTorch) - required dependency

---

## 📝 Update Your `.env` File

Add these lines to `backend/.env`:

```env
# Embedding Provider (choose one)
EMBEDDING_PROVIDER=sentence_transformers

# Sentence Transformer Model
# Options:
#   - all-MiniLM-L6-v2 (384 dimensions, fast, good quality)
#   - all-mpnet-base-v2 (768 dimensions, better quality, slower)
#   - sentence-transformers/all-MiniLM-L12-v2 (384 dimensions)
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

---

## 🎯 Model Options

### Recommended Models:

1. **`all-MiniLM-L6-v2`** (Default - Recommended)
   - Dimensions: 384
   - Speed: ⚡ Very Fast
   - Quality: ✅ Good
   - Size: Small (~80MB)
   - **Best for:** Most use cases

2. **`all-mpnet-base-v2`**
   - Dimensions: 768
   - Speed: 🐢 Slower
   - Quality: ⭐ Excellent
   - Size: Large (~420MB)
   - **Best for:** When quality is critical

3. **`sentence-transformers/all-MiniLM-L12-v2`**
   - Dimensions: 384
   - Speed: ⚡ Fast
   - Quality: ✅ Very Good
   - Size: Medium (~130MB)
   - **Best for:** Balance of speed and quality

---

## 🔄 How to Switch

### Step 1: Update `.env`
```env
EMBEDDING_PROVIDER=sentence_transformers
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

### Step 2: Restart Backend
The backend will:
- Load the Sentence Transformer model on startup
- Auto-detect embedding dimensions
- Use local embeddings (no API calls!)

### Step 3: Re-ingest Documents
Since embedding dimensions changed, you need to re-ingest:
```bash
# Delete old FAISS index
rm backend/data/faiss/index.faiss
rm backend/data/faiss/metadata.jsonl

# Re-ingest documents
python backend/scripts/bulk_ingest_documents.py
```

---

## 💰 Cost Comparison

### OpenAI Embeddings:
- 💰 **Cost:** ~$0.0001 per 1K tokens
- 🌐 **Requires:** Internet + API key
- ⚡ **Speed:** Fast (API call)

### Sentence Transformers:
- ✅ **Cost:** FREE (runs locally)
- 🏠 **Requires:** Just your computer
- ⚡ **Speed:** Very fast (local processing)

---

## 📊 Performance

**Sentence Transformers:**
- ✅ No API rate limits
- ✅ Works offline
- ✅ No costs
- ✅ Fast batch processing
- ✅ Good quality for most tasks

**OpenAI Embeddings:**
- ✅ Slightly better quality
- ❌ Costs money
- ❌ Requires internet
- ❌ API rate limits

---

## 🎯 Recommendation

**For your use case (local development):**
- ✅ **Use Sentence Transformers** (`all-MiniLM-L6-v2`)
- ✅ Free, fast, works offline
- ✅ Perfect quality for legal document search

---

## ✅ After Switching

1. **Update `.env`** with `EMBEDDING_PROVIDER=sentence_transformers`
2. **Restart backend** (to load new model)
3. **Re-ingest documents** (new embeddings)
4. **Test chat** - should work perfectly!

---

**Sentence Transformers is installed and ready! Just update `.env` and restart!** 🚀


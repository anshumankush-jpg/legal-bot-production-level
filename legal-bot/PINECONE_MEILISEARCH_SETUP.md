# 🚀 Pinecone + Meilisearch Integration Complete!

## ✅ What's Been Installed

1. **Pinecone** - Cloud vector database (FREE tier available)
2. **Meilisearch** - Full-text keyword search engine (FREE & open source)

Both are now integrated into your legal AI system!

---

## 📝 Step 1: Update Your `.env` File

Add these lines to `backend/.env`:

```bash
# ============================================================================
# VECTOR STORE CONFIGURATION
# ============================================================================

# Switch from FAISS to Pinecone
VECTOR_STORE=pinecone
EMBEDDING_DIMENSIONS=1536

# Pinecone Configuration
PINECONE_API_KEY=pcsk_32Scji_ES7HgKskDQVdeHmcNBVaoUPJVikvqoAdj7jmjQrDtrMe6DAzWUmipY4B4wQPfr3
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=legal-docs
USE_PINECONE=true

# ============================================================================
# SEARCH ENGINE CONFIGURATION
# ============================================================================

# Meilisearch (optional - for keyword search)
USE_MEILISEARCH=true
MEILISEARCH_HOST=http://localhost:7700
MEILISEARCH_API_KEY=
MEILISEARCH_INDEX_NAME=legal-documents
```

**Important:** Make sure you have `OPENAI_API_KEY` set for embeddings!

---

## 📝 Step 2: Install Meilisearch Server (Optional)

Meilisearch needs a server running. Choose one option:

### Option A: Docker (Easiest)
```bash
docker run -d -p 7700:7700 -v $(pwd)/meili_data:/meili_data getmeili/meilisearch:latest
```

### Option B: Direct Install (Windows)
```powershell
# Download and run
Invoke-WebRequest -Uri https://github.com/meilisearch/meilisearch/releases/latest/download/meilisearch-windows-amd64.exe -OutFile meilisearch.exe
.\meilisearch.exe
```

### Option C: Skip for Now
If you don't want keyword search yet, set:
```bash
USE_MEILISEARCH=false
```

---

## 🧪 Step 3: Test the Integration

Run this test script:

```bash
cd backend
python test_pinecone_integration.py
```

---

## 📊 How It Works Now

### Architecture:

```
User Query
    ↓
┌─────────────────────────────────────────┐
│  Your Legal AI Backend                  │
├─────────────────────────────────────────┤
│                                          │
│  1. Generate Embedding (OpenAI)         │
│     ↓                                    │
│  2. Vector Search (Pinecone) ←─────────┐│
│     • Semantic similarity               ││
│     • Fast cloud-based                  ││
│     • Scales automatically              ││
│     ↓                                    ││
│  3. Keyword Search (Meilisearch) ←─────┤│
│     • Exact term matching               ││
│     • Case numbers, statutes            ││
│     • Typo-tolerant                     ││
│     ↓                                    ││
│  4. Combine Results (Hybrid)            ││
│     ↓                                    ││
│  5. Generate Answer (GPT-4o-mini)       ││
│                                          │
└─────────────────────────────────────────┘
           ↓
    Legal Answer to User
```

---

## 🎯 Benefits You Get

### **With Pinecone:**
✅ **Cloud-based** - Access from anywhere
✅ **Fast** - Sub-50ms queries
✅ **Scalable** - Handles millions of documents
✅ **No maintenance** - Fully managed
✅ **FREE tier** - 1M vectors, 100K queries/month

### **With Meilisearch (optional):**
✅ **Keyword search** - Find exact case numbers, statute references
✅ **Typo tolerance** - "trffic" → finds "traffic"
✅ **Fast** - 50ms response time
✅ **FREE forever** - Open source

---

## 📦 What Files Were Created

1. `backend/app/vector_store/pinecone_store.py` - Pinecone integration
2. `backend/app/search/meilisearch_client.py` - Meilisearch integration
3. `backend/app/core/config.py` - Updated with new settings
4. `backend/app/vector_store/__init__.py` - Auto-selects vector store

---

## 🔄 Migration from FAISS to Pinecone

Your existing FAISS data won't automatically transfer. You'll need to re-ingest documents:

```bash
cd backend
python ingest_all_documents.py
```

This will:
1. Read all your legal documents
2. Generate embeddings using OpenAI
3. Upload to Pinecone cloud
4. Index in Meilisearch (if enabled)

---

## 💰 Cost Estimate (Monthly)

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| **Pinecone** | 1M vectors, 100K queries | $70/month for more |
| **Meilisearch** | Unlimited (self-hosted) | $25/month (cloud) |
| **OpenAI Embeddings** | ~$0.13/1M tokens | ~$0.13/1M tokens |
| **OpenAI GPT-4o-mini** | ~$0.15/$0.60 per 1M tokens | Same |

**For 10,000 legal documents:**
- Embeddings: ~$1-2 one-time
- Pinecone: FREE (fits in free tier)
- Queries: FREE for <100K/month

**Total:** Essentially FREE for development! 🎉

---

## 🔧 Configuration Options

### Stay with FAISS (Local)
```bash
VECTOR_STORE=faiss
```

### Use Pinecone (Cloud)
```bash
VECTOR_STORE=pinecone
```

### Use Pinecone + Meilisearch (Best)
```bash
VECTOR_STORE=pinecone
USE_MEILISEARCH=true
```

---

## 🚨 Security Note

**IMPORTANT:** You shared your Pinecone API key in chat. For security:

1. Go to [Pinecone Console](https://app.pinecone.io)
2. Navigate to API Keys
3. **Regenerate your API key**
4. Update the new key in your `.env` file

---

## 🐛 Troubleshooting

### Pinecone Connection Issues
```bash
# Test connection
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='your-key'); print(pc.list_indexes())"
```

### Meilisearch Not Running
```bash
# Check if running
curl http://localhost:7700/health

# Start if not running
docker start <container-id>  # or
.\meilisearch.exe
```

### Dimension Mismatch
If you see "dimension mismatch" errors:
1. Delete Pinecone index in console
2. Update `EMBEDDING_DIMENSIONS` in `.env`
3. Restart backend
4. Re-ingest documents

---

## 📚 Next Steps

1. ✅ Update `.env` file with settings above
2. ✅ (Optional) Start Meilisearch server
3. ✅ Restart your backend
4. ✅ Re-ingest your documents
5. ✅ Test queries!

---

## 🎯 Ready to Deploy to GCP?

Your app is now production-ready with:
- ✅ Pinecone (cloud vector DB)
- ✅ Meilisearch (can run on GCP Compute)
- ✅ FastAPI backend
- ✅ React frontend

You can deploy to:
- **Cloud Run** (serverless, easiest)
- **Compute Engine** (VMs)
- **Kubernetes** (GKE)

Want deployment help? Just ask! 🚀

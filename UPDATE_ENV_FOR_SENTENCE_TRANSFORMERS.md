# 📝 Update .env for Sentence Transformers

## Add These Lines to `backend/.env`

Open `backend/.env` and add these lines:

```env
# Embedding Provider - Switch to Sentence Transformers
EMBEDDING_PROVIDER=sentence_transformers

# Sentence Transformer Model
# Options:
#   all-MiniLM-L6-v2 (384 dim, fast, recommended)
#   all-mpnet-base-v2 (768 dim, better quality, slower)
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

---

## Complete .env Example

Your `.env` should look like:

```env
# OpenAI API Key (still needed for chat/LLM)
OPENAI_API_KEY=your-openai-api-key-here

# Embedding Provider - Use Sentence Transformers (FREE, local)
EMBEDDING_PROVIDER=sentence_transformers
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2

# LLM Provider (still use OpenAI for chat responses)
LLM_PROVIDER=openai
OPENAI_CHAT_MODEL=gpt-4o
```

---

## What This Does

- **Embeddings:** Uses Sentence Transformers (local, free)
- **Chat/LLM:** Still uses OpenAI (for generating answers)
- **Result:** Free embeddings + OpenAI for chat

---

## After Updating .env

1. **Restart backend** (to load new settings)
2. **Delete old index** (different dimensions):
   ```bash
   rm backend/data/faiss/index.faiss
   rm backend/data/faiss/metadata.jsonl
   ```
3. **Re-ingest documents** (with new embeddings)

---

**Add those 2 lines to `.env` and restart!** 🚀


# Testing Backend with PEI Highway Traffic Act

This guide will help you test if your backend can answer questions about maximum penalties in the PEI Highway Traffic Act.

## Prerequisites

1. **Azure credentials** - You need:
   - Azure OpenAI endpoint and API key
   - Azure AI Search endpoint and API key

2. **Backend dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

## Step 1: Set Up Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
AZURE_OPENAI_EMBEDDING_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_MODEL=gpt-4
AZURE_OPENAI_CHAT_API_VERSION=2024-02-15-preview

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-azure-search-key
AZURE_SEARCH_INDEX_NAME=legal-documents-index

# Optional: Azure Blob Storage (can skip for testing)
USE_AZURE_STORAGE=false

# RAG Configuration
RAG_TOP_K=10
PARENT_CHUNK_SIZE=2000
PARENT_CHUNK_OVERLAP=200
CHILD_CHUNK_SIZE=500
CHILD_CHUNK_OVERLAP=50
```

## Step 2: Start the Backend

Open a terminal in the `backend/` directory and run:

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## Step 3: Run the Test Script

Open another terminal and run:

```bash
cd backend
python test_pei_query.py
```

## What the Test Does

1. **Checks backend health** - Verifies the API is running
2. **Ingests PEI PDF** - Uploads and processes the PEI Highway Traffic Act PDF
3. **Queries for maximum penalties** - Asks multiple questions:
   - "What is the maximum penalty or fine in the PEI Highway Traffic Act?"
   - "What is the biggest or most serious offence in Prince Edward Island Highway Traffic Act?"
   - "What is the maximum imprisonment term for traffic offences in PEI?"
4. **Shows results** - Displays the AI's answer and source citations

## Expected Output

You should see:
- ✅ Backend is running
- ✅ PDF ingested successfully (with chunk count)
- ✅ Answers to your questions with source citations
- 📚 List of sources used (documents, pages, scores)

## Manual Testing via API

You can also test manually using curl or Postman:

### 1. Check Health
```bash
curl http://localhost:8000/health
```

### 2. Ingest PDF
```bash
curl -X POST "http://localhost:8000/api/ingest/file" \
  -F "file=@../CANADA TRAFFIC FILES/pei_highway_traffic_act.pdf" \
  -F "organization=PEI Government" \
  -F "subject=Highway Traffic Act"
```

### 3. Query for Maximum Penalties
```bash
curl -X POST "http://localhost:8000/api/query/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the maximum penalty or fine in the PEI Highway Traffic Act?",
    "top_k": 10
  }' \
  -G --data-urlencode "hybrid=true" \
  --data-urlencode "include_parent=true"
```

### 4. View API Docs
Open in browser: http://localhost:8000/docs

## Troubleshooting

### Backend won't start
- Check that `.env` file exists and has correct Azure credentials
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check for port conflicts (port 8000 already in use)

### PDF ingestion fails
- Verify PDF file exists at: `../CANADA TRAFFIC FILES/pei_highway_traffic_act.pdf`
- Check Azure AI Search index exists (will be created automatically)
- Verify Azure OpenAI API key is valid

### No answers returned
- Check that PDF was ingested successfully (look for doc_id)
- Verify Azure AI Search has documents indexed
- Check Azure OpenAI API quota/limits

### Answers are not accurate
- Try increasing `top_k` (e.g., 15 or 20)
- Check if parent-child chunking is working
- Verify the PDF text was extracted correctly

## Success Criteria

Your backend is working correctly if:
- ✅ PDF is ingested without errors
- ✅ Queries return relevant answers
- ✅ Answers cite specific sources (documents, pages)
- ✅ Answers mention maximum penalties/fines
- ✅ Answers are grounded in the PEI Highway Traffic Act content


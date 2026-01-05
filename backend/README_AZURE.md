# PLAZA-AI Legal RAG Backend - Azure AI Search Edition

Production-style embedding + RAG backend using **Azure AI Search** with HNSW vector search and parent-child chunking, deployable on GCP.

## Architecture

- **Embedding Model**: Azure OpenAI `text-embedding-ada-002` (1536 dimensions)
- **Vector Database**: Azure AI Search with HNSW indexing
- **Chunking Strategy**: Parent-child hierarchical chunking
  - Parent chunks: 2000 chars, 200 overlap (reference only, no vectors)
  - Child chunks: 500 chars, 50 overlap (with vectors, searchable)
- **Document Storage**: Azure Blob Storage (optional) or local
- **Search**: Hybrid search (vector + text) with parent context expansion

## Features

✅ **Parent-Child Chunking**: Hierarchical document structure for better context retrieval  
✅ **HNSW Vector Search**: Fast approximate nearest neighbor search  
✅ **Hybrid Search**: Combines vector similarity with text search  
✅ **Parent Context Expansion**: Automatically retrieves parent chunks for child results  
✅ **Azure Blob Storage Integration**: Download PDFs directly from Azure Storage  
✅ **GCP Deployable**: Works on GCP while using Azure services  

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required Azure credentials:
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_SEARCH_ENDPOINT` - Your Azure AI Search endpoint
- `AZURE_SEARCH_API_KEY` - Your Azure AI Search API key
- `AZURE_SEARCH_INDEX_NAME` - Name of your search index

Optional (for blob storage):
- `AZURE_STORAGE_ACCOUNT` - Storage account name
- `AZURE_STORAGE_CONTAINER` - Container name
- `USE_AZURE_STORAGE=true` - Enable blob storage

## Running the Server

```bash
# Development mode
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Usage

### 1. Ingest Text with Parent-Child Chunking

```bash
curl -X POST "http://localhost:8000/api/ingest/text?organization=Ontario&subject=Traffic%20Law" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your legal document text here...",
    "source_name": "Ontario Highway Traffic Act Section 128",
    "tags": ["traffic", "ontario"]
  }'
```

### 2. Ingest PDF File

```bash
curl -X POST "http://localhost:8000/api/ingest/file?subject=Traffic%20Violations" \
  -F "file=@document.pdf"
```

### 3. Ask Questions with Hybrid Search

```bash
curl -X POST "http://localhost:8000/api/query/answer?hybrid=true&include_parent=true" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the penalties for speeding 30 km/h over the limit in Ontario?",
    "top_k": 10
  }'
```

### 4. Vector-Only Search

```bash
curl -X POST "http://localhost:8000/api/query/search?hybrid=false" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "speeding ticket demerit points",
    "top_k": 5
  }'
```

## Parent-Child Chunking

The system uses a hierarchical chunking strategy:

1. **Parent Chunks** (2000 chars, 200 overlap):
   - Store full context sections
   - No vectors (reference only)
   - Used for context expansion

2. **Child Chunks** (500 chars, 50 overlap):
   - Smaller, searchable segments
   - Have vectors for similarity search
   - Linked to parent chunks

**Benefits**:
- Better context retrieval (parent chunks provide full context)
- More precise search (child chunks are fine-grained)
- Automatic context expansion (retrieve parent when child matches)

## Azure AI Search Index Schema

The index is automatically created with this structure:

```json
{
  "id": "unique-id",
  "content": "full text content",
  "parent_id": "parent-reference",
  "child_id": "child-reference",
  "subject": "document subject",
  "is_config": false,
  "source": "filename.pdf",
  "page": 1,
  "organization": "Organization name",
  "vector": [0.123, 0.456, ...]  // 1536 dimensions
}
```

## Vector Search Configuration

- **Profile**: `hnsw-vector-profile`
- **Algorithm**: HNSW (Hierarchical Navigable Small World)
- **Distance**: Cosine similarity (default)
- **Dimensions**: 1536 (text-embedding-ada-002)

## GCP Deployment

This backend can be deployed on GCP (Cloud Run, GKE, etc.) while using Azure services:

1. **Set environment variables** in GCP (Secret Manager or Cloud Run env vars)
2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy plaza-ai-backend \
     --source . \
     --region us-central1 \
     --set-env-vars AZURE_OPENAI_ENDPOINT=...,AZURE_SEARCH_ENDPOINT=...
   ```

3. **Or use GKE** with Azure credentials stored in Kubernetes secrets

## Configuration

Key settings in `.env`:

```env
# Parent-child chunking
PARENT_CHUNK_SIZE=2000
PARENT_CHUNK_OVERLAP=200
CHILD_CHUNK_SIZE=500
CHILD_CHUNK_OVERLAP=50
USE_PARENT_CHILD=true

# Search
RAG_TOP_K=10
BATCH_SIZE=100
EMBEDDING_DELAY=0.1  # Rate limiting
```

## Differences from FAISS Version

| Feature | FAISS Version | Azure Search Version |
|---------|--------------|---------------------|
| Vector DB | Local FAISS | Azure AI Search |
| Embeddings | OpenAI API | Azure OpenAI |
| Chunking | Simple | Parent-child hierarchical |
| Search | Vector only | Hybrid (vector + text) |
| Storage | Local files | Azure Blob (optional) |
| Scalability | Limited | Enterprise-scale |
| Deployment | Anywhere | GCP/Azure/AWS |

## API Endpoints

- `POST /api/ingest/text` - Ingest text with parent-child chunking
- `POST /api/ingest/file` - Ingest PDF/text files
- `POST /api/ingest/image` - Ingest images with OCR
- `POST /api/query/answer` - RAG question answering (with parent context)
- `POST /api/query/search` - Similarity search only
- `GET /health` - Health check with index stats

## Query Parameters

### Ingest Endpoints
- `organization` - Organization name for content formatting
- `subject` - Document subject/category
- `page` - Page number (for PDFs)

### Query Endpoints
- `hybrid` - Use hybrid search (vector + text) - default: true
- `include_parent` - Include parent context for child chunks - default: true

## Example: Complete Workflow

```python
# 1. Ingest document
POST /api/ingest/text
{
  "text": "In Ontario, speeding 30 km/h over carries 4 demerit points...",
  "source_name": "Ontario HTA",
  "tags": ["traffic", "ontario"]
}
?organization=Ontario&subject=Traffic%20Law

# 2. Query with parent context
POST /api/query/answer
{
  "question": "What are demerit points for speeding?",
  "top_k": 10
}
?hybrid=true&include_parent=true

# Response includes:
# - Answer from LLM
# - Child chunks (precise matches)
# - Parent chunks (full context)
```

## Troubleshooting

### Index Creation Fails
- Ensure Azure AI Search service exists
- Check API key permissions
- Verify endpoint URL format

### Embedding Generation Fails
- Verify Azure OpenAI endpoint and key
- Check API version compatibility
- Ensure model name matches (`text-embedding-ada-002`)

### Parent Context Not Retrieved
- Check `include_parent=true` in query
- Verify parent_id links in documents
- Ensure parent documents were uploaded

## Next Steps

- Add semantic ranking for better relevance
- Implement query expansion
- Add caching for frequent queries
- Implement batch ingestion from Azure Blob Storage
- Add monitoring and analytics


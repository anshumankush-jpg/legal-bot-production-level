# PLAZA-AI Legal RAG Backend

Production-style embedding + RAG backend for legal document analysis, built with FastAPI, OpenAI embeddings, and FAISS.

## Features

- **Embedding Model**: RTLD with SentenceTransformers (all-MiniLM-L6-v2) + CLIP for images
- **Vector Database**: FAISS (local, CPU-based, multi-modal)
- **Document Ingestion**:
  - Plain text, PDF, DOCX, Excel files
  - Images (JPG/PNG) with automatic OCR
  - Automatic offence number extraction
  - Multi-modal content processing
- **RAG Question Answering**: High-quality answers with document citations
- **Offence Number Extraction**: OCR-based extraction from uploaded documents
- **Web Chat Interface**: Upload documents directly in chat with "+" button
- **Modular Architecture**: Easy to extend and upgrade

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (for image processing)

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH or set `TESSERACT_CMD` environment variable

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 3. Set Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
```

## Running the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Usage

### 1. Ingest Text

```bash
curl -X POST "http://localhost:8000/api/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your legal document text here...",
    "source_name": "Ontario Highway Traffic Act Section 128",
    "tags": ["traffic", "ontario"],
    "metadata": {"jurisdiction": "ON", "act": "HTA"}
  }'
```

### 2. Ingest PDF File

```bash
curl -X POST "http://localhost:8000/api/ingest/file" \
  -F "file=@path/to/document.pdf"
```

### 3. Ingest Image (Ticket/Summons)

```bash
curl -X POST "http://localhost:8000/api/ingest/image" \
  -F "file=@path/to/ticket.jpg"
```

### 4. Ask Questions

```bash
curl -X POST "http://localhost:8000/api/query/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the penalties for speeding 30 km/h over the limit in Ontario?",
    "top_k": 8
  }'
```

### 5. Search Similar Content

```bash
curl -X POST "http://localhost:8000/api/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "speeding ticket demerit points",
    "top_k": 5
  }'
```

## API Endpoints

### Health Check
- `GET /health` - Check server and index status

### Ingestion
- `POST /api/ingest/text` - Ingest plain text
- `POST /api/ingest/file` - Ingest PDF or text file
- `POST /api/ingest/image` - Ingest image with OCR

### Query
- `POST /api/query/answer` - Get RAG-based answer
- `POST /api/query/search` - Similarity search only

## Project Structure

```
backend/
  app/
    main.py                 # FastAPI app
    api/
      routes/
        ingest.py          # Ingestion endpoints
        query.py           # Query endpoints
    core/
      config.py            # Settings
      openai_client.py     # OpenAI wrapper
    embeddings/
      embedding_service.py # Embedding generation
    vector_store/
      faiss_store.py       # FAISS implementation
    ocr/
      ocr_service.py       # OCR for images
    rag/
      rag_service.py       # RAG logic
    models/
      schemas.py           # Pydantic models
  data/
    faiss/                 # FAISS index files
    docs/                  # Document storage
  requirements.txt
  README.md
```

## Configuration

All configuration is done via environment variables (see `.env.example`):

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `EMBEDDING_MODEL`: Embedding model (default: `text-embedding-3-small`)
- `CHAT_MODEL`: Chat model for answers (default: `gpt-4o-mini`)
- `RAG_TOP_K`: Number of chunks to retrieve (default: 8)
- `CHUNK_SIZE`: Text chunk size in characters (default: 700)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 100)

## Architecture

1. **Embedding**: Text → OpenAI `text-embedding-3-small` → L2-normalized vectors
2. **Storage**: FAISS IndexFlatIP (inner product) with metadata in JSONL
3. **Retrieval**: Cosine similarity via inner product on normalized vectors
4. **Generation**: OpenAI ChatCompletion with retrieved context

## Legal Disclaimer

This system provides general information only and is NOT legal advice. All answers include appropriate disclaimers. Users should consult licensed lawyers or paralegals for actual legal matters.

## Troubleshooting

### OCR Not Working
- Ensure Tesseract is installed and in PATH
- Check image quality (may need preprocessing)
- Try different image formats

### PDF Extraction Issues
- Install `pdfplumber` (preferred) or `PyPDF2`
- Some PDFs may be image-based (use OCR instead)

### FAISS Index Errors
- Ensure `data/faiss/` directory exists
- Check file permissions
- Index is automatically saved after each ingestion

## Future Enhancements

- Hybrid search (dense + sparse/BM25)
- Reranking models (Cohere Rerank)
- Support for more document types
- Batch ingestion endpoints
- Metadata filtering in queries
- Upgrade to HNSW or IVF indices for larger datasets


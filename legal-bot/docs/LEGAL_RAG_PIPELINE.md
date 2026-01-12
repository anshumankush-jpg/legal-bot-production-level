# Legal RAG Pipeline Documentation

## Overview

The Legal RAG (Retrieval-Augmented Generation) pipeline provides jurisdiction-aware legal Q&A capabilities that are grounded in indexed legal documents. Unlike generic chatbots, this system ensures answers are based only on retrieved legal sources and includes proper citations.

## Architecture

```
User Question → Legal Retrieval → RAG Prompt Builder → LLM → Grounded Answer
      ↓              ↓                        ↓           ↓         ↓
   Filters     Jurisdiction-aware      Citations &     OpenAI    Citations &
   (Country,    Vector Search          Context        Chat API   Disclaimers
    Jurisdiction)
```

## Core Components

### 1. Legal Retrieval Service (`app/legal_retrieval.py`)

**Purpose**: Specialized retrieval for legal documents with jurisdiction filtering.

**Key Features**:
- Uses same SentenceTransformer model (`all-MiniLM-L6-v2`) as indexing
- Jurisdiction-aware filtering (Canada/Ontario, USA/California, etc.)
- Legal metadata extraction (law names, sections, citations)
- Efficient vector similarity search via FAISS

**API**:
```python
# Initialize service
retrieval_service = get_legal_retrieval_service()

# Search with filters
chunks = retrieval_service.search_legal_index(
    query="speeding penalties Ontario",
    k=10,
    filters={'country': 'Canada', 'jurisdiction': 'Ontario'}
)
```

### 2. RAG Prompt Builder (`app/rag_prompt_builder.py`)

**Purpose**: Constructs legal-specific prompts that enforce grounded answers.

**Key Features**:
- System prompts that prohibit hallucinations
- Structured context with document citations
- Token-aware context truncation
- Jurisdiction-aware disclaimers

**Safety Rules**:
- Answers must be grounded in provided documents
- Explicit refusal when context is insufficient
- Mandatory legal disclaimers in all responses

### 3. Legal LLM Client (`app/llm_client.py`)

**Purpose**: Handles OpenAI-compatible API calls with legal-specific configuration.

**Configuration**:
- Temperature: 0.1 (for legal accuracy)
- Model: GPT-4 (configurable via env)
- Automatic fallback responses on API failure
- Timeout and error handling

### 4. Legal Chat API (`app/api/routes/legal_chat.py`)

**Endpoint**: `POST /api/legal/chat`

**Request Format**:
```json
{
  "question": "What are the speeding penalties in Ontario?",
  "country": "Canada",
  "jurisdiction": "Ontario",
  "max_results": 8
}
```

**Response Format**:
```json
{
  "answer": "Based on the Highway Traffic Act, Section 217...",
  "citations": [
    {
      "doc_id": "doc_123",
      "law_name": "Highway Traffic Act",
      "section": "217",
      "citation": "Highway Traffic Act, Section 217, Ontario, Canada",
      "jurisdiction": "Ontario",
      "country": "Canada",
      "page": 45,
      "source_path": "ontario_traffic_act.pdf",
      "relevance_score": 0.89
    }
  ],
  "jurisdiction": "Ontario",
  "country": "Canada",
  "chunks_used": 3
}
```

## Data Processing Pipeline

### Document Ingestion

1. **Text Extraction**:
   - HTML: BeautifulSoup parsing, script/style removal
   - PDF: Multi-method extraction (pdfplumber → PyPDF2 → pypdf → OCR)
   - Tables: Structured table extraction from PDFs

2. **Text Chunking**:
   - Parent-child chunking strategy
   - Configurable chunk sizes (500-2000 chars)
   - Overlapping chunks for context preservation

3. **Embeddings**:
   - SentenceTransformer: `all-MiniLM-L6-v2` (384 dimensions)
   - Local processing (no API costs)
   - Normalized vectors for cosine similarity

4. **Indexing**:
   - FAISS vector database (local storage)
   - Metadata storage with legal classifications
   - Jurisdiction and law name indexing

### Retrieval Process

1. **Query Processing**:
   - Same embedding model as indexing
   - Jurisdiction/country filtering
   - Top-k retrieval with relevance scoring

2. **Context Building**:
   - Citation-formatted document chunks
   - Token-aware context limits
   - Legal metadata inclusion

3. **LLM Generation**:
   - Grounded answer generation
   - Citation preservation
   - Legal disclaimer inclusion

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_CHAT_MODEL=gpt-4o

# Azure OpenAI (alternative)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key

# Legal RAG Settings
EMBEDDING_PROVIDER=sentence_transformers
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSIONS=384
```

### Model Configuration

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dim, fast, accurate)
- **Chat Model**: GPT-4 or GPT-4o (configurable)
- **Temperature**: 0.1 (low for legal accuracy)
- **Max Tokens**: 2000 (sufficient for legal answers)

## Usage Examples

### Basic Legal Question

```python
import requests

response = requests.post("http://localhost:8000/api/legal/chat", json={
    "question": "What are the demerit points for speeding in Ontario?",
    "country": "Canada",
    "jurisdiction": "Ontario"
})

data = response.json()
print(data['answer'])  # Grounded answer with citations
print(data['citations'])  # Source documents used
```

### Jurisdiction Filtering

```python
# Ontario-specific question
response = requests.post("http://localhost:8000/api/legal/chat", json={
    "question": "What is the fine for running a red light?",
    "jurisdiction": "Ontario"
})

# Cross-jurisdiction comparison
response = requests.post("http://localhost:8000/api/legal/chat", json={
    "question": "Compare DUI penalties in Ontario vs California",
    "max_results": 12
})
```

## Testing

### Unit Tests

Run the legal RAG test suite:
```bash
cd backend
python -m pytest tests/test_legal_rag.py -v
```

### Integration Tests

Test end-to-end functionality:
```bash
# Test with mock data
python -m pytest tests/test_legal_rag.py::TestLegalRAGIntegration -v

# Test API endpoints
curl -X POST http://localhost:8000/api/legal/health
```

### Manual Testing

```bash
# Test with real indexed documents
curl -X POST http://localhost:8000/api/legal/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are speeding penalties in Oklahoma?",
    "jurisdiction": "Oklahoma"
  }'
```

## Safety & Accuracy

### Hallucination Prevention

1. **System Prompts**: Explicitly forbid answers not in provided context
2. **Context Validation**: Check for sufficient relevant documents
3. **Fallback Responses**: Clear messages when information is unavailable
4. **Citation Requirements**: All answers must cite sources

### Legal Disclaimers

Every response includes:
> "This is general legal information only, not legal advice. For advice about your specific case, consult a licensed lawyer or paralegal in your jurisdiction."

### Data Validation

- Jurisdiction accuracy checking
- Source document verification
- Citation format validation
- Token limit enforcement

## Performance Considerations

### Indexing Performance

- **Batch Processing**: Embeddings processed in batches of 32
- **Local Models**: No API latency for embeddings
- **Incremental Updates**: New documents can be added without full reindexing

### Query Performance

- **FAISS Search**: Sub-millisecond vector similarity search
- **Filtering**: Post-retrieval filtering for jurisdiction
- **Caching**: Metadata caching for repeated queries

### Token Optimization

- **Context Limits**: 3000 tokens max for context
- **Chunk Selection**: Top-k most relevant chunks
- **Truncation**: Automatic truncation with warnings

## Monitoring & Logging

### Health Checks

```bash
# Overall system health
GET /health

# Legal RAG specific health
GET /api/legal/health
```

### Logging

- Query logging with jurisdiction and performance metrics
- Error tracking for API failures
- Citation validation logging
- Performance monitoring (response times, token usage)

## Future Enhancements

### Advanced Features

1. **Multi-jurisdiction Comparison**: Side-by-side law comparisons
2. **Legal Ontology**: Structured legal concept relationships
3. **Case Law Integration**: Precedent-based answers
4. **Temporal Reasoning**: Law change tracking over time

### Performance Optimizations

1. **Index Sharding**: Split large indexes by jurisdiction
2. **Query Expansion**: Legal synonym expansion
3. **Hybrid Search**: Combine vector + keyword search
4. **Caching Layer**: Frequently asked question caching

### Quality Improvements

1. **Answer Validation**: LLM-based answer quality checking
2. **Source Credibility**: Document authority scoring
3. **Explanation Quality**: Answer comprehensiveness metrics
4. **User Feedback**: Answer rating and improvement system

## Troubleshooting

### Common Issues

1. **"No relevant legal documents found"**
   - Check if documents are indexed: `GET /health`
   - Verify jurisdiction spelling and availability
   - Try broader queries without strict filtering

2. **LLM API Errors**
   - Check API key configuration
   - Verify model availability
   - Check rate limits and quota

3. **Slow Responses**
   - Reduce `max_results` parameter
   - Check index size and search performance
   - Consider index optimization

### Debug Mode

Enable detailed logging:
```python
import logging
logging.getLogger('app.legal_retrieval').setLevel(logging.DEBUG)
logging.getLogger('app.llm_client').setLevel(logging.DEBUG)
```

## API Reference

### Endpoints

- `POST /api/legal/chat` - Legal Q&A with citations
- `GET /api/legal/health` - Legal RAG health check

### Request/Response Schemas

See `app/models/schemas.py` for complete Pydantic models:
- `LegalChatRequest`
- `LegalChatResponse`
- `LegalCitation`

This legal RAG system provides accurate, jurisdiction-aware legal information while maintaining strict safety boundaries and proper legal disclaimers.
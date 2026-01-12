# Quick Start Guide

## 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 2. Set Up Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

## 3. Start the Server

```bash
uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

## 4. Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Ingest Text
```bash
curl -X POST "http://localhost:8000/api/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "In Ontario, speeding 30 km/h over the limit carries 4 demerit points and a fine of $95-$400.",
    "source_name": "Ontario Traffic Law Example",
    "tags": ["traffic", "ontario"]
  }'
```

### Ask a Question
```bash
curl -X POST "http://localhost:8000/api/query/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the penalties for speeding in Ontario?",
    "top_k": 5
  }'
```

## 5. View API Documentation

Open in browser: `http://localhost:8000/docs`

## Next Steps

- Ingest your legal documents (PDFs, text files)
- Upload ticket images for OCR processing
- Query your knowledge base
- Customize prompts and chunking in `app/rag/rag_service.py`


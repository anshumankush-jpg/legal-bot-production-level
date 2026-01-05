# Bulk Document Ingestion Guide

This guide explains how to ingest all your legal documents into the vector database for the RAG system.

## Prerequisites

1. **Backend server must be running**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Required Python packages** (if not already installed):
   ```bash
   pip install requests beautifulsoup4 PyPDF2
   ```

3. **Environment variables configured** (`.env` file):
   - `OPENAI_API_KEY` or `AZURE_OPENAI_API_KEY`
   - `AZURE_SEARCH_ENDPOINT` and `AZURE_SEARCH_API_KEY` (if using Azure AI Search)

## Available Scripts

### 1. Bulk Ingestion Script (Recommended)
**File:** `bulk_ingest_documents.py`

This comprehensive script ingests:
- ✅ PDF files (legal statutes, traffic acts)
- ✅ HTML files (state codes, law portals)
- ✅ JSON files (case studies from paralegal advice dataset)

**Usage:**
```bash
cd backend/scripts
python bulk_ingest_documents.py
```

**What it does:**
1. Searches all legal document directories
2. Extracts text from PDFs, HTML, and JSON files
3. Automatically detects jurisdiction and document type from file paths
4. Ingests documents via the API with proper metadata
5. Shows progress and summary statistics

**Supported directories:**
- `canada criminal and federal law/`
- `CANADA TRAFFIC FILES/`
- `canada_traffic_acts/`
- `canada_criminal_law/`
- `DATA SET/`
- `us_traffic_laws/`
- `usa_criminal_law/`
- `us_state_codes/`
- `paralegal_advice_dataset/`

### 2. HTML-Only Script
**File:** `index_html_documents.py`

For ingesting only HTML files:
```bash
cd backend/scripts
python index_html_documents.py
```

## Manual Ingestion via API

You can also ingest documents manually using the API:

### Ingest a PDF/HTML file:
```bash
curl -X POST "http://localhost:8000/api/ingest/file?organization=Ontario&subject=Traffic%20Law" \
  -F "file=@path/to/document.pdf"
```

### Ingest text directly:
```bash
curl -X POST "http://localhost:8000/api/ingest/text?organization=PEI&subject=Traffic%20Law" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your legal text here...",
    "source_name": "document_name",
    "tags": ["traffic", "pei"]
  }'
```

## What Gets Indexed

Each document is:
1. **Chunked** using parent-child hierarchical chunking:
   - Parent chunks: 2000 characters (for context)
   - Child chunks: 500 characters (for precise search)
2. **Embedded** using OpenAI `text-embedding-ada-002`
3. **Stored** in Azure AI Search (or FAISS if configured)
4. **Tagged** with:
   - Jurisdiction (e.g., "Ontario", "California")
   - Document type (e.g., "traffic", "criminal")
   - File type (e.g., "pdf", "html", "json")

## Metadata Extraction

The script automatically extracts:
- **Organization/Jurisdiction**: From folder names (e.g., "ontario" → "Ontario")
- **Subject**: From file names (e.g., "traffic" → "Traffic Law")
- **Tags**: Combination of jurisdiction, document type, and file type

## Verification

After ingestion, verify documents are indexed:

1. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```
   This shows the total number of documents indexed.

2. **Test with a query:**
   ```bash
   curl -X POST "http://localhost:8000/api/query/answer" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the penalties for speeding in PEI?"}'
   ```

3. **Search documents:**
   ```bash
   curl -X POST "http://localhost:8000/api/query/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "speeding penalties", "top_k": 5}'
   ```

## Troubleshooting

### "Cannot connect to backend API"
- Make sure the backend server is running on port 8000
- Check if the API_BASE_URL in the script matches your server URL

### "PyPDF2 not installed"
- Install: `pip install PyPDF2`

### "BeautifulSoup not installed"
- Install: `pip install beautifulsoup4`

### Documents not appearing in search
- Check that embeddings were generated (check logs)
- Verify Azure AI Search index was created
- Check that documents have sufficient text (>100 characters)

### Rate limiting errors
- The script includes delays between requests
- If you get rate limits, increase the `time.sleep()` delay in the script

## Performance Tips

1. **Batch processing**: Documents are processed in batches of 100 (configurable in `config.py`)

2. **Parallel processing**: For large datasets, consider running multiple instances targeting different directories

3. **Incremental updates**: The script can be run multiple times - it will add new documents without removing existing ones

4. **Monitor progress**: Watch the logs to see which documents are being processed

## Next Steps

After ingestion:
1. Test queries in the frontend chat interface
2. Verify answers cite your documents correctly
3. Check that case studies are referenced when relevant
4. Monitor the `/health` endpoint for index statistics

## Example Output

```
============================================================
Bulk Document Ingestion Script
============================================================
✓ Backend API is running at http://localhost:8000

Searching for documents...

Found documents:
  PDF files: 12
  HTML files: 89
  JSON files: 6
  Total: 107

[1/107] Processing: pei_highway_traffic_act.pdf
✓ Indexed pei_highway_traffic_act.pdf - 1247 chunks

[2/107] Processing: ontario_highway_traffic_act.html
✓ Indexed ontario_highway_traffic_act.html - 892 chunks

...

============================================================
Bulk Ingestion Complete!
Successfully indexed: 105
Failed: 2
============================================================
```


# Quick Start: Ingest Your Legal Documents

This guide will help you quickly get all your legal documents indexed and ready for querying.

## Prerequisites Checklist

- [ ] Backend server is running
- [ ] Environment variables configured (`.env` file)
- [ ] Required packages installed

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `PyPDF2` - For PDF text extraction
- `beautifulsoup4` - For HTML parsing
- `requests` - For API calls
- All other backend dependencies

### 2. Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Keep this terminal open. The server should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Test the Setup (Optional but Recommended)

In a **new terminal**:

```bash
cd backend/scripts
python test_ingestion.py
```

This will:
- ✓ Check if API is running
- ✓ Test ingesting a sample document
- ✓ Test querying the ingested document

If all tests pass, you're ready for bulk ingestion!

### 4. Run Bulk Ingestion

In the same terminal:

```bash
python bulk_ingest_documents.py
```

The script will:
1. Search for all PDF, HTML, and JSON files in your legal document folders
2. Show you how many files it found
3. Ask for confirmation before proceeding
4. Process each file and show progress
5. Display a summary when complete

**Expected output:**
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

Do you want to proceed with ingestion? (yes/no): yes

[1/107] Processing: pei_highway_traffic_act.pdf
✓ Indexed pei_highway_traffic_act.pdf - 1247 chunks
...
```

### 5. Verify Documents Are Indexed

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

Or visit in browser: `http://localhost:8000/health`

You should see the `index_size` showing the number of documents indexed.

### 6. Test with a Query

Test via API:

```bash
curl -X POST "http://localhost:8000/api/query/answer" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the penalties for speeding in PEI?"}'
```

Or use the frontend chat interface at `http://localhost:4200/chat` (if frontend is running).

## Troubleshooting

### "Cannot connect to backend API"
- Make sure the backend server is running (Step 2)
- Check that it's running on port 8000
- Verify no firewall is blocking the connection

### "ModuleNotFoundError: No module named 'PyPDF2'"
- Run: `pip install PyPDF2 beautifulsoup4 requests`

### "No documents found"
- Check that your document folders are in the project root
- Verify folder names match exactly (case-sensitive on Linux/Mac)
- See `bulk_ingest_documents.py` for the expected folder structure

### Documents ingested but queries return "I don't have information"
- Wait a few seconds after ingestion (indexing may take time)
- Check the health endpoint to verify documents are indexed
- Try a more specific query related to your documents
- Check backend logs for any errors

### Rate limiting errors
- The script includes delays, but if you see rate limits:
  - Increase the `time.sleep()` delay in the script
  - Process documents in smaller batches

## What Gets Indexed

The script automatically processes:

**PDF Files:**
- Canadian traffic acts (PEI, Ontario, etc.)
- US state codes
- Legal statutes

**HTML Files:**
- State law portals
- Provincial law websites
- Legal code websites

**JSON Files:**
- Case studies from `paralegal_advice_dataset/`
- Each case becomes a separate indexed document

## Expected Processing Time

- **Small files (< 1MB)**: ~1-2 seconds per file
- **Medium files (1-10MB)**: ~5-10 seconds per file
- **Large files (> 10MB)**: ~30-60 seconds per file

For 100+ documents, expect 10-30 minutes total processing time.

## Next Steps After Ingestion

1. **Test queries** in the frontend chat interface
2. **Verify citations** - answers should cite sources with page numbers
3. **Check case studies** - queries should reference real case examples when available
4. **Monitor performance** - use `/health` endpoint to track index size

## Quick Reference

```bash
# Start backend
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test setup
cd backend/scripts && python test_ingestion.py

# Bulk ingest
cd backend/scripts && python bulk_ingest_documents.py

# Check health
curl http://localhost:8000/health

# Test query
curl -X POST "http://localhost:8000/api/query/answer" \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

## Support

For detailed information, see:
- `backend/scripts/BULK_INGESTION_GUIDE.md` - Comprehensive guide
- `backend/README.md` - Backend documentation
- `backend/README_AZURE.md` - Azure configuration


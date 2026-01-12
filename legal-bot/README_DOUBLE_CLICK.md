# 🖱️ Double-Click to Ingest All Documents

## ✅ Simple Solution

Just **double-click** `INGEST_ALL_DOCUMENTS.bat` and it will:
1. ✅ Check if backend is running (starts it if needed)
2. ✅ Verify your API key is set
3. ✅ Find all documents in the `data/` folder
4. ✅ Ingest all JSON files (demerit tables, guides, tickets, etc.)
5. ✅ Show progress and results

---

## 📁 What Gets Ingested

The script automatically finds and ingests:

### From `data/` folder:
- ✅ **Demerit Tables** (`data/demerit_tables/**/*.json`)
  - Ontario demerit points
  - California demerit points
  - All other jurisdictions

- ✅ **Fight Process Guides** (`data/fight_process_guides/**/*.json`)
  - How to dispute tickets
  - Process steps per jurisdiction

- ✅ **Example Tickets** (`data/example_tickets/*.json`)
  - Sample ticket data
  - Parsed ticket examples

- ✅ **Lawyer Data** (`data/lawyers/*.json`)
  - Lawyer directories
  - Registration information

### From other folders (if they exist):
- PDF files from legal document folders
- HTML files from state code websites
- JSON case studies from paralegal advice dataset

---

## 🚀 How to Use

### Step 1: Make Sure API Key is Set

1. Open `backend/.env`
2. Set your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

### Step 2: Double-Click

**Double-click:** `INGEST_ALL_DOCUMENTS.bat`

That's it! The script will:
- Check everything
- Start backend if needed
- Ingest all documents
- Show you the results

---

## 📊 What You'll See

```
=======================================
  PLAZA-AI - Bulk Document Ingestion
=======================================

[1/4] Checking backend server...
[OK] Backend server is running

[2/4] Checking API key...
[OK] API key found in .env

[3/4] Running bulk ingestion...

Searching in: data
  ✓ Indexed ontario.json - 15 chunks
  ✓ Indexed california.json - 12 chunks
  ✓ Indexed fight_process_ontario.json - 8 chunks
  ...

[4/4] Verification...
[OK] Documents indexed successfully!
```

---

## 🎯 After Ingestion

Once complete, you can:

1. **Go to Chat:** http://localhost:4200/chat
2. **Ask questions like:**
   - "What are the demerit points for speeding in Ontario?"
   - "How do I fight a traffic ticket?"
   - "What happens if I get 3 demerit points?"

3. **The AI will use your ingested documents to answer!**

---

## 🔧 Troubleshooting

### "Backend not running"
- The script will try to start it automatically
- If it fails, manually start: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

### "API key not set"
- Edit `backend/.env` and set `OPENAI_API_KEY=sk-...`
- Get key from: https://platform.openai.com/account/api-keys

### "No documents found"
- Make sure `data/` folder exists
- Check that JSON files are in subfolders
- Script searches recursively, so files can be nested

### "Ingestion failed"
- Check backend logs for errors
- Verify API key is valid
- Make sure backend is accessible at http://localhost:8000

---

## 📝 Files Created

- **`INGEST_ALL_DOCUMENTS.bat`** - Main ingestion script (double-click this!)
- **`START_EVERYTHING.bat`** - Start backend + frontend + browser

---

## ✅ That's It!

**Just double-click `INGEST_ALL_DOCUMENTS.bat` and all your documents will be ingested!** 🎉

No need to run commands manually - everything is automated.


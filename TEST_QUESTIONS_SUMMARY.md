# 5 Legal Questions Test - Federal, Traffic & Criminal Law

## Questions to be Tested

### 1. FEDERAL LAW - Criminal
**Question:** "What are the federal criminal penalties for drug trafficking in Canada?"

**Category:** Federal Criminal Law  
**Focus:** Drug trafficking penalties under Canadian federal law

---

### 2. TRAFFIC LAW - Speeding
**Question:** "What are the penalties for speeding in Ontario?"

**Category:** Regulatory / Traffic Law  
**Focus:** Speeding violations and penalties in Ontario

---

### 3. TRAFFIC LAW - DUI
**Question:** "What happens if I get a DUI ticket in Canada?"

**Category:** Regulatory / Traffic Law (Hybrid with Criminal)  
**Focus:** DUI violations, penalties, and consequences

---

### 4. CRIMINAL LAW - Assault
**Question:** "What is the difference between assault and aggravated assault?"

**Category:** Criminal Law  
**Focus:** Assault charges and their distinctions

---

### 5. FEDERAL LAW - Immigration
**Question:** "What are the federal immigration requirements for permanent residency?"

**Category:** Federal Administrative Law  
**Focus:** Immigration and permanent residency requirements

---

## How to Run the Test

### Step 1: Start the Backend Server

**Option A: Using Python script**
```bash
python start_local_server.py
```

**Option B: Using uvicorn directly**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option C: Using batch file (Windows)**
```bash
START_EVERYTHING.bat
```

### Step 2: Wait for Server to Start
You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 3: Run the Test
**In a NEW terminal window:**
```bash
python test_5_legal_questions.py
```

---

## Expected Output

For each question, you'll see:
- ✅ The question being asked
- ✅ The generated answer from the AI
- ✅ Statistics (citations, chunks used, confidence score)
- ✅ Source citations with filenames and page numbers

---

## What This Tests

1. **Federal Law Coverage** - Can the system answer federal criminal and administrative questions?
2. **Traffic Law Coverage** - Can it handle traffic violations (speeding, DUI)?
3. **Criminal Law Coverage** - Can it explain criminal law concepts?
4. **RAG Performance** - Are relevant documents being retrieved?
5. **Answer Quality** - Are answers accurate and well-cited?

---

## Notes

- Make sure documents have been ingested first (`python ingest_all_documents.py`)
- The backend needs to be running on `http://localhost:8000`
- Each question may take 5-15 seconds to process
- Answers depend on what documents are in your vector store

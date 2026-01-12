# Run 5 Legal Questions Test - Instructions

## 📋 The 5 Questions

### Question 1: FEDERAL LAW (Criminal)
**Question:** "What are the federal criminal penalties for drug trafficking in Canada?"

### Question 2: TRAFFIC LAW (Speeding)
**Question:** "What are the penalties for speeding in Ontario?"

### Question 3: TRAFFIC LAW (DUI)
**Question:** "What happens if I get a DUI ticket in Canada?"

### Question 4: CRIMINAL LAW (Assault)
**Question:** "What is the difference between assault and aggravated assault?"

### Question 5: FEDERAL LAW (Immigration)
**Question:** "What are the federal immigration requirements for permanent residency?"

---

## 🚀 How to Run the Test

### Step 1: Start the Backend Server

**Open a terminal and run:**

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**OR use the batch file (Windows):**
```bash
START_EVERYTHING.bat
```

**Wait until you see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Run the Test Script

**Open a NEW terminal window and run:**

```bash
python test_5_legal_questions.py
```

---

## 📊 What You'll See

For each question, the test will show:

1. **Question Details**
   - Category (Federal/Traffic/Criminal)
   - The actual question
   
2. **Generated Answer**
   - The AI's response based on your legal documents
   
3. **Statistics**
   - Number of citations found
   - Number of document chunks used
   - Confidence score
   
4. **Citations**
   - Source documents
   - Page numbers
   - Relevance scores

---

## ✅ Expected Output Format

```
====================================================================================================
QUESTION 1: FEDERAL LAW
====================================================================================================
Description: Federal criminal law question about drug trafficking
Question: What are the federal criminal penalties for drug trafficking in Canada?
----------------------------------------------------------------------------------------------------

[*] Sending request to http://localhost:8000/api/artillery/chat...
[*] Response Status: 200

====================================================================================================
GENERATED ANSWER:
====================================================================================================
[The AI's answer will appear here based on your ingested documents]

====================================================================================================
STATISTICS:
====================================================================================================
  Citations Found: 5
  Chunks Used: 10
  Confidence Score: 0.856

====================================================================================================
CITATIONS (Sources):
====================================================================================================

  [1] canada_criminal_code_c46.pdf
      Page: 45
      Relevance Score: 0.923

  [2] federal_criminal_law_drugs.pdf
      Page: 12
      Relevance Score: 0.891
...
```

---

## 🔧 Troubleshooting

### Backend Not Starting?
- Check if port 8000 is already in use
- Make sure you're in the `backend` directory
- Check for Python errors in the terminal

### No Answers Generated?
- Make sure documents have been ingested: `python ingest_all_documents.py`
- Check that the vector store has documents: Look for `faiss_artillery_legal_documents_index.bin`
- Verify documents are in the expected directories

### Connection Errors?
- Verify backend is running: `curl http://localhost:8000/health`
- Check firewall settings
- Make sure you're using the correct port (8000)

---

## 📝 Notes

- The test takes about 1-2 minutes to complete all 5 questions
- Each question may take 5-15 seconds to process
- Answers depend on what documents are in your vector store
- Make sure you've ingested documents first!

---

## 🎯 What This Tests

✅ **Federal Law Coverage** - Can answer federal criminal and administrative questions  
✅ **Traffic Law Coverage** - Can handle traffic violations (speeding, DUI)  
✅ **Criminal Law Coverage** - Can explain criminal law concepts  
✅ **RAG Performance** - Are relevant documents being retrieved?  
✅ **Answer Quality** - Are answers accurate and well-cited?

---

**Ready to test? Start the backend, then run `python test_5_legal_questions.py`!**

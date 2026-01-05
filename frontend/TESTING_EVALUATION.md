# Testing the Evaluation UI

## ✅ Prerequisites Check

### 1. Backend Status
- ✅ Backend is running on port 8000
- Verify: `http://localhost:8000/health` should return status

### 2. Frontend Dependencies
Make sure all Angular Material modules are installed:

```bash
cd frontend
npm install
```

Required Material modules (should already be in package.json):
- `@angular/material` (already installed)
- All Material modules are imported in components

## 🚀 Step-by-Step Testing

### Step 1: Start Frontend

```bash
cd frontend
npm start
```

Wait for compilation. You should see:
```
✔ Browser application bundle generation complete.
** Angular Live Development Server is listening on localhost:4200 **
```

### Step 2: Navigate to Evaluation Page

**Option A: Direct URL**
- Open browser: `http://localhost:4200/evaluation`

**Option B: Navigation Menu**
- Look for "Evaluation" link in the top navigation (dev mode only)
- Click it to navigate

### Step 3: Verify Page Loads

You should see:
- ✅ Page title: "System Evaluation – Ontario Tickets"
- ✅ Description text explaining the page
- ✅ "Run All Tests" button
- ✅ 3 test case cards (Test #1, #2, #3)

### Step 4: Run Tests

1. **Click "Run All Tests" button**
   - Button should show "Running Tests..." with hourglass icon
   - Button becomes disabled during execution

2. **Wait for Results**
   - Tests run sequentially (one at a time)
   - Each test calls the backend `/api/query/answer` endpoint
   - Results appear as they complete

3. **Review Results**
   - Each test card shows PASS or FAIL badge
   - Summary bar shows: "X passed, Y failed, Z total"
   - Failures are listed in red boxes
   - Response times are displayed

### Step 5: Examine Individual Tests

For each test case:

**Input Section:**
- Question text
- Ticket data (offence code, description, fine, demerit points)

**Expected Section:**
- Checklist of what should be in the answer
- Required phrases
- Validation criteria

**Actual Section:**
- PASS/FAIL badge (green/red)
- List of failures (if any)
- Response time in milliseconds
- Expandable "View Model Answer" panel

**To see full answer:**
- Click "View Model Answer" expansion panel
- Full LLM response is displayed

## 🐛 Troubleshooting

### Problem: "Evaluation" link not showing

**Solution:**
- Check `frontend/src/environments/environment.ts`
- Ensure `showEvaluation: true`
- Restart frontend dev server

### Problem: Tests fail with "Cannot connect to backend"

**Solution:**
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```
2. Check CORS settings in backend
3. Verify `apiUrl` in `environment.ts` is `http://localhost:8000`

### Problem: All tests show "Error occurred"

**Solution:**
1. Check backend logs for errors
2. Verify OpenAI API key is configured
3. Check that documents are ingested (run bulk ingestion first)
4. Test a simple query in `/chat` to verify backend works

### Problem: Tests pass but answers seem wrong

**Solution:**
- This is expected if documents aren't ingested yet
- Run bulk ingestion: `python backend/scripts/bulk_ingest_documents.py`
- Re-run evaluation tests

### Problem: Design tokens not applying

**Solution:**
- Check browser console for SCSS errors
- Verify `_design-tokens.scss` exists at `frontend/src/styles/_design-tokens.scss`
- Check that `styles.scss` imports the tokens file

## 📊 Understanding Test Results

### PASS Criteria

A test PASSES if:
- ✅ All required phrases are found in answer
- ✅ No forbidden phrases are present
- ✅ Offence is correctly identified
- ✅ Demerit points are correctly stated
- ✅ Both FIGHT and PAY options are mentioned
- ✅ Disclaimer is present

### FAIL Reasons

Common failure reasons:
- ❌ "Missing required phrase: '3 demerit points'"
  - Answer doesn't mention the expected phrase
- ❌ "Offence not clearly identified"
  - Offence code or description not found
- ❌ "Fight/dispute option not mentioned"
  - Option 1 (Fight) not present
- ❌ "Pay option not mentioned"
  - Option 2 (Pay) not present
- ❌ "Disclaimer not present"
  - Legal disclaimer missing

### Improving Results

If tests are failing:

1. **Check Backend Logs:**
   - See what the LLM actually returned
   - Check if retrieval found relevant documents

2. **Ingest More Documents:**
   - Run bulk ingestion
   - Ensure demerit tables are indexed
   - Ensure fight process guides are indexed

3. **Review System Prompt:**
   - Check `backend/app/core/config.py`
   - Verify `LEGAL_ASSISTANT_SYSTEM_PROMPT` is being used

4. **Test Individual Queries:**
   - Use `/chat` page to test queries manually
   - See what the system actually returns

## 🎯 Expected Behavior

### First Run (No Documents Ingested)
- Tests may fail with "I don't have information" messages
- This is expected - you need to ingest documents first

### After Document Ingestion
- Tests should pass if:
  - Documents contain relevant information
  - System prompt is correctly configured
  - Backend is working properly

### Ideal Results
- All 3 tests PASS
- Response times < 5 seconds
- Answers include all required elements
- No forbidden phrases

## 📝 Next Steps After Testing

1. **If tests fail:**
   - Review failure reasons
   - Check backend logs
   - Ingest more relevant documents
   - Adjust system prompt if needed

2. **If tests pass:**
   - Add more test cases
   - Test with different jurisdictions
   - Add edge cases
   - Set up automated testing

3. **Improve system:**
   - Use evaluation results to improve prompts
   - Add missing data to knowledge base
   - Refine retrieval parameters

---

## 🚀 Quick Test Command

```bash
# Terminal 1: Backend (if not running)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm start

# Browser
# Open: http://localhost:4200/evaluation
# Click: "Run All Tests"
```

---

**Ready to test! Follow the steps above and review the results.** 🎯


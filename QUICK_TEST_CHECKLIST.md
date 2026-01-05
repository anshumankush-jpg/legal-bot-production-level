# Quick Test Checklist - Evaluation UI

## ✅ Pre-Flight Check

- [ ] Backend running on port 8000
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Environment shows evaluation: `showEvaluation: true`

## 🚀 Test Steps

### 1. Start Frontend
```bash
cd frontend
npm start
```
✅ Wait for: `Angular Live Development Server is listening on localhost:4200`

### 2. Open Evaluation Page
- Navigate to: `http://localhost:4200/evaluation`
- OR click "Evaluation" in navigation bar

### 3. Verify Page Elements
You should see:
- [ ] Page title: "System Evaluation – Ontario Tickets"
- [ ] "Run All Tests" button
- [ ] 3 test case cards visible
- [ ] Summary area (empty initially)

### 4. Run Tests
- [ ] Click "Run All Tests"
- [ ] Button shows "Running Tests..." (disabled)
- [ ] Tests execute one by one
- [ ] Results appear as they complete

### 5. Review Results
For each test, check:
- [ ] PASS/FAIL badge appears (green/red)
- [ ] Failures listed (if any)
- [ ] Response time shown
- [ ] "View Model Answer" expandable
- [ ] Summary shows: "X passed, Y failed, 3 total"

## 📊 What Success Looks Like

### Best Case Scenario
```
Summary: 3 passed, 0 failed, 3 total
```
- All tests show green PASS badges
- No failures listed
- Answers include all required elements

### Expected First Run (No Documents)
```
Summary: 0 passed, 3 failed, 3 total
```
- Tests fail with "I don't have information"
- This is normal - need to ingest documents first

### After Document Ingestion
```
Summary: 2-3 passed, 0-1 failed, 3 total
```
- Most tests should pass
- Some may fail if documents don't cover that specific scenario

## 🔍 Debugging Tips

### If Tests Don't Run
1. Check browser console (F12) for errors
2. Check network tab - are API calls being made?
3. Verify backend is responding: `http://localhost:8000/health`

### If All Tests Fail
1. Check backend logs for errors
2. Verify OpenAI API key is set
3. Test a simple query in `/chat` first
4. Check if documents are ingested

### If Tests Pass But Answers Are Wrong
1. Review actual answers in "View Model Answer"
2. Check if relevant documents are in the knowledge base
3. Verify system prompt is correct
4. Check retrieval scores (should be > 0.7)

## 🎯 Next Actions

**If tests pass:**
- ✅ System is working correctly
- Add more test cases
- Test with real tickets

**If tests fail:**
- Review failure reasons
- Ingest more documents
- Adjust system prompt
- Improve retrieval parameters

---

**Ready to test!** 🚀


# 🚀 Quick Start: Run Complex Question Tests

## ✅ Current Status

- ✅ Backend is running on port 8000
- ✅ .env file updated with optimal settings
- ⚠️ OpenAI API key needs to be added

## 📝 Step 1: Add Your OpenAI API Key

**Edit `backend/.env` file and add your API key:**

```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

Get your API key from: https://platform.openai.com/api-keys

## 🔄 Step 2: Restart Backend (to load new .env)

**Stop the current backend** (Ctrl+C in the terminal where it's running)

**Then restart it:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 Step 3: Run Complex Question Tests

**In a new terminal:**
```bash
python test_complex_legal_questions.py
```

## 📊 What to Expect

The test will:
1. ✅ Check backend health
2. ✅ Ask 10 complex legal questions
3. ✅ Analyze answer quality
4. ✅ Show performance metrics
5. ✅ Save results to `complex_test_results.json`

**Example output:**
```
================================================================================
COMPLEX LEGAL QUESTION TESTING
================================================================================
[OK] Backend is running

TEST 1/10: Criminal Law - DUI
[ASKING] What are the specific penalties for a first-time DUI offense...
[OK] Response received in 3.45s
[INFO] Chunks used: 5
[INFO] Confidence: 0.852
[QUALITY] GOOD (Score: 0.85)
[TOPICS] Found: 6/7
...
```

## 🎯 Success Criteria

- ✅ All 10 questions answered successfully
- ✅ Average quality score > 0.7 (GOOD)
- ✅ Response time < 10 seconds per question
- ✅ Answers contain relevant legal topics

## 🐛 Troubleshooting

**"OPENAI_API_KEY not found"**
- Make sure you added the key to `backend/.env`
- Restart backend after adding key
- Check the key starts with `sk-`

**"Backend is not running"**
- Start backend: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

**"Request timed out"**
- Backend might be slow, increase timeout in test script
- Check backend logs for errors

**"No documents indexed"**
- Upload some legal documents first via the frontend
- Or use the upload API endpoint

---

**Ready?** Add your API key, restart backend, and run the tests! 🎯

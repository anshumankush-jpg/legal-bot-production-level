# 🧪 Testing Instructions - Backend Issues Detected

## ⚠️ Current Issue

**Multiple backend processes detected on port 8000** - This is causing conflicts and timeouts.

## 🔧 Solution: Clean Restart

### Option 1: Use the cleanup script (Recommended)

```bash
cleanup_and_restart.bat
```

This will:
1. Kill all processes on port 8000
2. Wait for port to be free
3. Start backend in a new window

### Option 2: Manual cleanup

**Step 1: Kill all processes on port 8000**
```bash
# Find PIDs
netstat -ano | findstr :8000

# Kill each PID (replace <PID> with actual process ID)
taskkill /F /PID <PID>
```

**Step 2: Start backend fresh**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## ✅ After Backend Starts

**Wait 10-15 seconds** for backend to fully initialize, then:

### Test 1: Quick diagnostic
```bash
python diagnose_and_test.py
```

### Test 2: Single complex question
```bash
python test_single_question.py
```

### Test 3: Full complex question suite
```bash
python test_complex_legal_questions.py
```

## 📋 Prerequisites

Before testing, make sure:

1. ✅ **OpenAI API key is set** in `backend/.env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. ✅ **Backend is running** and responding:
   ```bash
   curl http://localhost:8000/health
   ```

3. ✅ **Documents are indexed** (optional but recommended):
   - Upload some legal documents via frontend
   - Or use the upload API

## 🎯 Expected Test Results

- **Backend health**: Should return 200 OK
- **Response time**: < 10 seconds per question
- **Answer quality**: Should contain relevant legal information
- **Topics found**: 70%+ of expected topics

## 🐛 Troubleshooting

**"Backend timed out"**
- Kill all processes on port 8000
- Restart backend
- Wait longer (15-20 seconds) for initialization

**"No documents indexed"**
- Upload documents first
- Or test will return "No documents uploaded yet"

**"API key error"**
- Check `backend/.env` has valid API key
- Restart backend after adding key

---

**Ready?** Run `cleanup_and_restart.bat` first, then test! 🚀

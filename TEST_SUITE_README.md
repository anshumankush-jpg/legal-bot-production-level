# 🧪 Comprehensive Test Suite with Logging

## 📋 What's Been Created

### 1. **Backend Test Suite** (`test_backend_comprehensive.py`)
Tests:
- ✅ Backend health check
- ✅ Root endpoint
- ✅ OpenAI API key configuration
- ✅ Vector store status
- ✅ Simple chat endpoint
- ✅ Complex legal question chat endpoint

### 2. **Frontend/Backend Integration Tests** (`test_frontend_comprehensive.py`)
Tests:
- ✅ Frontend accessibility
- ✅ Backend connectivity from frontend
- ✅ CORS headers
- ✅ Response format validation
- ✅ Direct API endpoint testing

### 3. **Detailed Logging** (Enabled in `backend/app/main.py`)
- ✅ All logs saved to `backend_detailed.log`
- ✅ Console output with file/line numbers
- ✅ DEBUG level logging enabled

### 4. **Log Viewer** (`view_logs.py`)
- ✅ View recent log entries
- ✅ Analyze errors
- ✅ Show test results summary

## 🚀 How to Run Tests

### Option 1: Run All Tests (Recommended)
```bash
RUN_TESTS_AND_VIEW_LOGS.bat
```

### Option 2: Run Tests Individually

**Backend Tests:**
```bash
python test_backend_comprehensive.py
```

**Frontend/Backend Integration:**
```bash
python test_frontend_comprehensive.py
```

**View Logs:**
```bash
python view_logs.py
```

## 📊 What the Tests Will Show

### Backend Tests Will Check:
1. **Backend Health** - Is it running?
2. **API Key** - Is OpenAI key configured and working?
3. **Vector Store** - Are documents indexed?
4. **Chat Endpoint** - Can it answer questions?
5. **Response Quality** - Are answers detailed and accurate?

### Frontend Tests Will Check:
1. **Frontend Access** - Can you reach the UI?
2. **Backend Connection** - Can frontend reach backend?
3. **CORS** - Are headers configured correctly?
4. **Response Format** - Is data structure correct?

## 📝 Log Files Generated

1. **`backend_detailed.log`** - All backend logs with timestamps
2. **`backend_test_results.json`** - Backend test results
3. **`frontend_test_results.json`** - Frontend test results

## 🔍 How to Identify Problems

### Step 1: Run Tests
```bash
python test_backend_comprehensive.py
```

### Step 2: Check Logs
```bash
python view_logs.py
```

### Step 3: Look for:
- **"Backend Health: FAIL"** → Backend not running
- **"OpenAI API Key: FAIL"** → API key issue
- **"Chat Endpoint: FAIL"** → Backend processing issue
- **"CORS Headers: FAIL"** → Frontend can't connect
- **"Response Format: FAIL"** → Data structure issue

## 🎯 Expected Test Results

**If everything works:**
```
[OK] Backend Health: PASS
[OK] Root Endpoint: PASS
[OK] OpenAI API Key: PASS
[OK] Vector Store: PASS
[OK] Simple Chat: PASS
[OK] Complex Chat: PASS
Success Rate: 100.0%
```

**If backend not running:**
```
[FAIL] Backend Health: FAIL
   Cannot connect - backend not running
```

**If API key issue:**
```
[FAIL] OpenAI API Key: FAIL
   API key not found or invalid format
```

## ⚠️ Important Notes

1. **Backend must be running** for tests to work
2. **Start backend first:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. **Wait 15-20 seconds** after starting backend before running tests
4. **Check logs** if tests fail to see exact error messages

## 📋 Quick Diagnostic Flow

1. **Run backend tests** → See what's failing
2. **Check logs** → See detailed error messages
3. **Fix issues** → Based on log errors
4. **Re-run tests** → Verify fixes
5. **Test frontend** → Once backend works

---

**Ready to diagnose!** Run the tests and check the logs! 🔍

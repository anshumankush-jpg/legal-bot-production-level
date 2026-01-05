# 🧪 Test Suite and Logging Setup

## ✅ What's Been Created

### Test Files

1. **`test_backend_comprehensive.py`** — Backend test suite
   - Tests 6 backend components
   - Shows detailed results
   - Saves results to JSON (`backend_test_results.json`)

2. **`test_frontend_comprehensive.py`** — Frontend/backend integration tests
   - Tests frontend connectivity
   - Tests API integration
   - Validates response formats
   - Saves results to JSON (`frontend_test_results.json`)

3. **`view_logs.py`** — Log viewer and analyzer
   - Shows recent log entries (last 100 lines)
   - Analyzes errors
   - Displays test summaries

### Batch Scripts

4. **`RUN_TESTS_AND_VIEW_LOGS.bat`** — Run all tests at once
   - Runs backend tests
   - Runs frontend/backend integration tests
   - Views logs and results

5. **`QUICK_DIAGNOSTIC.bat`** — Quick problem finder
   - Checks if backend is running
   - Tests backend API
   - Checks logs
   - Tests frontend connection

## 📝 Logging Enabled

### Detailed Logging Configuration

**Location:** `backend/app/main.py`

- ✅ Detailed logging enabled
- ✅ All logs saved to `backend_detailed.log`
- ✅ Console output with file/line numbers
- ✅ DEBUG level logging for troubleshooting

**Log Format:**
```
%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s
```

**Log File:** `backend_detailed.log` (appends, doesn't overwrite)

## 🔍 Main Problem Identified

**Backend is not running or not responding.**

### Test Results Summary:
- ❌ 5 of 6 tests failed
- ❌ All failures are connection timeouts
- ❌ Backend health check fails

## 🚀 How to Use

### Step 1: Start Backend (with logging)

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Watch the console for errors.** Logs will be saved to `backend_detailed.log`.

### Step 2: Run Tests

**Option A: Run backend tests only**
```bash
python test_backend_comprehensive.py
```

**Option B: Run frontend/backend integration tests**
```bash
python test_frontend_comprehensive.py
```

**Option C: Run everything at once**
```bash
RUN_TESTS_AND_VIEW_LOGS.bat
```

### Step 3: View Logs

```bash
python view_logs.py
```

**Or use the quick diagnostic:**
```bash
QUICK_DIAGNOSTIC.bat
```

## 📊 What the Tests Will Show

Once the backend is running, tests will show:

1. **Which components are working**
   - Backend health check
   - Root endpoint
   - OpenAI API key configuration
   - Vector store status
   - Chat endpoints (simple and complex)
   - Frontend accessibility
   - CORS headers
   - Response format validation

2. **Exact error messages**
   - Connection errors
   - Timeout errors
   - API errors
   - Configuration errors

3. **Response times**
   - API call latency
   - LLM generation time
   - Total request time

4. **Answer quality**
   - Response length
   - Chunks used
   - Confidence scores
   - Content quality metrics

5. **Detailed logs for debugging**
   - File and line numbers
   - Error stack traces
   - Request/response details

## 🧪 Test Details

### Backend Tests (`test_backend_comprehensive.py`)

1. **Backend Health Check** — Tests `/health` endpoint
2. **Root Endpoint** — Tests `/` endpoint
3. **OpenAI Config** — Validates API key configuration
4. **Vector Store** — Checks FAISS index status
5. **Simple Chat** — Tests basic chat functionality
6. **Complex Chat** — Tests complex legal questions with quality metrics

### Frontend/Backend Integration Tests (`test_frontend_comprehensive.py`)

1. **Frontend Accessibility** — Checks if frontend is running
2. **Backend Connectivity** — Tests API connection from frontend perspective
3. **CORS Headers** — Validates CORS configuration
4. **Response Format** — Validates API response structure
5. **API Endpoint** — Direct API endpoint test with detailed metrics

## 📁 Output Files

- `backend_test_results.json` — Backend test results
- `frontend_test_results.json` — Frontend test results
- `backend_detailed.log` — Detailed backend logs

## 💡 Troubleshooting Tips

### Backend Not Starting

1. Check if port 8000 is in use:
   ```bash
   netstat -ano | findstr :8000
   ```

2. Check Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Check for import errors in console output

### Backend Starts But Tests Fail

1. Wait 30-60 seconds for models to load
2. Check `backend_detailed.log` for errors
3. Verify API keys in `backend/.env`
4. Check network connectivity

### All Tests Timeout

1. Backend may not be running — start it first
2. Check firewall settings
3. Verify backend is on `0.0.0.0:8000`
4. Check CORS configuration

## 🎯 Next Steps

1. **Start the backend** (see Step 1 above)
2. **Run the quick diagnostic** to identify issues:
   ```bash
   QUICK_DIAGNOSTIC.bat
   ```
3. **Review the logs** to see exactly where problems occur:
   ```bash
   python view_logs.py
   ```
4. **Fix issues** based on log output
5. **Re-run tests** to verify fixes

---

**The logs will show exactly where the problem is. Start the backend and run the tests to see detailed diagnostic information.**

# 🔧 Fix "Failed to fetch" Error

## Problem
You're seeing: `"Error: Failed to fetch"` when uploading files.

## Root Cause
The frontend can't connect to the backend API endpoints.

---

## ✅ Solution Steps

### Step 1: Verify Backend is Running

**Check if backend is running:**
```bash
# In a new terminal, check:
curl http://localhost:8000
```

Or visit: http://localhost:8000/docs

**If not running, start it:**
```bash
python api_server.py
```

### Step 2: Wait for Models to Load

**Backend needs 30-60 seconds to load:**
- SentenceTransformer model (~80MB)
- CLIP model (~150MB) 
- FAISS initialization

**Look for this message:**
```
[+] Unified Embedding Server initialized!
```

### Step 3: Verify Endpoints Exist

**Check API docs:**
Visit: http://localhost:8000/docs

**You should see:**
- ✅ `POST /api/artillity/upload`
- ✅ `POST /api/artillity/search`

**If you DON'T see these:**
- Backend was started before endpoints were added
- **Solution**: Restart backend

### Step 4: Test Connection

**Run test script:**
```bash
python test_connection.py
```

**Or test manually:**
```bash
# Test upload endpoint
curl -X POST http://localhost:8000/api/artillity/upload \
  -F "file=@sample_data/sample_texts.txt"
```

### Step 5: Check CORS

**CORS is already enabled** in `api_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    ...
)
```

**If still having issues**, check browser console (F12) for CORS errors.

---

## 🔍 Common Issues

### Issue 1: Backend Not Running
**Symptom**: "Failed to fetch" immediately

**Fix**: Start backend
```bash
python api_server.py
```

### Issue 2: Endpoints Not Loaded
**Symptom**: 404 errors

**Fix**: Restart backend to load new endpoints

### Issue 3: Models Still Loading
**Symptom**: Timeout or slow response

**Fix**: Wait 30-60 seconds, then try again

### Issue 4: Port Conflict
**Symptom**: "Address already in use"

**Fix**: 
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID)
taskkill /PID <PID> /F

# Restart backend
python api_server.py
```

---

## ✅ Quick Verification

### Test 1: Backend Health
```bash
curl http://localhost:8000
```
**Expected**: JSON response with status

### Test 2: Artillity Endpoints
```bash
curl http://localhost:8000/docs
```
**Expected**: Swagger UI page

### Test 3: Upload Test
```bash
python test_connection.py
```
**Expected**: Files upload successfully

---

## 🚀 Complete Restart Procedure

If nothing works, do a complete restart:

1. **Stop everything:**
   ```bash
   # Stop backend (Ctrl+C in terminal)
   # Stop frontend (Ctrl+C in terminal)
   ```

2. **Start backend:**
   ```bash
   python api_server.py
   ```
   Wait for: `[+] Unified Embedding Server initialized!`

3. **Start frontend:**
   ```bash
   cd frontend
   python -m http.server 5500
   ```

4. **Open browser:**
   - Go to: http://localhost:5500
   - Refresh (F5)

5. **Test upload:**
   - Upload a small file first (like `sample_texts.txt`)
   - Wait for success message

---

## 📝 Debug Checklist

- [ ] Backend is running (`python api_server.py`)
- [ ] Backend shows "Server ready!" message
- [ ] Can access http://localhost:8000/docs
- [ ] Artillity endpoints visible in docs
- [ ] Frontend is running (http://localhost:5500)
- [ ] Browser console shows no CORS errors
- [ ] Tried refreshing browser (F5)
- [ ] Waited 30-60 seconds after backend start

---

## 🎯 Expected Behavior

**When working correctly:**
1. Upload file → Shows "Processing..."
2. After 10-30 seconds → Shows "✓ indexed"
3. Search query → Shows results with sources

**If you see this, everything is working!** ✅

---

**Most common fix: Restart backend and wait 30 seconds!** 🔄


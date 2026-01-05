# 🔧 Troubleshooting "Failed to fetch" Error

## 🎯 Quick Fix

**The error "Failed to fetch" means the frontend can't reach the backend.**

### ✅ Solution (3 steps):

1. **Start Backend:**
   ```bash
   python api_server.py
   ```
   Wait for: `[+] Unified Embedding Server initialized!`

2. **Wait 30-60 seconds** for models to load

3. **Refresh browser** at http://localhost:5500

---

## 🔍 Why This Happens

### Common Causes:

1. **Backend Not Running**
   - Most common cause
   - Backend process stopped or crashed
   - **Fix**: Start backend again

2. **Backend Still Loading**
   - Models take 30-60 seconds to load
   - Endpoints not ready yet
   - **Fix**: Wait longer, then refresh

3. **Endpoints Not Registered**
   - Backend started before endpoints were added
   - **Fix**: Restart backend

4. **Port Conflict**
   - Another app using port 8000
   - **Fix**: Kill conflicting process

---

## ✅ Step-by-Step Fix

### Step 1: Check if Backend is Running

**Open a new terminal and run:**
```bash
curl http://localhost:8000
```

**Expected**: JSON response
**If error**: Backend not running

### Step 2: Start Backend

```bash
cd "C:\Users\anshu\OneDrive\Documents\project\EMEEDING MODLEL-GPT"
python api_server.py
```

**Look for these messages:**
```
[*] Initializing Unified Embedding Server...
[*] Loading text embedding model...
[*] Loading image embedding model...
[*] Initializing FAISS vector database...
[+] Unified Embedding Server initialized!
```

### Step 3: Verify Endpoints

**Wait 30 seconds, then visit:**
http://localhost:8000/docs

**You should see:**
- ✅ `POST /api/artillity/upload`
- ✅ `POST /api/artillity/search`

**If you DON'T see these:**
- Backend needs restart
- Endpoints weren't loaded

### Step 4: Test Upload

**Run test script:**
```bash
python test_connection.py
```

**Or test manually:**
```bash
# Upload a test file
curl -X POST http://localhost:8000/api/artillity/upload \
  -F "file=@sample_data/sample_texts.txt"
```

### Step 5: Refresh Frontend

1. Go to: http://localhost:5500
2. Press **F5** to refresh
3. Try uploading again

---

## 🚀 Easy Way: Use Batch File

**I created `START_BOTH_SERVERS.bat` for you!**

Just double-click it, and it will:
1. Start backend in one window
2. Start frontend in another window
3. Show you the URLs

**Then:**
- Wait 30-60 seconds
- Refresh browser
- Upload files!

---

## 🔍 Debug Steps

### Check Backend Status
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
```

### Check Python Processes
```bash
# See all Python processes
tasklist | findstr python
```

### Check Browser Console
1. Open browser (F12)
2. Go to Console tab
3. Look for errors
4. Common errors:
   - "Failed to fetch" → Backend not running
   - "CORS error" → CORS not enabled (but it is)
   - "404" → Endpoint not found

---

## ✅ Verification Checklist

Before uploading files, verify:

- [ ] Backend terminal shows "Server ready!"
- [ ] Can access http://localhost:8000/docs
- [ ] Artillity endpoints visible in docs
- [ ] Frontend is at http://localhost:5500
- [ ] Browser console (F12) shows no errors
- [ ] Waited 30-60 seconds after backend start

---

## 🎯 Expected Success Flow

1. **Backend starts** → Shows initialization messages
2. **Models load** → Takes 30-60 seconds
3. **Server ready** → Shows "Unified Embedding Server initialized!"
4. **Frontend connects** → No "Failed to fetch" error
5. **Upload works** → Shows "✓ indexed" message
6. **Search works** → Shows results with sources

---

## 💡 Pro Tips

1. **Start backend first**, wait for "ready", then use frontend
2. **Use small files first** to test (like `sample_texts.txt`)
3. **Check browser console** (F12) for detailed errors
4. **Wait patiently** - models take time to load
5. **Restart if needed** - sometimes a clean restart fixes everything

---

## 🆘 Still Not Working?

1. **Check backend terminal** for error messages
2. **Check browser console** (F12) for detailed errors
3. **Try test script**: `python test_connection.py`
4. **Restart everything**: Close all, start fresh
5. **Check ports**: Make sure 8000 and 5500 are free

---

**Most common fix: Restart backend and wait 30 seconds!** 🔄


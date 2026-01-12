# 🔌 Artillity Connection Guide

## ✅ NO API KEYS NEEDED!

**You don't need any API keys!** Artillity uses:
- ✅ **SentenceTransformer** - FREE, runs locally
- ✅ **CLIP** - FREE, runs locally  
- ✅ **FAISS** - FREE, runs locally

**Everything is 100% free and local!**

---

## 📊 Current Status

### ✅ Frontend
- **Status**: Running
- **URL**: http://localhost:5500
- **Action**: Open in browser

### ⚠️ Backend
- **Status**: Starting (models loading)
- **URL**: http://localhost:8000
- **Wait**: 30-60 seconds for models to load

---

## 🚀 Quick Setup

### Step 1: Start Backend
```bash
python api_server.py
```

Wait for: `[+] Unified Embedding Server initialized!`

### Step 2: Open Frontend
Visit: **http://localhost:5500**

### Step 3: Upload Sample Files
1. Click "Choose file..." in left panel
2. Navigate to `sample_data/` folder
3. Select files:
   - `sample_texts.txt`
   - `products.csv`
   - `faq_document.txt`
4. Click "Upload & Index"
5. Wait for "✓ indexed" messages

### Step 4: Ask Questions
Type in the search box (right panel):
- "artificial intelligence"
- "machine learning"
- "how does embedding work"
- "what products are available"

---

## 📝 Sample Questions

See **SAMPLE_QUESTIONS.md** for a complete list!

### Quick Test Questions:
1. **"What is artificial intelligence?"**
2. **"How does embedding work?"**
3. **"What products are available?"**
4. **"What is machine learning in healthcare?"**

---

## 🔍 Troubleshooting

### "Failed to fetch" Error
**Problem**: Backend not ready or not running

**Solution**:
1. Check backend terminal - wait for "Server ready!"
2. Wait 30-60 seconds for models to load
3. Refresh browser (F5)

### "404 Not Found" Error
**Problem**: Artillity endpoints not loaded

**Solution**:
1. Restart backend: `python api_server.py`
2. Wait for initialization
3. Try again

### Files Not Uploading
**Problem**: Backend still loading or timeout

**Solution**:
1. Wait longer (large files take 20-60 seconds)
2. Check backend terminal for errors
3. Try smaller files first

---

## ✅ Verification

### Test Backend
```bash
python test_connection.py
```

### Check Endpoints
Visit: http://localhost:8000/docs

You should see:
- `/api/artillity/upload`
- `/api/artillity/search`

---

## 📁 Sample Files Location

All in `sample_data/` folder:
- `sample_texts.txt` - Healthcare AI articles
- `products.csv` - Product catalog
- `faq_document.txt` - FAQ about server
- `tech_articles.txt` - Technology articles
- `healthcare_data.csv` - Patient data

---

## 🎯 Expected Workflow

1. **Backend starts** → Models load (30-60 sec)
2. **Frontend opens** → http://localhost:5500
3. **Upload files** → Left panel, choose files
4. **Wait for indexing** → See "✓ indexed" messages
5. **Search** → Right panel, type questions
6. **Get results** → See top 3 matches with sources

---

**Everything is FREE and LOCAL - No keys needed!** 🎉


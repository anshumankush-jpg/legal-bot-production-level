# 🔧 Quick Connection Test & Sample Questions

## ✅ NO API KEYS NEEDED!

**Artillity uses:**
- ✅ SentenceTransformer (FREE, local)
- ✅ CLIP (FREE, local)  
- ✅ FAISS (FREE, local)

**No OpenAI key, no vector DB key needed!**

---

## 🔌 Connection Status

### Backend
- **URL**: http://localhost:8000
- **Status**: Needs restart to load Artillity endpoints
- **Action**: Restart backend with `python api_server.py`

### Frontend  
- **URL**: http://localhost:5500
- **Status**: Running
- **Action**: Refresh browser after backend restart

---

## 📤 How to Upload Sample Files

### Option 1: Via Frontend (Easiest)
1. Open http://localhost:5500
2. Click "Choose file..." in left panel
3. Select files from `sample_data/` folder:
   - `sample_texts.txt`
   - `products.csv`
   - `faq_document.txt`
   - `tech_articles.txt`
4. Click "Upload & Index"
5. Wait for "✓ indexed" message

### Option 2: Via Python Script
```bash
python test_connection.py
```

---

## ❓ Sample Questions to Ask

### Healthcare Questions
1. **"What is artificial intelligence in healthcare?"**
2. **"How does machine learning help with medical imaging?"**
3. **"What are the applications of AI in patient care?"**

### Technology Questions
1. **"What is machine learning?"**
2. **"How does deep learning work?"**
3. **"What is natural language processing?"**

### Product Questions
1. **"What electronics products do you have?"**
2. **"Show me products under $500"**
3. **"What gaming products are available?"**

### FAQ Questions
1. **"What is an embedding?"**
2. **"How does the embedding server work?"**
3. **"How fast is the search?"**
4. **"Is the service free?"**

### Quick Test Questions
1. **"artificial intelligence"**
2. **"machine learning"**
3. **"how does embedding work"**

---

## 🚀 Quick Start Steps

1. **Restart Backend** (if endpoints not working):
   ```bash
   # Stop current backend (Ctrl+C in terminal)
   python api_server.py
   ```

2. **Wait 30 seconds** for models to load

3. **Refresh Frontend**: http://localhost:5500

4. **Upload Files**:
   - Use files from `sample_data/` folder
   - Or your own files

5. **Ask Questions**:
   - Type in the search box
   - Press Enter or click Send

---

## 📋 Files Ready to Upload

Located in `sample_data/`:
- ✅ `sample_texts.txt` - Healthcare AI (20 chunks)
- ✅ `products.csv` - Product catalog (15 items)
- ✅ `faq_document.txt` - FAQ about server (16 chunks)
- ✅ `tech_articles.txt` - Tech articles (16 chunks)
- ✅ `healthcare_data.csv` - Patient data (15 records)

---

## ✅ Expected Results

After uploading and asking questions, you should see:

```
Result 1
[Preview text from document...]
[source: sample_data/sample_texts.txt]

Result 2
[Preview text...]
[source: sample_data/products.csv]

Artillity • 3 hit(s)
```

---

## 🔍 Troubleshooting

### "Failed to fetch" Error
- **Cause**: Backend not running or endpoints not loaded
- **Fix**: Restart backend, wait 30 seconds, refresh browser

### "404 Not Found" Error
- **Cause**: Artillity endpoints not registered
- **Fix**: Restart backend to load new endpoints

### Files Not Uploading
- **Cause**: Backend still loading models
- **Fix**: Wait 30-60 seconds, try again

### No Search Results
- **Cause**: No files uploaded yet
- **Fix**: Upload files first, then search

---

**Everything is FREE and LOCAL - No API keys needed!** 🎉


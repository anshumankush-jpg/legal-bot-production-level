# 🚨 QUICK FIX - Make Everything Work

## ⚡ Main Issue: API Key Not Set

Your `.env` file has a placeholder. **Replace it with your real API key!**

### Step 1: Get Your OpenAI API Key

1. Go to: https://platform.openai.com/account/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Step 2: Update `.env` File

1. Open: `backend/.env`
2. Find this line:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Replace with your real key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

### Step 3: Restart Backend

**Stop the current backend** (Ctrl+C) and restart:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 4: Test

1. **Chat:** http://localhost:4200/chat
   - Should work now! (may say "no information" until docs ingested)

2. **Upload:** http://localhost:4200/upload
   - PDF/text files work ✅
   - Images need Tesseract (optional)

---

## 📋 What's Fixed

✅ **pytesseract installed** - Python package ready
✅ **Backend running** - Server is up
✅ **Frontend running** - UI is up
✅ **CORS configured** - Frontend can talk to backend
✅ **Better error messages** - More helpful errors

❌ **Need to fix:**
- Set real OpenAI API key in `.env`
- (Optional) Install Tesseract for image OCR

---

## 🎯 After Setting API Key

Everything will work:
- ✅ Chat queries
- ✅ File uploads (PDF, text, HTML)
- ✅ Document ingestion
- ✅ RAG system
- ⚠️ Image OCR (needs Tesseract binary)

---

## 🔧 Optional: Install Tesseract for Image OCR

**Only needed if you want to upload images (tickets, etc.)**

1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install (default: `C:\Program Files\Tesseract-OCR`)
3. Set environment variable:
   ```powershell
   $env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```
4. Restart backend

**Note:** Text/PDF uploads work fine without Tesseract!

---

## ✅ Test Checklist

After setting API key:

- [ ] Chat works: http://localhost:4200/chat
- [ ] Upload PDF works: http://localhost:4200/upload
- [ ] Upload text works: http://localhost:4200/upload
- [ ] Backend health: http://localhost:8000/health
- [ ] (Optional) Image upload works (if Tesseract installed)

---

**The main fix is setting your OpenAI API key in `backend/.env`!** 🔑

Once that's done, restart the backend and everything will work.


# 🧪 Test Query & HTML to PDF Conversion

## ✅ What's Been Created

### **1. Test Script: `test_pdf_vs_html.py`**
- Tests queries against the backend
- Shows which sources (PDF/HTML) are used
- Compares extraction quality
- Checks backend status

### **2. HTML to PDF Converter: `convert_html_to_pdf.py`**
- Converts HTML files to PDF
- Uses multiple methods (weasyprint, pdfkit, playwright)
- Creates PDFs in `converted_pdfs/` folder
- Better for PDF-focused processing

---

## 🔍 Testing Current Setup

### **Check Sentence Transformers:**
```bash
cd backend
python -c "from sentence_transformers import SentenceTransformer; print('✅ Installed')"
```

### **Check Embedding Service:**
```bash
cd backend
python -c "from app.embeddings.embedding_service import get_embedding_service; es = get_embedding_service(); print('Provider:', es.embedding_provider)"
```

### **Test a Query:**
```bash
cd backend/scripts
python test_pdf_vs_html.py
```

This will:
- ✅ Check if backend is running
- ✅ Check index size
- ✅ Test multiple queries
- ✅ Show which sources (PDF/HTML) are used
- ✅ Compare results

---

## 📄 Converting HTML to PDF

### **Why Convert?**
- PDFs may be processed better by some readers
- Consistent format
- Better for legal documents

### **Install PDF Converter:**
```bash
pip install weasyprint
```

### **Convert HTML Files:**
```bash
cd backend/scripts
python convert_html_to_pdf.py
```

This will:
- Find all HTML files in:
  - `us_state_codes/`
  - `canada_traffic_acts/`
  - `canada criminal and federal law/`
- Convert them to PDF
- Save to `converted_pdfs/` folder

---

## 🔑 API Key Check

### **Current Status:**
- Sentence Transformers: ✅ Local (no API key needed)
- OpenAI Chat: ⚠️ Needs API key for answers

### **To Set OpenAI API Key:**
1. Open `backend/.env`
2. Add/update:
   ```env
   OPENAI_API_KEY=sk-proj-your-key-here
   ```
3. Restart backend

**Note:** Sentence Transformers works WITHOUT API key (local, free)
**OpenAI API key is ONLY needed for generating chat answers**

---

## 🧪 Quick Test

### **1. Test Backend:**
```bash
curl http://localhost:8000/health
```

### **2. Test Query:**
```bash
cd backend/scripts
python test_pdf_vs_html.py
```

### **3. Check Results:**
- See which sources are used (PDF vs HTML)
- Compare answer quality
- Verify extraction is working

---

## 📋 Summary

**Sentence Transformers:**
- ✅ Installed and working
- ✅ No API key needed (local)
- ✅ Model: all-MiniLM-L6-v2

**OpenAI API Key:**
- ⚠️ Needed for chat answers
- ✅ Already set in your .env (based on previous setup)

**PDF vs HTML:**
- Both work, but PDFs may have better extraction
- Use test script to compare
- Convert HTML to PDF if needed

---

**Run the test script to see which works better!** 🚀


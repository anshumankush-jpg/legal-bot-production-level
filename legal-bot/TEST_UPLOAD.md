# 🧪 Test PDF Upload End-to-End

## **Quick Test Instructions**

### **Step 1: Start Clean**

```bash
cd C:\Users\anshu\Downloads\assiii
.\CLEAN_START.bat
```

Wait for both servers to start (35 seconds).

---

### **Step 2: Open Frontend**

Open browser: **http://localhost:4201**

You should see the chat interface.

---

### **Step 3: Test Drag & Drop**

**Test File:** `C:\Users\anshu\Downloads\assiii\ALEBRTA RUL BOOK.pdf`

1. **Drag the PDF** from File Explorer
2. **Drop it** anywhere on the chat interface
3. **Watch for:**
   - Drag overlay appears (blue background)
   - Upload progress bar
   - Success message: "✅ Document uploaded! X chunks indexed"

**Expected Result:**
```
✅ Document uploaded! 150 chunks indexed
Processing time: 8.5 seconds
```

---

### **Step 4: Test Image Upload (Ctrl+V)**

1. **Take a screenshot** (Win+Shift+S)
2. **Click in chat input**
3. **Press Ctrl+V**
4. **Watch for:**
   - Image preview appears
   - Upload starts automatically
   - OCR extraction message

**Expected Result:**
```
✅ Image uploaded! OCR extracted 5 chunks
```

---

### **Step 5: Test Plus Button**

1. **Click the + button** (bottom left of input)
2. **Choose "PDF"**
3. **Select:** `ALEBRTA RUL BOOK.pdf`
4. **Watch upload progress**

**Expected Result:**
```
✅ Document uploaded successfully!
```

---

### **Step 6: Ask Questions**

After upload, try these questions:

**Question 1:**
```
What are the traffic laws in this document?
```

**Expected:** Should return relevant chunks about traffic laws

**Question 2:**
```
What are the penalties for speeding?
```

**Expected:** Should return chunks about speeding penalties

**Question 3:**
```
Summarize the key points of this document
```

**Expected:** Should provide a summary based on indexed chunks

---

## **🔍 Verify in Backend Logs**

### **Check Backend Terminal**

You should see:

```
2026-01-08 XX:XX:XX - app.main - INFO - ================================================================================
2026-01-08 XX:XX:XX - app.main - INFO - BACKEND STARTING - DETAILED LOGGING ENABLED
2026-01-08 XX:XX:XX - app.main - INFO - ================================================================================
2026-01-08 XX:XX:XX - app.main - INFO - ✅ Tesseract OCR configured at: C:\Program Files\Tesseract-OCR\tesseract.exe
2026-01-08 XX:XX:XX - app.main - INFO - ✅ Tesseract version: 5.4.0.20240606
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### **When You Upload**

```
INFO:     127.0.0.1:XXXXX - "POST /api/ingest/file HTTP/1.1" 200 OK
2026-01-08 XX:XX:XX - app.main - INFO - 📄 Processing file: ALEBRTA RUL BOOK.pdf
2026-01-08 XX:XX:XX - artillery.document_processor - INFO - 📄 Processing document: ALEBRTA RUL BOOK.pdf
2026-01-08 XX:XX:XX - artillery.document_processor - INFO - ✅ Document processed: 150 chunks
2026-01-08 XX:XX:XX - artillery.rtld_vector_search_engine - INFO - 🧮 Generating embeddings for 150 chunks...
2026-01-08 XX:XX:XX - artillery.faiss_vector_store - INFO - ✅ Added 150 vectors to index (total: 150)
```

---

## **❌ Common Issues & Fixes**

### **Issue 1: "Tesseract not found"**

**Symptom:**
```
tesseract is not installed or it's not in your PATH
```

**Fix:**
```bash
# Check if installed
tesseract --version

# If not found, run:
.\CLEAN_START.bat
```

---

### **Issue 2: "Connection refused"**

**Symptom:**
```
Failed to fetch
net::ERR_CONNECTION_REFUSED
```

**Fix:**
```bash
# Check backend is running
curl http://localhost:8000/health

# If not running, restart:
.\CLEAN_START.bat
```

---

### **Issue 3: "Upload stuck at 0%"**

**Symptom:**
- Progress bar doesn't move
- No error message

**Fix:**
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Restart backend:
   ```bash
   .\CLEAN_START.bat
   ```

---

### **Issue 4: "Can't read PDF"**

**Symptom:**
```
Could not extract text from PDF
```

**Fix:**
```bash
# Install additional libraries
cd backend
pip install PyMuPDF pdfminer.six pdfplumber

# Restart
cd ..
.\CLEAN_START.bat
```

---

### **Issue 5: "No chunks indexed"**

**Symptom:**
```
✅ Document uploaded! 0 chunks indexed
```

**Possible Causes:**
1. PDF is scanned image (needs OCR)
2. PDF is encrypted
3. PDF has no text

**Fix:**
- Try a different PDF
- Or use image upload with OCR
- Or extract text manually first

---

## **📊 Performance Expectations**

| File Type | Size | Expected Time | Chunks |
|-----------|------|---------------|--------|
| **Small PDF** | 10 pages | 5-10 sec | ~50 |
| **Medium PDF** | 50 pages | 15-25 sec | ~250 |
| **Large PDF** | 100 pages | 30-60 sec | ~500 |
| **Image (OCR)** | 1 page | 2-5 sec | ~5-10 |
| **Text file** | 10KB | 1-2 sec | ~20 |

---

## **✅ Success Criteria**

Your system is working if:

- [ ] Backend starts without errors
- [ ] Tesseract version shows in logs
- [ ] Frontend loads at http://localhost:4201
- [ ] Can drag & drop PDF
- [ ] Upload progress shows
- [ ] Success message appears
- [ ] Chunks are indexed (> 0)
- [ ] Can ask questions about document
- [ ] Search returns relevant answers
- [ ] OCR works on images

---

## **🎯 Next Steps After Testing**

If everything works:

1. **Upload your real documents**
2. **Test with different file types**
3. **Optimize if needed** (see OPTIMIZE_CHUNKING.md)
4. **Monitor performance** in logs
5. **Scale up** if handling many documents

If issues persist:

1. **Check logs** in backend terminal
2. **Check browser console** (F12)
3. **Verify Tesseract** is installed
4. **Restart everything** with CLEAN_START.bat
5. **Contact support** with error logs

---

## **🚀 Advanced Testing**

### **Test Multiple Uploads**

Upload 3-5 documents in sequence:

```
1. ALEBRTA RUL BOOK.pdf
2. An image (screenshot)
3. A text file
4. Another PDF
5. Another image
```

**Expected:** All should upload successfully

---

### **Test Search Across Documents**

After uploading multiple documents, ask:

```
"What do all my documents say about traffic laws?"
```

**Expected:** Should return chunks from all relevant documents

---

### **Test Metadata Filtering**

Upload with metadata:

```javascript
// In frontend, add metadata to upload
formData.append('province', 'Alberta');
formData.append('category', 'traffic_law');
```

Then search with filter:

```
"Show me Alberta traffic laws"
```

**Expected:** Should filter by province

---

## **📝 Test Results Template**

Use this to track your tests:

```
Date: ___________
Tester: ___________

Test 1: Drag & Drop PDF
Status: [ ] Pass [ ] Fail
Time: _____ seconds
Chunks: _____
Notes: ___________

Test 2: Ctrl+V Image
Status: [ ] Pass [ ] Fail
Time: _____ seconds
Chunks: _____
Notes: ___________

Test 3: Plus Button Upload
Status: [ ] Pass [ ] Fail
Time: _____ seconds
Chunks: _____
Notes: ___________

Test 4: Ask Questions
Status: [ ] Pass [ ] Fail
Relevance: [ ] High [ ] Medium [ ] Low
Notes: ___________

Overall: [ ] All Pass [ ] Some Fail [ ] All Fail
```

---

**Ready to test? Run `.\CLEAN_START.bat` and start uploading!** 🚀

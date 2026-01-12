# ✅ After Installing Tesseract OCR

## 🎯 What to Do After Installation

### **1. Restart Your Terminal (REQUIRED)**

⚠️ **CRITICAL:** You MUST restart your terminal for PATH changes to take effect!

**Close:**
- All PowerShell windows
- All CMD windows
- Any terminals running your servers

**Open:**
- Fresh new terminal/PowerShell window

---

### **2. Verify Installation**

Test that Tesseract is accessible:

```bash
tesseract --version
```

**Expected Output:**
```
tesseract 5.5.0
 leptonica-1.84.1
 ...
```

**If you see:** `tesseract is not recognized`
→ Your terminal is still using old PATH
→ Close ALL terminals and open a NEW one

---

### **3. Restart Your Servers**

```bash
# From project root (C:\Users\anshu\Downloads\assiii)
START_BOTH_SERVERS.bat
```

This starts:
- Backend on http://localhost:8000
- Frontend on http://localhost:4201

---

### **4. Test Image Upload**

#### **Method 1: Drag & Drop**
1. Open http://localhost:4201
2. Find an image file (JPG, PNG, etc.)
3. Drag it over the browser
4. See the cyan overlay appear
5. Drop it
6. ✅ Should upload with OCR!

#### **Method 2: Ctrl+V Paste**
1. Take a screenshot (Win+Shift+S)
2. Open the chat
3. Press Ctrl+V
4. ✅ Should upload with OCR!

#### **Method 3: Plus Button**
1. Click the + button
2. Select "Image (OCR)"
3. Choose your image
4. ✅ Should upload with OCR!

---

### **5. Run Complete OCR Test**

Run our comprehensive test:

```bash
cd backend
python test_image_ocr.py
```

**Expected Output:**
```
================================================================================
🖼️  TESTING IMAGE OCR FUNCTIONALITY
================================================================================

📦 Initializing services...
✅ Services initialized successfully

🔍 Checking OCR capabilities...
   PDF Support: True
   DOCX Support: True
   OCR Support: True
   Tables Support: True

✅ OCR is available!

📝 Creating test image with text...
✅ Test image created: backend/test_uploads/test_legal_document.png

🔄 Processing test image with OCR...
✅ Image processed successfully!
   Text chunks: 1
   Images: 1

📄 Extracted text (first 500 chars):
--------------------------------------------------------------------------------
TRAFFIC VIOLATION NOTICE
Offence Number: 1234567890
Province: Ontario
...
--------------------------------------------------------------------------------

✅ Detected offence number: 1234567890
✅ Detected province: Ontario

🧠 Creating embeddings...
✅ Embedding created: shape (1, 384)

💾 Storing in vector database...
✅ Stored in vector database

🔍 Testing search...
✅ Search successful! Found 1 results
   Top result score: 0.9999
   Content preview: TRAFFIC VIOLATION NOTICE...

================================================================================
✅ ALL TESTS PASSED!
================================================================================

🎉 Image OCR is working correctly!
```

---

### **6. What You Can Do Now**

#### **✅ Upload Images with OCR**
- JPG, JPEG, PNG, BMP, TIFF files
- OCR automatically extracts text
- Text is searchable in chat

#### **✅ Upload Documents**
- PDF (with or without OCR)
- DOCX, TXT, XLSX
- All work perfectly

#### **✅ Ask Questions**
```
User: "What is my offence number?"
Bot: "Based on your uploaded document, your offence number is 1234567890..."

User: "What was I charged with?"
Bot: "According to the ticket, you were charged with speeding at 120 km/h in an 80 km/h zone..."
```

---

### **7. Troubleshooting**

#### **Issue: "tesseract is not recognized"**
**Solution:**
1. Make sure you closed ALL old terminals
2. Open a BRAND NEW terminal
3. Test again: `tesseract --version`

#### **Issue: "tesseract --version works but upload still fails"**
**Solution:**
1. Restart your backend server
2. Stop: Ctrl+C in backend terminal
3. Start: `cd backend; python -m uvicorn app.main:app --reload`

#### **Issue: "OCR accuracy is poor"**
**Solutions:**
- Use higher resolution images
- Ensure good contrast and lighting
- Crop image to text area only
- Try PNG format instead of JPG

#### **Issue: "Upload is slow"**
**Normal:** OCR processing takes 1-3 seconds per image
- The first upload loads the embedding model (~5 seconds)
- Subsequent uploads are faster

---

### **8. Advanced Usage**

#### **Multi-Language OCR (Optional)**
By default, Tesseract uses English. To add other languages:

**Download Language Packs:**
```
https://github.com/tesseract-ocr/tessdata
```

**Install to:**
```
C:\Program Files\Tesseract-OCR\tessdata\
```

**Supported Languages:**
- French: `fra.traineddata`
- Hindi: `hin.traineddata`
- Punjabi: `pan.traineddata`
- Spanish: `spa.traineddata`

---

## 📋 Quick Checklist

Before testing image upload:

- [ ] Tesseract installed to `C:\Program Files\Tesseract-OCR`
- [ ] "Add to PATH" was checked during install
- [ ] Closed ALL old terminals
- [ ] Opened NEW terminal
- [ ] `tesseract --version` works
- [ ] Servers restarted (backend + frontend)
- [ ] Browser open at http://localhost:4201

---

## 🎉 You're Ready!

If all the above checks pass, you can now:
- ✅ Drag & drop images
- ✅ Press Ctrl+V to paste screenshots
- ✅ Upload traffic tickets, documents, legal papers
- ✅ Ask questions about uploaded images
- ✅ Get OCR-extracted text automatically

**Try it now!** Take a screenshot and press Ctrl+V in the chat! 🚀

# 🚀 PLAZA-AI Quick Start Guide

## **Start Both Servers (Easiest Way)**

### **Option 1: Windows Batch File (Recommended for Windows)**
```bash
# Double-click or run:
START_BOTH_SERVERS.bat
```

### **Option 2: Python Script (Cross-Platform)**
```bash
python start_both_servers.py
```

Both scripts will:
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:4200
- ✅ Open separate windows for each server
- ✅ Wait for servers to be ready

---

## **Manual Start (If Scripts Don't Work)**

### **Step 1: Start Backend**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will run on:** http://localhost:8000

### **Step 2: Start Frontend (New Terminal)**
```bash
cd frontend
npm start
```

**Frontend will run on:** http://localhost:4200

---

## **Verify Connection**

### **Test Backend:**
```bash
# Open in browser or use curl:
http://localhost:8000/health
http://localhost:8000/api/artillery/health
```

### **Test Frontend:**
```bash
# Open in browser:
http://localhost:4200
```

### **Run Connection Test:**
```bash
python test_frontend_backend_connection.py
```

---

## **First Time Setup**

### **1. Install Frontend Dependencies:**
```bash
cd frontend
npm install
```

### **2. Install Backend Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

### **3. Ingest Legal Documents (Optional):**
```bash
python ingest_all_documents.py
```

---

## **Troubleshooting**

### **Backend Won't Start:**
- Check if port 8000 is already in use
- Verify Python dependencies are installed
- Check backend logs for errors

### **Frontend Won't Start:**
- Check if port 4200 is already in use
- Run `npm install` in frontend directory
- Check Node.js version (should be 14+)

### **Connection Issues:**
- Verify backend is running: http://localhost:8000/health
- Check browser console for CORS errors
- Verify API URL in ChatInterface.jsx is `http://localhost:8000`

---

## **What Happens When You Start:**

1. **Backend Starts:**
   - Loads FAISS vector store
   - Loads embedding models
   - Starts FastAPI server on port 8000

2. **Frontend Starts:**
   - Starts Vite dev server on port 4200
   - Opens browser automatically
   - Shows onboarding wizard (first time)

3. **User Experience:**
   - Complete onboarding (language, country, province)
   - Ask legal questions
   - Upload documents via plus icon
   - Get structured legal responses

---

## **Stopping Servers**

### **Windows:**
- Close the console windows
- Or press `Ctrl+C` in each window

### **Linux/Mac:**
- Press `Ctrl+C` in each terminal
- Or find and kill processes:
  ```bash
  lsof -ti:8000 | xargs kill  # Backend
  lsof -ti:4200 | xargs kill  # Frontend
  ```

---

## **Quick Reference**

| Service | URL | Status Check |
|---------|-----|--------------|
| Backend | http://localhost:8000 | `/health` |
| Frontend | http://localhost:4200 | Browser |
| Artillery API | http://localhost:8000/api/artillery | `/api/artillery/health` |

---

**Ready to go! Just run `START_BOTH_SERVERS.bat` or `python start_both_servers.py`** 🚀
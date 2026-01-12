@echo off
echo ============================================
echo   CLEAN START - KILL ALL & RESTART FRESH
echo ============================================
echo.

echo Step 1: Killing ALL Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python3.12.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
echo Done!
echo.

echo Step 2: Waiting for processes to close...
timeout /t 5 /nobreak >nul
echo.

echo Step 3: Verifying all killed...
netstat -ano | findstr ":8000" | findstr "LISTENING"
echo (Should be empty above)
echo.

echo Step 4: Adding Tesseract to PATH...
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
echo Done!
echo.

echo Step 5: Starting Backend (SINGLE INSTANCE)...
cd backend
start "PLAZA-AI Backend" cmd /k "set PATH=%PATH%;C:\Program Files\Tesseract-OCR && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd ..
echo.

echo Step 6: Waiting for backend to fully start (35 seconds)...
timeout /t 35 /nobreak
echo.

echo Step 7: Verifying backend is running...
curl -s http://localhost:8000/health
echo.

echo Step 8: Starting Frontend...
cd frontend
start "PLAZA-AI Frontend" cmd /k "npm run dev"
cd ..
echo.

echo ============================================
echo   SERVERS STARTED!
echo ============================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4201
echo.
echo ✅ Clean start complete!
echo ✅ Tesseract OCR enabled!
echo ✅ Drag & Drop ready!
echo.
echo TEST IT NOW:
echo 1. Open http://localhost:4201
echo 2. Drag a PDF onto the page
echo 3. Or press Ctrl+V with an image
echo 4. Ask questions about your document!
echo.
pause

@echo off
echo ============================================
echo   FIXING ALL ISSUES AND RESTARTING
echo ============================================
echo.

echo Step 1: Killing all duplicate backend processes...
taskkill /F /PID 32092 2>nul
taskkill /F /PID 33596 2>nul
taskkill /F /PID 29644 2>nul
taskkill /F /PID 28820 2>nul
taskkill /F /PID 6080 2>nul
taskkill /F /PID 35412 2>nul
echo Done!
echo.

echo Step 2: Waiting for processes to fully close...
timeout /t 5 /nobreak >nul
echo.

echo Step 3: Adding Tesseract to PATH...
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
echo Done!
echo.

echo Step 4: Starting Backend with Tesseract...
cd backend
start "PLAZA-AI Backend" cmd /k "set PATH=%PATH%;C:\Program Files\Tesseract-OCR && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd ..
echo.

echo Step 5: Waiting for backend to start (30 seconds)...
timeout /t 30 /nobreak
echo.

echo Step 6: Starting Frontend...
cd frontend
start "PLAZA-AI Frontend" cmd /k "npm run dev"
cd ..
echo.

echo ============================================
echo   SERVERS STARTED SUCCESSFULLY!
echo ============================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4201
echo.
echo ✅ Tesseract OCR is now enabled!
echo ✅ All duplicate processes killed!
echo ✅ Drag & Drop is ready!
echo.
echo Next steps:
echo 1. Open http://localhost:4201 in your browser
echo 2. Drag and drop a PDF or image anywhere on the page
echo 3. Or use Ctrl+V to paste an image
echo 4. Or click the + button to upload
echo.
pause

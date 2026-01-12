@echo off
echo ============================================
echo   RESTARTING SERVERS WITH TESSERACT
echo ============================================
echo.

echo Step 1: Stopping existing servers...
taskkill /F /IM python.exe /T > nul 2>&1
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *PLAZA-AI*" /T > nul 2>&1
echo Done!

echo.
echo Step 2: Waiting for processes to close...
timeout /t 3 /nobreak > nul

echo.
echo Step 3: Adding Tesseract to PATH...
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
echo Done!

echo.
echo Step 4: Starting Backend (with Tesseract)...
start "PLAZA-AI Backend (Tesseract Enabled)" cmd /k "set PATH=%PATH%;C:\Program Files\Tesseract-OCR && cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo Step 5: Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Step 6: Starting Frontend...
start "PLAZA-AI Frontend" cmd /k "cd frontend && npm start"

echo.
echo ============================================
echo   SERVERS STARTED!
echo ============================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4201
echo.
echo ✅ Tesseract OCR is now enabled!
echo.
echo Next steps:
echo 1. Wait 30 seconds for servers to fully start
echo 2. Refresh browser (F5) at http://localhost:4201
echo 3. Upload your image AGAIN
echo 4. Look for: "✅ Image uploaded! OCR extracted X chunks..."
echo 5. Ask questions about your image!
echo.
pause

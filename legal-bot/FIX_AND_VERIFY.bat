@echo off
echo ============================================
echo   FIX IMAGE READING - COMPLETE SOLUTION
echo ============================================
echo.

echo This will:
echo 1. Install Tesseract OCR
echo 2. Restart your servers
echo 3. Verify the entire image pipeline
echo 4. Test with a sample image
echo.
echo Press any key to continue...
pause > nul

echo.
echo ============================================
echo   STEP 1: Installing Tesseract OCR
echo ============================================
echo.

call INSTALL_TESSERACT.bat

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Tesseract installation failed!
    echo Please install manually from: https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)

echo.
echo ============================================
echo   STEP 2: Restarting Servers
echo ============================================
echo.

echo Stopping any running servers...
taskkill /F /IM python.exe /T > nul 2>&1
taskkill /F /IM node.exe /T > nul 2>&1
timeout /t 2 /nobreak > nul

echo Starting servers...
start "PLAZA-AI Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 5 /nobreak > nul
start "PLAZA-AI Frontend" cmd /k "cd frontend && npm start"

echo.
echo Waiting for servers to start (30 seconds)...
timeout /t 30 /nobreak

echo.
echo ============================================
echo   STEP 3: Verifying Image Pipeline
echo ============================================
echo.

cd backend
python verify_image_pipeline.py

if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some verification tests failed!
    echo Check the output above for details.
    echo.
) else (
    echo.
    echo ============================================
    echo   SUCCESS! IMAGE READING IS NOW WORKING!
    echo ============================================
    echo.
    echo The bot can now:
    echo  ✓ Upload images
    echo  ✓ Extract text with OCR
    echo  ✓ Answer questions about images
    echo.
    echo Open your browser at: http://localhost:4201
    echo Upload an image and ask questions!
    echo.
)

cd ..
pause

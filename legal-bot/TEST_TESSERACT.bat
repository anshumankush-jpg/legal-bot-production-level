@echo off
echo ============================================
echo   Testing Tesseract OCR Installation
echo ============================================
echo.

echo Step 1: Checking if Tesseract is installed...
tesseract --version
if errorlevel 1 (
    echo.
    echo ❌ Tesseract NOT found!
    echo Please install Tesseract and restart your terminal.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Tesseract is installed!
echo.

echo Step 2: Testing the OCR system...
cd backend
python test_image_ocr.py

echo.
echo ============================================
echo   Test Complete!
echo ============================================
echo.
echo If you saw "✅ ALL TESTS PASSED!" above, you're ready!
echo.
echo Open your app at: http://localhost:4201
echo.
pause

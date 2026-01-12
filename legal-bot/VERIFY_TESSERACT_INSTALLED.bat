@echo off
echo ============================================
echo   VERIFYING TESSERACT INSTALLATION
echo ============================================
echo.

echo Step 1: Checking if Tesseract is in PATH...
echo.

tesseract --version > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ SUCCESS! Tesseract is installed and in PATH!
    echo.
    tesseract --version
    echo.
    echo ============================================
    echo   NEXT STEPS:
    echo ============================================
    echo.
    echo 1. Restart your servers:
    echo    START_BOTH_SERVERS.bat
    echo.
    echo 2. Refresh your browser (F5)
    echo.
    echo 3. Upload your image AGAIN
    echo    (old uploads won't have OCR text)
    echo.
    echo 4. You should see:
    echo    "✅ Image uploaded! OCR extracted X chunks..."
    echo.
    echo 5. Ask questions about your image!
    echo.
) else (
    echo ❌ Tesseract NOT found in PATH!
    echo.
    echo This means either:
    echo 1. Installation not complete yet
    echo 2. "Add to PATH" was not checked
    echo 3. Need to restart terminal
    echo.
    echo ============================================
    echo   MANUAL PATH SETUP:
    echo ============================================
    echo.
    echo If Tesseract is installed but not in PATH:
    echo.
    echo 1. Press Win + R
    echo 2. Type: sysdm.cpl
    echo 3. Go to "Advanced" tab
    echo 4. Click "Environment Variables"
    echo 5. Under "System variables", find "Path"
    echo 6. Click "Edit"
    echo 7. Click "New"
    echo 8. Add: C:\Program Files\Tesseract-OCR
    echo 9. Click OK, OK, OK
    echo 10. Close ALL terminals
    echo 11. Open NEW terminal
    echo 12. Run this script again
    echo.
)

pause

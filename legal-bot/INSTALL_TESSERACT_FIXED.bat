@echo off
echo ============================================
echo   TESSERACT OCR INSTALLATION
echo ============================================
echo.

echo Opening download page in your browser...
echo.
start https://github.com/UB-Mannheim/tesseract/wiki

echo.
echo ============================================
echo   MANUAL INSTALLATION STEPS:
echo ============================================
echo.
echo 1. Your browser is opening the download page
echo.
echo 2. Look for: "tesseract-ocr-w64-setup-v5.5.0.20241111.exe"
echo    (or the latest version available)
echo.
echo 3. Click the download link
echo.
echo 4. Run the downloaded .exe file
echo.
echo 5. IMPORTANT DURING INSTALLATION:
echo    - Install to: C:\Program Files\Tesseract-OCR
echo    - Check: "Add to PATH" option
echo.
echo 6. After installation:
echo    - Close ALL terminals
echo    - Open NEW terminal
echo    - Run: tesseract --version
echo    - Run: START_BOTH_SERVERS.bat
echo.
echo ============================================
echo   OR USE CHOCOLATEY (If you have it):
echo ============================================
echo.
echo Run this command in an ADMIN PowerShell:
echo choco install tesseract
echo.
echo ============================================
echo   OR USE DIRECT DOWNLOAD:
echo ============================================
echo.
echo Try this alternative link:
echo https://github.com/tesseract-ocr/tesseract/releases
echo.
pause

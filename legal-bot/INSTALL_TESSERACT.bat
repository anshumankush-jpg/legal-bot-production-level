@echo off
echo ============================================
echo   INSTALLING TESSERACT OCR FOR WINDOWS
echo ============================================
echo.

echo Step 1: Downloading Tesseract installer...
echo.
powershell -Command "& {Invoke-WebRequest -Uri 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.5.0.20241111.exe' -OutFile '%TEMP%\tesseract-installer.exe'}"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to download installer!
    echo Please download manually from: https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)

echo.
echo Step 2: Starting Tesseract installer...
echo.
echo IMPORTANT INSTALLATION STEPS:
echo 1. Click "Next" to start installation
echo 2. Accept the license agreement
echo 3. Install to: C:\Program Files\Tesseract-OCR (default)
echo 4. IMPORTANT: Check "Add to PATH" option!
echo 5. Click "Install" and wait for completion
echo 6. Click "Finish"
echo.
echo Press any key to start the installer...
pause > nul

start /wait %TEMP%\tesseract-installer.exe

echo.
echo Step 3: Verifying installation...
echo.
timeout /t 3 /nobreak > nul

tesseract --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Tesseract not found in PATH!
    echo.
    echo Please follow these manual steps:
    echo 1. Close ALL PowerShell and CMD windows
    echo 2. Open NEW PowerShell window
    echo 3. Run: tesseract --version
    echo 4. If still not found, add manually to PATH:
    echo    - Open "Environment Variables"
    echo    - Add: C:\Program Files\Tesseract-OCR
    echo    - Restart computer if needed
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ SUCCESS! Tesseract is installed and working!
    echo.
    tesseract --version
    echo.
    echo ============================================
    echo   INSTALLATION COMPLETE!
    echo ============================================
    echo.
    echo Next steps:
    echo 1. Close this window
    echo 2. Close ALL terminals
    echo 3. Run START_BOTH_SERVERS.bat
    echo 4. Upload an image to test OCR
    echo.
    pause
    exit /b 0
)

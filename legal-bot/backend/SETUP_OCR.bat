@echo off
echo ============================================
echo   PLAZA-AI OCR Setup for Windows
echo ============================================
echo.

echo Step 1: Installing Python packages...
pip install pytesseract opencv-python Pillow PyMuPDF
echo.

echo Step 2: Tesseract OCR Installation
echo ============================================
echo.
echo Tesseract OCR is required for image text extraction.
echo.
echo Please follow these steps:
echo.
echo 1. Download Tesseract for Windows from:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo 2. Download the latest installer (tesseract-ocr-w64-setup-*.exe)
echo.
echo 3. Run the installer and install to:
echo    C:\Program Files\Tesseract-OCR
echo.
echo 4. Add to PATH (the installer usually does this automatically)
echo.
echo 5. Restart your terminal after installation
echo.

pause
echo.

echo Step 3: Testing Tesseract installation...
tesseract --version
if errorlevel 1 (
    echo.
    echo ERROR: Tesseract not found! Please install it manually:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo After installation, add this to your environment:
    echo C:\Program Files\Tesseract-OCR
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   ✅ OCR Setup Complete!
echo ============================================
echo.
echo You can now upload images (JPG, PNG, BMP, TIFF) and the system will:
echo   - Extract text using OCR
echo   - Create embeddings
echo   - Make them searchable in chat
echo.
echo Supported formats:
echo   📄 Documents: PDF, DOCX, TXT, XLSX
echo   🖼️ Images: JPG, PNG, BMP, TIFF (with OCR)
echo.
pause

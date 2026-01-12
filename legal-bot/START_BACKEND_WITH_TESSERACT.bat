@echo off
echo ============================================
echo   STARTING BACKEND WITH TESSERACT
echo ============================================
echo.

REM Add Tesseract to PATH
set PATH=%PATH%;C:\Program Files\Tesseract-OCR

REM Navigate to backend directory
cd /d %~dp0\backend

REM Start backend
echo Starting backend with Tesseract in PATH...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

@echo off
REM ========================================
REM Test Setup - Verify Everything Works
REM ========================================
title Test Setup - PLAZA-AI

echo.
echo ========================================
echo   Testing PLAZA-AI Setup
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/4] Testing Python environment...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)
echo [OK] Python is available
echo.

echo [2/4] Testing API key...
python -c "from app.core.config import settings; key = settings.OPENAI_API_KEY; print('API Key:', 'SET' if key and key != 'your_openai_api_key_here' and key.startswith('sk-') else 'NOT SET'); print('Preview:', key[:15] + '...' if key and len(key) > 15 else 'Not configured')"
if errorlevel 1 (
    echo [ERROR] Could not check API key
    pause
    exit /b 1
)
echo.

echo [3/4] Testing backend connection...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend not running
    echo Start it with: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
) else (
    echo [OK] Backend is running
    curl -s http://localhost:8000/health
    echo.
)
echo.

echo [4/4] Testing OpenAI connection...
python -c "import requests; r = requests.post('http://localhost:8000/api/query/answer', json={'question': 'Hello'}, timeout=10); print('Status:', r.status_code); print('Response:', 'OK' if r.status_code == 200 else r.text[:100])" 2>&1
echo.

echo ========================================
echo   Test Complete
echo ========================================
echo.
echo If all tests passed, you can now:
echo   1. Run INGEST_ALL_DOCUMENTS.bat to ingest documents
echo   2. Go to http://localhost:4200/chat to use the AI
echo.
pause


@echo off
REM ========================================
REM Complete Setup & Document Ingestion
REM ========================================
title Complete Setup - PLAZA-AI

echo.
echo ========================================
echo   PLAZA-AI - Complete Setup
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

echo [1/5] Checking .env configuration...
echo.

REM Check if Sentence Transformers is configured
findstr /C:"EMBEDDING_PROVIDER=sentence_transformers" .env >nul 2>&1
if errorlevel 1 (
    echo [WARNING] EMBEDDING_PROVIDER not set to sentence_transformers
    echo.
    echo Please add to backend\.env:
    echo   EMBEDDING_PROVIDER=sentence_transformers
    echo   SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
    echo.
    pause
)

REM Check API key
findstr /C:"OPENAI_API_KEY=sk-" .env >nul 2>&1
if errorlevel 1 (
    echo [ERROR] OpenAI API key not set
    echo Please set OPENAI_API_KEY in backend\.env
    pause
    exit /b 1
)
echo [OK] Configuration looks good
echo.

echo [2/5] Stopping old backend processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo [OK] Old processes stopped
echo.

echo [3/5] Starting backend server...
start "PLAZA-AI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo Waiting for backend to start...
timeout /t 8 /nobreak >nul

REM Wait for backend
:wait_backend
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_backend
)
echo [OK] Backend is running
echo.

echo [4/5] Checking embedding provider...
python -c "from app.core.config import settings; print('Embedding Provider:', settings.EMBEDDING_PROVIDER); print('Model:', getattr(settings, 'SENTENCE_TRANSFORMER_MODEL', 'Not set'))" 2>&1
echo.

echo [5/5] Starting document ingestion...
echo.
echo This will ingest ALL documents from:
echo   - data/ folder
echo   - us_state_codes/
echo   - canada_traffic_acts/
echo   - paralegal_advice_dataset/
echo   - All other legal document folders
echo.
echo This may take several minutes...
echo.

cd scripts
echo yes | python bulk_ingest_documents.py

if errorlevel 1 (
    echo.
    echo [ERROR] Ingestion had errors. Check the output above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Documents have been ingested!
echo.
echo You can now:
echo   1. Go to http://localhost:4200/chat
echo   2. Ask questions about:
echo      - US state laws
echo      - Canada traffic acts
echo      - Demerit points
echo      - Paralegal advice
echo      - All ingested documents
echo.
echo The chatbot will answer from the ingested datasets!
echo.
pause


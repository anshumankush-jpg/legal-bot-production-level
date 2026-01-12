@echo off
REM ========================================
REM Double-Click to Ingest All Documents
REM ========================================
title Ingest All Documents - PLAZA-AI

echo.
echo ========================================
echo   PLAZA-AI - Bulk Document Ingestion
echo ========================================
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [1/4] Checking backend server...
echo.

REM Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend server is not running
    echo.
    echo Starting backend server in background...
    echo.
    start "PLAZA-AI Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Waiting for backend to start...
    timeout /t 5 /nobreak >nul
    
    REM Wait for backend to be ready
    :wait_backend
    curl -s http://localhost:8000/health >nul 2>&1
    if errorlevel 1 (
        timeout /t 2 /nobreak >nul
        goto wait_backend
    )
    echo [OK] Backend server is running
) else (
    echo [OK] Backend server is already running
)

echo.
echo [2/4] Checking API key...
echo.

REM Check if .env exists and has API key
if exist ".env" (
    findstr /C:"OPENAI_API_KEY=sk-" .env >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] OpenAI API key not set in .env file
        echo.
        echo Please edit backend\.env and set:
        echo   OPENAI_API_KEY=sk-your-actual-key-here
        echo.
        echo Get your key from: https://platform.openai.com/account/api-keys
        echo.
        pause
        exit /b 1
    )
    echo [OK] API key found in .env
) else (
    echo [ERROR] .env file not found
    echo Please create backend\.env with your OPENAI_API_KEY
    pause
    exit /b 1
)

echo.
echo [3/4] Running bulk ingestion...
echo.
echo This will ingest all documents from the data folder:
echo   - PDF files
echo   - HTML files  
echo   - JSON files (legal data, demerit tables, etc.)
echo.
echo Progress will be shown below...
echo.

REM Run the bulk ingestion script
cd scripts
python bulk_ingest_documents.py

if errorlevel 1 (
    echo.
    echo [ERROR] Ingestion failed. Check the error messages above.
    pause
    exit /b 1
)

echo.
echo [4/4] Verification...
echo.

REM Wait a moment for indexing to complete
timeout /t 2 /nobreak >nul

REM Check health endpoint
curl -s http://localhost:8000/health > temp_health.json 2>&1
if exist temp_health.json (
    findstr /C:"index_size" temp_health.json >nul
    if not errorlevel 1 (
        echo [OK] Documents indexed successfully!
        echo.
        type temp_health.json
        del temp_health.json
    )
)

echo.
echo ========================================
echo   INGESTION COMPLETE!
echo ========================================
echo.
echo You can now:
echo   1. Go to http://localhost:4200/chat
echo   2. Ask questions about your legal documents
echo   3. The AI will use the ingested documents to answer
echo.
echo Press any key to close...
pause >nul


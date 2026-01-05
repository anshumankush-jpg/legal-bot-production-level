@echo off
REM ========================================
REM Restart Backend to Load New API Key
REM ========================================
title Restart Backend - PLAZA-AI

echo.
echo ========================================
echo   Restarting Backend Server
echo ========================================
echo.

REM Kill any existing backend processes
echo [1/3] Stopping old backend processes...
taskkill /F /FI "WINDOWTITLE eq PLAZA-AI Backend*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Old processes stopped
echo.

REM Change to backend directory
cd /d "%~dp0backend"

echo [2/3] Starting backend with new configuration...
echo.
start "PLAZA-AI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo [3/3] Verifying backend is running...
:wait_backend
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_backend
)

echo [OK] Backend is running!
echo.

REM Test API key
echo Testing API connection...
python -c "import requests; r = requests.post('http://localhost:8000/api/query/answer', json={'question': 'test'}, timeout=10); print('Status:', r.status_code); print('Result:', 'SUCCESS' if r.status_code == 200 else 'ERROR - Check API key')" 2>&1
echo.

echo ========================================
echo   Backend Restarted!
echo ========================================
echo.
echo Backend is now running with your updated API key.
echo.
echo You can now:
echo   1. Run INGEST_ALL_DOCUMENTS.bat to ingest documents
echo   2. Go to http://localhost:4200/chat to use the AI
echo.
echo Press any key to close...
pause >nul


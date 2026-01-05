@echo off
REM ========================================
REM Complete Backend Restart
REM ========================================
title Restart Backend - PLAZA-AI

echo.
echo ========================================
echo   Restarting Backend (Fresh Start)
echo ========================================
echo.

REM Kill all Python processes
echo [1/3] Stopping all Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo [OK] All Python processes stopped
echo.

REM Change to backend directory
cd /d "%~dp0backend"

echo [2/3] Starting backend with fresh code...
echo.
start "PLAZA-AI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo.
echo Waiting for backend to start...
timeout /t 8 /nobreak >nul

echo [3/3] Testing backend...
python -c "import requests; import time; time.sleep(2); r = requests.post('http://localhost:8000/api/ingest/text', json={'text': 'Test', 'source_name': 'test.txt'}, timeout=10); print('Status:', r.status_code); print('SUCCESS!' if r.status_code == 200 else 'Still loading...')" 2>&1
echo.

echo ========================================
echo   Backend Restarted!
echo ========================================
echo.
echo If test shows SUCCESS, you can now:
echo   1. Run INGEST_ALL_DOCUMENTS.bat
echo   2. Go to http://localhost:4200/chat
echo.
pause


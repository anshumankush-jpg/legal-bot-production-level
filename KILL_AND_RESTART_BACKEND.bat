@echo off
REM ========================================
REM Kill Old Backend and Restart
REM ========================================
title Kill & Restart Backend - PLAZA-AI

echo.
echo ========================================
echo   Killing Old Backend and Restarting
echo ========================================
echo.

echo [1/3] Finding and killing old backend processes...
echo.

REM Find processes using port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Found process using port 8000: PID %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo   Could not kill PID %%a (may need admin rights)
    ) else (
        echo   [OK] Killed PID %%a
    )
)

REM Also kill by window title
taskkill /F /FI "WINDOWTITLE eq PLAZA-AI Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1

echo.
echo Waiting for port to be free...
timeout /t 3 /nobreak >nul

echo [2/3] Starting new backend...
echo.

cd /d "%~dp0backend"

REM Start backend in new window
start "PLAZA-AI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

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

REM Show health status
curl -s http://localhost:8000/health
echo.
echo.

echo ========================================
echo   Backend Restarted Successfully!
echo ========================================
echo.
echo Note: "Azure Search not available" is normal.
echo       The system uses FAISS (local) instead.
echo.
echo Backend is ready at: http://localhost:8000
echo.
echo Press any key to close...
pause >nul


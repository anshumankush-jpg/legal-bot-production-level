@echo off
REM ========================================
REM Restart Backend and Frontend Servers
REM ========================================
title Restart Servers - PLAZA-AI

echo.
echo ========================================
echo   Restarting Backend and Frontend
echo ========================================
echo.

cd /d "%~dp0"

REM Stop existing processes
echo [1/4] Stopping existing processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Processes stopped
echo.

REM Start Backend
echo [2/4] Starting Backend Server...
echo   Backend will run on: http://localhost:8000
start "PLAZA-AI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul
echo [OK] Backend starting...
echo.

REM Start Frontend
echo [3/4] Starting Frontend Server...
echo   Frontend will run on: http://localhost:4200
start "PLAZA-AI Frontend" cmd /k "cd /d %~dp0frontend && npm start"
echo [OK] Frontend starting...
echo.

REM Wait and check status
echo [4/4] Waiting for servers to start...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   Server Status
echo ========================================
echo.

REM Check Backend
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [INFO] Backend: Starting... (check backend window)
) else (
    echo [OK] Backend: RUNNING at http://localhost:8000
)

REM Check Frontend
curl -s http://localhost:4200 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Frontend: Starting... (may take 30-60 seconds to compile)
) else (
    echo [OK] Frontend: RUNNING at http://localhost:4200
)

echo.
echo ========================================
echo   Access Your Application
echo ========================================
echo.
echo Backend API:    http://localhost:8000
echo Frontend App:   http://localhost:4200
echo Chat Interface: http://localhost:4200/chat
echo.
echo Note: Frontend may take 30-60 seconds to compile
echo       Both servers are running in separate windows
echo.
pause


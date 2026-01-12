@echo off
REM ========================================
REM Double-Click to Start Everything
REM ========================================
title PLAZA-AI - Start Everything

echo.
echo ========================================
echo   PLAZA-AI - Starting All Services
echo ========================================
echo.

REM Change to project root
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Starting Backend Server...
echo.

cd backend

REM Check if backend is already running
curl -s http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Backend is already running on port 8000
) else (
    echo Starting backend server...
    start "PLAZA-AI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Waiting for backend to start...
    timeout /t 5 /nobreak >nul
)

echo.
echo [2/3] Starting Frontend...
echo.

cd ..\frontend

REM Check if frontend is already running
curl -s http://localhost:4200 >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Frontend is already running on port 4200
) else (
    echo Starting frontend server...
    start "PLAZA-AI Frontend" cmd /k "cd /d %~dp0frontend && npm start"
    echo Waiting for frontend to start...
    timeout /t 10 /nobreak >nul
)

echo.
echo [3/3] Opening Browser...
echo.

REM Wait a bit more for everything to be ready
timeout /t 3 /nobreak >nul

REM Open browser
start http://localhost:4200/chat

echo.
echo ========================================
echo   ALL SERVICES STARTED!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:4200
echo Chat:     http://localhost:4200/chat
echo.
echo Two windows opened:
echo   - Backend server (keep running)
echo   - Frontend server (keep running)
echo.
echo Browser should open automatically.
echo.
echo Press any key to close this window...
pause >nul


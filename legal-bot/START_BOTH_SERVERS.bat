@echo off
REM PLAZA-AI - Start Both Backend and Frontend Servers
REM This script starts both the backend and frontend together

echo ============================================================
echo PLAZA-AI - Starting Backend and Frontend Servers
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "backend\app\main.py" (
    echo [ERROR] Backend directory not found!
    echo Please run this script from the PLAZA-AI root directory.
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [ERROR] Frontend directory not found!
    echo Please run this script from the PLAZA-AI root directory.
    pause
    exit /b 1
)

echo [INFO] Starting Backend Server...
echo [INFO] Backend will run on: http://localhost:8000
echo.

REM Start backend in a new window
start "PLAZA-AI Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [INFO] Waiting for backend to start (5 seconds)...
timeout /t 5 /nobreak >nul

echo.
echo [INFO] Starting Frontend Server...
echo [INFO] Frontend will run on: http://localhost:4200
echo.

REM Start frontend in a new window
start "PLAZA-AI Frontend" cmd /k "cd frontend && npm start"

echo.
echo ============================================================
echo [SUCCESS] Both servers are starting!
echo ============================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:4200
echo.
echo Two new windows have opened:
echo   1. Backend server window
echo   2. Frontend server window
echo.
echo The frontend will automatically open in your browser.
echo.
echo To stop the servers, close the respective windows.
echo.
pause

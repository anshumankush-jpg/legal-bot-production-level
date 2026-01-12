@echo off
echo ========================================
echo Cleaning up port 8000 and restarting
echo ========================================
echo.

echo [1/3] Finding processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [2/3] Waiting for port to be free...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting backend...
cd backend
start "PLAZA-AI Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [OK] Backend starting in new window
echo [TIP] Wait 10-15 seconds for backend to fully start, then run tests
echo.
pause

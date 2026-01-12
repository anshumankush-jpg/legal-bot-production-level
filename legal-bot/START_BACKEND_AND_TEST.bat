@echo off
echo ========================================
echo Starting Backend with API Key
echo ========================================
echo.

cd backend
echo [INFO] Starting backend server...
echo [INFO] API Key is configured in .env file
echo.

start "PLAZA-AI Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [OK] Backend starting in new window
echo [TIP] Wait 15-20 seconds for backend to fully start
echo [TIP] Then test at: http://localhost:4202
echo.
pause

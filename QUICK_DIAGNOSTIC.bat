@echo off
echo ========================================
echo QUICK DIAGNOSTIC - Finding Main Problem
echo ========================================
echo.

echo [1/4] Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is running!
    goto :test_backend
) else (
    echo [FAIL] Backend is NOT running!
    echo.
    echo [PROBLEM FOUND] Backend needs to be started
    echo.
    echo [SOLUTION] Run this in a new terminal:
    echo   cd backend
    echo   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    echo.
    goto :end
)

:test_backend
echo.
echo [2/4] Testing backend API...
python test_backend_comprehensive.py
echo.

echo [3/4] Checking logs...
python view_logs.py
echo.

echo [4/4] Testing frontend connection...
python test_frontend_comprehensive.py
echo.

:end
echo ========================================
echo Diagnostic complete!
echo Check results above to identify problems.
echo ========================================
pause

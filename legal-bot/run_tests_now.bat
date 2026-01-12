@echo off
echo ========================================
echo Running Complex Legal Question Tests
echo ========================================
echo.

REM Check if backend is running
echo [1/3] Checking backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Backend is not running!
    echo Please start backend first:
    echo   cd backend
    echo   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    pause
    exit /b 1
)
echo [OK] Backend is running
echo.

REM Check API key
echo [2/3] Checking OpenAI API key...
python check_openai_balance.py >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] OpenAI API key not found or invalid
    echo Please add your API key to backend/.env
    echo.
)
echo.

REM Run tests
echo [3/3] Running complex question tests...
echo.
python test_complex_legal_questions.py

echo.
echo ========================================
echo Tests completed!
echo Check complex_test_results.json for details
echo ========================================
pause

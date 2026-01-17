@echo off
echo ========================================
echo Starting LEGID OAuth Servers
echo ========================================
echo.

echo [1/2] Starting Backend Server on port 8000...
start "LEGID Backend" cmd /k "cd /d C:\Users\anshu\Downloads\production_level\backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 >nul

echo [2/2] Starting Frontend Server on port 3000...
start "LEGID Frontend" cmd /k "cd /d C:\Users\anshu\Downloads\production_level\frontend && python -m http.server 3000"

timeout /t 2 >nul

echo.
echo ========================================
echo Servers Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Opening login page in 3 seconds...
timeout /t 3 >nul

start http://localhost:3000/legid-with-google-auth.html

echo.
echo ========================================
echo READY TO TEST GOOGLE OAUTH!
echo ========================================
echo.
echo Click "Sign in with Google" to test!
echo.
echo Press any key to close this window...
pause >nul

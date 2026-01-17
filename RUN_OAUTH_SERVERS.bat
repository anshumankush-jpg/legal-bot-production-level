@echo off
echo ========================================
echo LEGID OAuth - Starting Servers
echo ========================================

echo.
echo Starting Backend on port 8000...
start "LEGID Backend" /D "C:\Users\anshu\Downloads\production_level\backend" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 5 /nobreak > nul

echo Starting Frontend on port 3000...
start "LEGID Frontend" /D "C:\Users\anshu\Downloads\production_level\frontend" cmd /k "python -m http.server 3000"

timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo Opening Login Page...
echo ========================================
start http://localhost:3000/legid-with-google-auth.html

echo.
echo Servers should now be running!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause

@echo off
echo ========================================
echo Starting Artillity - Backend and Frontend
echo ========================================
echo.

echo [1] Starting Backend Server...
echo     This will open in a new window
echo     Wait 30-60 seconds for models to load
echo.
start "Artillity Backend" cmd /k "python api_server.py"

echo [2] Waiting 5 seconds before starting frontend...
timeout /t 5 /nobreak >nul

echo [3] Starting Frontend Server...
echo     Frontend will be at: http://localhost:5500
echo.
cd frontend
start "Artillity Frontend" cmd /k "python -m http.server 5500"
cd ..

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5500
echo.
echo IMPORTANT:
echo - Wait 30-60 seconds for backend models to load
echo - Look for "Server ready!" message in backend window
echo - Then refresh browser at http://localhost:5500
echo.
pause


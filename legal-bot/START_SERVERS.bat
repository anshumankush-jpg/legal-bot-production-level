@echo off
echo Starting PLAZA-AI Backend and Frontend Servers...
echo.

echo Starting Backend Server on port 8000...
start "PLAZA-AI Backend" cmd /k "cd /d %~dp0 && python start_local_server.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server on port 4200...
start "PLAZA-AI Frontend" cmd /k "cd /d %~dp0\frontend && npm start"

echo.
echo Servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4200
echo.
echo Press any key to exit this window (servers will continue running)...
pause >nul
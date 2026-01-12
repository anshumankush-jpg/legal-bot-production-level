@echo off
echo ========================================
echo  Restarting Frontend on Port 4200
echo ========================================
echo.

echo [1/3] Killing old Node processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] Starting frontend server...
cd frontend
start "LEGID Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo  Frontend Starting!
echo ========================================
echo.
echo  Wait 5 seconds, then open:
echo  http://localhost:4200
echo.
echo  Or check the new window for the actual port
echo ========================================
pause

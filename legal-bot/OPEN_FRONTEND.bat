@echo off
echo.
echo ========================================
echo   LeguBot - AI Legal Assistant
echo ========================================
echo.
echo Opening LeguBot in your browser...
echo.
echo Make sure the backend is running!
echo Backend should be at: http://127.0.0.1:8000
echo.

REM Open the frontend HTML file in the default browser
start "" "%~dp0frontend\legal-chat.html"

echo.
echo Frontend opened in your browser!
echo.
echo If the backend is not running, open a new terminal and run:
echo   cd backend
echo   python -m uvicorn app.main:app --reload
echo.
pause

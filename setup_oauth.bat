@echo off
REM Setup Google OAuth Credentials for LEGID
REM This script will help you configure OAuth securely

echo ========================================
echo LEGID - Google OAuth Setup
echo ========================================
echo.

REM Check if backend .env exists
if not exist "backend\.env" (
    echo Creating backend/.env file...
    copy backend\env_template.txt backend\.env
    echo ✓ Created backend/.env
) else (
    echo ✓ backend/.env already exists
)

echo.
echo ========================================
echo Adding Google OAuth Configuration
echo ========================================
echo.

REM Append OAuth settings to .env if not already present
findstr /C:"GOOGLE_CLIENT_ID" backend\.env >nul 2>&1
if errorlevel 1 (
    echo. >> backend\.env
    echo # Google OAuth Configuration >> backend\.env
    echo GOOGLE_CLIENT_ID=1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com >> backend\.env
    echo GOOGLE_CLIENT_SECRET=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 >> backend\.env
    echo GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google >> backend\.env
    echo.
    echo ✓ Google OAuth credentials added to backend/.env
) else (
    echo ⚠ Google OAuth credentials already exist in backend/.env
    echo   To update, manually edit backend/.env
)

echo.
echo ========================================
echo SECURITY WARNING
echo ========================================
echo.
echo ⚠ IMPORTANT: These credentials should be rotated!
echo.
echo You shared these credentials in chat. For security:
echo 1. Go to https://console.cloud.google.com/
echo 2. Navigate to APIs ^& Services ^> Credentials
echo 3. Find your OAuth 2.0 Client ID
echo 4. Click "Regenerate Secret"
echo 5. Update backend/.env with the new secret
echo.
echo ========================================
echo Setup Complete
echo ========================================
echo.
echo Next steps:
echo 1. Review backend/.env to verify settings
echo 2. Rotate the OAuth secret in Google Cloud Console
echo 3. Start the backend server: cd backend ^&^& python -m uvicorn app.main:app --reload
echo.
pause

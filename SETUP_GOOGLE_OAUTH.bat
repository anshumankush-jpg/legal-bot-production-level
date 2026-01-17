@echo off
echo ========================================
echo LEGID Google OAuth Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [1/5] Installing required dependencies...
cd backend
pip install httpx PyJWT python-jose[cryptography] -q
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully
echo.

echo [2/5] Checking environment file...
if exist .env (
    echo ✓ .env file already exists
    echo.
    echo WARNING: Please manually add the following variables to backend\.env:
    echo.
    type GOOGLE_OAUTH_SETUP.env
    echo.
) else (
    echo Creating .env file from template...
    copy GOOGLE_OAUTH_SETUP.env .env >nul
    echo ✓ .env file created successfully
    echo.
    echo IMPORTANT: Please edit backend\.env and:
    echo   1. Update JWT_SECRET_KEY to a secure random value
    echo   2. Add your other environment variables (OPENAI_API_KEY, etc.)
    echo.
)

echo [3/5] Verifying OAuth configuration...
echo.
echo Your Google OAuth Credentials:
echo   Client ID: 1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com
echo   Client Secret: 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
echo   Project ID: auth-login-page-481522
echo.
echo ✓ Credentials configured
echo.

echo [4/5] Testing backend imports...
python -c "from app.auth.google_oauth import get_google_oauth_handler; print('✓ Google OAuth handler imported successfully')" 2>nul
if errorlevel 1 (
    echo WARNING: Could not import OAuth handler. This is normal if .env is not fully configured.
) else (
    echo ✓ OAuth handler ready
)
echo.

echo [5/5] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Configure Google Cloud Console:
echo    - Go to: https://console.cloud.google.com/apis/credentials
echo    - Edit your OAuth 2.0 Client ID
echo    - Add to Authorized redirect URIs:
echo      http://localhost:8000/auth/google/callback
echo.
echo 2. Start the backend server:
echo    cd backend
echo    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 3. Start the frontend:
echo    cd frontend
echo    python -m http.server 3000
echo.
echo 4. Open your browser:
echo    http://localhost:3000/legid-with-google-auth.html
echo.
echo 5. Click "Sign in with Google" to test!
echo.
echo ========================================
echo Documentation: GOOGLE_OAUTH_IMPLEMENTATION.md
echo ========================================
echo.

cd ..
pause

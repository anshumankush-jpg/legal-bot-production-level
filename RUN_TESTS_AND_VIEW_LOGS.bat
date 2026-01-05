@echo off
echo ========================================
echo COMPREHENSIVE TEST SUITE WITH LOGGING
echo ========================================
echo.

echo [1/3] Running backend tests...
python test_backend_comprehensive.py
echo.

echo [2/3] Running frontend/backend integration tests...
python test_frontend_comprehensive.py
echo.

echo [3/3] Viewing logs and results...
python view_logs.py
echo.

echo ========================================
echo Tests complete! Check logs above.
echo ========================================
pause

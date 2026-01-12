@echo off
echo Starting Artillity Frontend...
echo.
echo Frontend will be available at: http://localhost:5500
echo Make sure the backend is running at: http://localhost:8000
echo.
cd frontend
python -m http.server 5500
pause


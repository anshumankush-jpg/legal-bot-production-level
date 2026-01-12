@echo off
echo ================================================================================
echo PLAZA-AI Legal Data Update Scheduler
echo ================================================================================
echo.
echo This will start the daily legal data update scheduler.
echo Updates run automatically at 2:00 AM every day.
echo.
echo Press Ctrl+C to stop the scheduler.
echo.
echo ================================================================================
echo.

cd backend
python daily_update_scheduler.py

pause

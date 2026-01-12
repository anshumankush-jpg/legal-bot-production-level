@echo off
REM Batch file to install Punjabi language pack
REM This will launch PowerShell with administrator privileges

echo ========================================
echo   Punjabi Language Pack Installer
echo ========================================
echo.
echo This will install Punjabi voice on your system.
echo.
echo IMPORTANT: You need Administrator privileges!
echo.
pause

echo.
echo Launching PowerShell as Administrator...
echo.

REM Check if PowerShell script exists
if not exist "install_punjabi_voice.ps1" (
    echo ERROR: install_punjabi_voice.ps1 not found!
    echo Please make sure you're in the correct directory.
    echo.
    pause
    exit /b 1
)

REM Launch PowerShell as Administrator
powershell -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0install_punjabi_voice.ps1\"' -Verb RunAs"

echo.
echo PowerShell window should open with Administrator privileges.
echo Follow the instructions in that window.
echo.
pause

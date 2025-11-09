@echo off
REM Library Online Management System - Windows Launcher
REM Double-click this file to start the application

echo ================================================
echo Library Online Management System
echo ================================================
echo.
echo Starting application...
echo.

python run.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start the application!
    echo Please ensure Python 3.7+ is installed.
    echo.
    pause
)



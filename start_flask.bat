@echo off
REM Library Online - Flask Application Launcher

echo ================================================
echo Library Online - Flask Web Application
echo ================================================
echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Flask application...
echo.
echo Application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python run.py

pause













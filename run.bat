@echo off
REM College ERP - Backend Startup Script for Windows

cls
echo ========================================
echo College ERP - Backend Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    exit /b 1
)

echo [✓] Python found
echo.

REM Create virtual environment if it doesn't exist (optional)
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo [✓] Virtual environment created
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat 2>nul
if exist venv\Scripts\activate.bat (
    echo [✓] Virtual environment activated
)

REM Install/upgrade requirements
echo.
echo Installing dependencies (this may take a minute)...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)
echo [✓] Dependencies installed
echo.

REM Create database directory if needed
if not exist "backend" (
    echo Error: backend directory not found
    exit /b 1
)

echo ========================================
echo Starting College ERP Backend Server
echo ========================================
echo.
echo URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Login: http://localhost:8000/login
echo.
echo Default Credentials:
echo   Email: admin@college.edu
echo   Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

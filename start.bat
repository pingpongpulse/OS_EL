@echo off
REM PhaseSentinel Startup Script for Windows

echo.
echo =====================================================
echo.       PhaseSentinel - AI-Powered Profiler
echo.
echo =====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python installed:
python --version

REM Navigate to backend directory
cd backend

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q -r requirements.txt

REM Create necessary directories
if not exist "models" mkdir models
if not exist "data" mkdir data

REM Show configuration
echo.
echo =====================================================
echo  PhaseSentinel Configuration
echo =====================================================
echo.
echo  Backend URL:  http://localhost:5000
echo  Dashboard:    http://localhost:5000/dashboard
echo  API Docs:     http://localhost:5000/api/health
echo.
echo  Data Dir:     ./data
echo  Models Dir:   ./models
echo.
echo Starting Flask server...
echo.
echo Press Ctrl+C to stop
echo =====================================================
echo.

REM Start the Flask server
python app.py

pause

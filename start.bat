@echo off
setlocal enabledelayedexpansion

echo ============================================
echo FLDIGI Web Interface - Auto Startup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python detected
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Check if requirements are installed (check for fastapi)
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing dependencies...
    echo This may take a few minutes...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed successfully
    echo.
) else (
    echo [OK] Dependencies already installed
    echo.
)

REM Check if FLDIGI is running (optional check)
echo [INFO] Checking for FLDIGI...
timeout /t 2 /nobreak >nul
echo [NOTE] Make sure FLDIGI is running with XML-RPC enabled on port 7362
echo.

REM Start the backend server
echo ============================================
echo Starting FLDIGI Web Interface...
echo ============================================
echo.
echo [INFO] Server starting on http://localhost:8000
echo [INFO] Open your browser and navigate to: http://localhost:8000
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Start the server
python -m backend.main

REM If server stops, pause so user can see error messages
echo.
echo [INFO] Server stopped
pause

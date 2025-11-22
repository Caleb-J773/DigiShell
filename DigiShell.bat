@echo off
setlocal enabledelayedexpansion

echo ============================================
echo DigiShell - Digital Mode Interface
echo ============================================
echo.

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

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

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

echo ============================================
echo Verifying FlDigi Connection
echo ============================================
echo.

set FLDIGI_RUNNING=0

echo [INFO] Checking if FlDigi is running...
tasklist /FI "IMAGENAME eq fldigi.exe" 2>NUL | find /I /N "fldigi.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] FlDigi process detected
    set FLDIGI_RUNNING=1
) else (
    echo [WARNING] FlDigi process not detected
)
echo.

if !FLDIGI_RUNNING! EQU 0 (
    echo [INFO] Attempting to start FlDigi...
    echo.

    set "FLDIGI_FOUND=0"
    set "FLDIGI_PATH="

    for /d %%D in ("C:\Program Files\Fldigi*") do (
        if exist "%%D\fldigi.exe" (
            set "FLDIGI_PATH=%%D\fldigi.exe"
            set "FLDIGI_FOUND=1"
            goto :fldigi_found
        )
    )

    for /d %%D in ("C:\Program Files (x86)\Fldigi*") do (
        if exist "%%D\fldigi.exe" (
            set "FLDIGI_PATH=%%D\fldigi.exe"
            set "FLDIGI_FOUND=1"
            goto :fldigi_found
        )
    )

    if exist "C:\Program Files\fldigi\fldigi.exe" (
        set "FLDIGI_PATH=C:\Program Files\fldigi\fldigi.exe"
        set "FLDIGI_FOUND=1"
        goto :fldigi_found
    )

    if exist "C:\Program Files (x86)\fldigi\fldigi.exe" (
        set "FLDIGI_PATH=C:\Program Files (x86)\fldigi\fldigi.exe"
        set "FLDIGI_FOUND=1"
        goto :fldigi_found
    )

    :fldigi_found
    if !FLDIGI_FOUND! EQU 1 (
        echo [OK] Found FlDigi at: !FLDIGI_PATH!

        REM Start FlDigi in normal mode
        REM NOTE: We DON'T use --wfall-only because it disables rig control subsystems
        REM which causes FlDigi to crash when trying to key PTT via Hamlib/Flrig
        start "" "!FLDIGI_PATH!"
        echo [OK] FlDigi started, waiting for initialization...
        timeout /t 5 /nobreak >nul
        echo.
    ) else (
        echo [WARNING] FlDigi not found in common installation paths
        echo Please start FlDigi manually and ensure XML-RPC is enabled
        echo.
        echo Searched in:
        echo - C:\Program Files\Fldigi*\fldigi.exe
        echo - C:\Program Files ^(x86^)\Fldigi*\fldigi.exe
        echo.
        echo After starting FlDigi manually, you can continue below.
        echo.
        pause
        echo.
    )
)

echo [INFO] Verifying XML-RPC port 7362...
powershell -Command "$client = New-Object System.Net.Sockets.TcpClient; try { $client.Connect('127.0.0.1', 7362); $client.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot connect to XML-RPC port 7362
    echo.
    echo FlDigi must be running with XML-RPC enabled:
    echo 1. Open FlDigi
    echo 2. Go to Configure ^> Misc ^> XML-RPC Server
    echo 3. Check "Enable XML-RPC Server"
    echo 4. Set Address: 127.0.0.1
    echo 5. Set Port: 7362
    echo 6. Click Apply and restart FlDigi
    echo.
    pause
    exit /b 1
)

echo [OK] XML-RPC port 7362 is accessible
echo [OK] FlDigi connection verified
echo.

echo ============================================
echo Select Interface Mode
echo ============================================
echo.
echo [1] Web Interface (Browser-based)
echo [2] Terminal UI (Console-based)
echo.
choice /C 12 /M "Select interface mode"
set INTERFACE_MODE=%ERRORLEVEL%

timeout /t 2 /nobreak >nul
echo.
echo ============================================
if !INTERFACE_MODE! EQU 1 (
    echo DigiShell - Starting Server
    echo ============================================
    echo.
    echo [INFO] Server starting on http://localhost:8000
    echo [INFO] Open your browser and navigate to: http://localhost:8000
    echo [INFO] Press Ctrl+C to stop the server
    echo.
    python -m backend.main
) else (
    echo Starting DigiShell Terminal UI
    echo ============================================
    echo.
    echo [INFO] Starting terminal interface...
    echo [INFO] Press Ctrl+C to exit
    echo.
    python run_tui.py
)

echo.
echo [INFO] DigiShell stopped
pause

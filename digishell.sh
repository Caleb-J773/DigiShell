#!/bin/bash

echo "============================================"
echo "DigiShell - Digital Mode Interface"
echo "============================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python is not installed or not in PATH"
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[OK] Python detected"
python3 --version
echo ""

if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo "[OK] Virtual environment created"
    echo ""
fi

echo "[INFO] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "[OK] Virtual environment activated"
echo ""

python -c "import fastapi" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[SETUP] Installing dependencies..."
    echo "This may take a few minutes..."
    echo ""
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo ""
    echo "[OK] Dependencies installed successfully"
    echo ""
else
    echo "[OK] Dependencies already installed"
    echo ""
fi

echo "============================================"
echo "Verifying FlDigi Connection"
echo "============================================"
echo ""

FLDIGI_RUNNING=0

echo "[INFO] Checking if FlDigi is running..."
if pgrep -x "fldigi" > /dev/null; then
    echo "[OK] FlDigi process detected"
    FLDIGI_RUNNING=1
else
    echo "[WARNING] FlDigi process not detected"
fi
echo ""

if [ $FLDIGI_RUNNING -eq 0 ]; then
    echo "[INFO] Attempting to start FlDigi..."
    echo ""

    FLDIGI_FOUND=0
    FLDIGI_PATH=""

    if command -v fldigi &> /dev/null; then
        FLDIGI_PATH=$(command -v fldigi)
        FLDIGI_FOUND=1
    elif [ -x "/usr/bin/fldigi" ]; then
        FLDIGI_PATH="/usr/bin/fldigi"
        FLDIGI_FOUND=1
    elif [ -x "/usr/local/bin/fldigi" ]; then
        FLDIGI_PATH="/usr/local/bin/fldigi"
        FLDIGI_FOUND=1
    elif [ -x "$HOME/.local/bin/fldigi" ]; then
        FLDIGI_PATH="$HOME/.local/bin/fldigi"
        FLDIGI_FOUND=1
    fi

    if [ $FLDIGI_FOUND -eq 1 ]; then
        echo "[OK] Found FlDigi at: $FLDIGI_PATH"
        "$FLDIGI_PATH" &> /dev/null &
        echo "[OK] FlDigi started, waiting for initialization..."
        sleep 5
        echo ""
    else
        echo "[WARNING] FlDigi not found in common installation paths"
        echo "Please start FlDigi manually and ensure XML-RPC is enabled"
        echo ""
        echo "Searched in:"
        echo "  - /usr/bin/fldigi"
        echo "  - /usr/local/bin/fldigi"
        echo "  - \$HOME/.local/bin/fldigi"
        echo "  - PATH"
        echo ""
        echo "After starting FlDigi manually, you can continue below."
        echo ""
        read -p "Press Enter to continue..."
        echo ""
    fi
fi

echo "[INFO] Verifying XML-RPC port 7362..."
if timeout 2 bash -c "</dev/tcp/127.0.0.1/7362" &> /dev/null; then
    echo "[OK] XML-RPC port 7362 is accessible"
    echo "[OK] FlDigi connection verified"
    echo ""
else
    echo "[ERROR] Cannot connect to XML-RPC port 7362"
    echo ""
    echo "FlDigi must be running with XML-RPC enabled:"
    echo "1. Open FlDigi"
    echo "2. Go to Configure > Misc > XML-RPC Server"
    echo "3. Check \"Enable XML-RPC Server\""
    echo "4. Set Address: 127.0.0.1"
    echo "5. Set Port: 7362"
    echo "6. Click Apply and restart FlDigi"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "============================================"
echo "Select Interface Mode"
echo "============================================"
echo ""
echo "[1] Web Interface (Browser-based)"
echo "[2] Terminal UI (Console-based)"
echo ""

while true; do
    read -p "Select interface mode (1 or 2): " INTERFACE_MODE
    case $INTERFACE_MODE in
        1|2)
            break
            ;;
        *)
            echo "Invalid selection. Please enter 1 or 2."
            ;;
    esac
done

if [ "$INTERFACE_MODE" = "1" ]; then
    echo ""
    echo "============================================"
    echo "Server Configuration"
    echo "============================================"
    echo ""
    echo "The default settings work for EVERYONE (local, LAN, and VPN access):"
    echo "  - Host: 0.0.0.0 (accessible on your local network)"
    echo "  - Port: 8000"
    echo ""
    echo "Only customize if you know you need to (most users should choose No)."
    echo ""
    read -p "Customize server settings? (y/N): " CUSTOMIZE

    if [[ "$CUSTOMIZE" =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Enter bind address (0.0.0.0 for all, 127.0.0.1 for local only) [0.0.0.0]: " CUSTOM_HOST
        CUSTOM_HOST=${CUSTOM_HOST:-0.0.0.0}

        read -p "Enter port number [8000]: " CUSTOM_PORT
        CUSTOM_PORT=${CUSTOM_PORT:-8000}

        export DIGISHELL_HOST="$CUSTOM_HOST"
        export DIGISHELL_PORT="$CUSTOM_PORT"
    else
        export DIGISHELL_HOST="0.0.0.0"
        export DIGISHELL_PORT="8000"
    fi
fi

sleep 2
echo ""
echo "============================================"

if [ "$INTERFACE_MODE" = "1" ]; then
    echo "DigiShell - Starting Server"
    echo "============================================"
    echo ""
    echo "[WARNING] SECURITY NOTICE"
    echo "This server is for LOCAL USE ONLY or trusted LAN/VPN access."
    echo "NEVER expose this to the public internet - it has no authentication!"
    echo "Anyone with access can control your radio station."
    echo ""
    echo "[INFO] Server starting on http://localhost:${DIGISHELL_PORT}"
    echo "[INFO] Open your browser and navigate to: http://localhost:${DIGISHELL_PORT}"
    echo "[INFO] Press Ctrl+C to stop the server"
    echo ""
    python -m backend.main
else
    echo "Starting DigiShell Terminal UI"
    echo "============================================"
    echo ""
    echo "[INFO] Starting terminal interface..."
    echo "[INFO] Press Ctrl+C to exit"
    echo ""
    python run_tui.py
fi

echo ""
echo "[INFO] DigiShell stopped"

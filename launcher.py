import sys
import os
import subprocess
import time
import glob
from pathlib import Path
from backend.utils import check_port_available


def print_header(title):
    print("\n" + "=" * 44)
    print(title)
    print("=" * 44)
    print()

def check_python():
    print(f"[OK] Python detected")
    print(f"Python {sys.version.split()[0]}")
    print()

def setup_venv():
    if not os.path.exists("venv"):
        print("[SETUP] Creating virtual environment...")
        result = subprocess.run([sys.executable, "-m", "venv", "venv"], capture_output=True)
        if result.returncode != 0:
            print("[ERROR] Failed to create virtual environment")
            input("Press Enter to exit...")
            sys.exit(1)
        print("[OK] Virtual environment created")
        print()

def activate_venv():
    print("[INFO] Activating virtual environment...")
    venv_python = os.path.join("venv", "Scripts", "python.exe") if sys.platform == "win32" else os.path.join("venv", "bin", "python")

    if not os.path.exists(venv_python):
        print("[ERROR] Virtual environment not found")
        input("Press Enter to exit...")
        sys.exit(1)

    print("[OK] Virtual environment activated")
    print()
    return venv_python

def check_dependencies(python_exe):
    result = subprocess.run([python_exe, "-c", "import fastapi"], capture_output=True, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        print("[SETUP] Installing dependencies...")
        print("This may take a few minutes...")
        print()

        result = subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"])
        if result.returncode != 0:
            print("[ERROR] Failed to install dependencies")
            input("Press Enter to exit...")
            sys.exit(1)

        print()
        print("[OK] Dependencies installed successfully")
        print()
    else:
        print("[OK] Dependencies already installed")
        print()

def is_fldigi_running():
    if sys.platform == "win32":
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq fldigi.exe"],
            capture_output=True,
            text=True
        )
        return "fldigi.exe" in result.stdout.lower()
    else:
        result = subprocess.run(["pgrep", "-x", "fldigi"], capture_output=True)
        return result.returncode == 0

def find_fldigi_windows():
    search_paths = [
        r"C:\Program Files\Fldigi*\fldigi.exe",
        r"C:\Program Files (x86)\Fldigi*\fldigi.exe",
        r"C:\Program Files\fldigi\fldigi.exe",
        r"C:\Program Files (x86)\fldigi\fldigi.exe",
    ]

    for pattern in search_paths[:2]:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    for exact_path in search_paths[2:]:
        if os.path.exists(exact_path):
            return exact_path

    return None

def find_fldigi_linux():
    from shutil import which

    fldigi_path = which("fldigi")
    if fldigi_path:
        return fldigi_path

    paths = [
        "/usr/bin/fldigi",
        "/usr/local/bin/fldigi",
        os.path.expanduser("~/.local/bin/fldigi"),
    ]

    for path in paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    return None

def start_fldigi():
    print("[INFO] Attempting to start FlDigi...")
    print()

    if sys.platform == "win32":
        fldigi_path = find_fldigi_windows()
    else:
        fldigi_path = find_fldigi_linux()

    if fldigi_path:
        print(f"[OK] Found FlDigi at: {fldigi_path}")

        if sys.platform == "win32":
            subprocess.Popen([fldigi_path], shell=True)
        else:
            subprocess.Popen([fldigi_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("[OK] FlDigi started, waiting for initialization...")
        time.sleep(5)
        print()
        return True
    else:
        print("[WARNING] FlDigi not found in common installation paths")
        print("Please start FlDigi manually and ensure XML-RPC is enabled")
        print()

        if sys.platform == "win32":
            print("Searched in:")
            print("  - C:\\Program Files\\Fldigi*\\fldigi.exe")
            print("  - C:\\Program Files (x86)\\Fldigi*\\fldigi.exe")
        else:
            print("Searched in:")
            print("  - /usr/bin/fldigi")
            print("  - /usr/local/bin/fldigi")
            print("  - $HOME/.local/bin/fldigi")
            print("  - PATH")

        print()
        print("After starting FlDigi manually, you can continue below.")
        print()
        input("Press Enter to continue...")
        print()
        return False

def check_xmlrpc_port():
    print("[INFO] Verifying XML-RPC port 7362...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 7362))
        sock.close()

        if result == 0:
            print("[OK] XML-RPC port 7362 is accessible")
            print("[OK] FlDigi connection verified")
            print()
            return True
        else:
            raise ConnectionRefusedError
    except (ConnectionRefusedError, OSError):
        print("[ERROR] Cannot connect to XML-RPC port 7362")
        print()
        print("FlDigi must be running with XML-RPC enabled:")
        print("1. Open FlDigi")
        print("2. Go to Configure > Misc > XML-RPC Server")
        print("3. Check \"Enable XML-RPC Server\"")
        print("4. Set Address: 127.0.0.1")
        print("5. Set Port: 7362")
        print("6. Click Apply and restart FlDigi")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

def select_interface():
    print_header("Select Interface Mode")
    print("[1] Web Interface (Browser-based)")
    print("[2] Terminal UI (Console-based)")
    print()

    while True:
        try:
            choice = input("Select interface mode (1 or 2): ").strip()
            if choice in ["1", "2"]:
                return int(choice)
            else:
                print("Invalid selection. Please enter 1 or 2.")
        except (ValueError, KeyboardInterrupt):
            print()
            sys.exit(0)

def main():
    print_header("DigiShell - Digital Mode Interface")

    check_python()

    if getattr(sys, 'frozen', False):
        python_exe = sys.executable
        print("[INFO] Running from packaged executable")
        print()
    else:
        setup_venv()
        python_exe = activate_venv()
        check_dependencies(python_exe)

    print_header("Verifying FlDigi Connection")

    print("[INFO] Checking if FlDigi is running...")
    if is_fldigi_running():
        print("[OK] FlDigi process detected")
        print()
    else:
        print("[WARNING] FlDigi process not detected")
        print()
        start_fldigi()

    check_xmlrpc_port()

    interface_mode = select_interface()

    time.sleep(2)
    print()

    print("=" * 44)

    if interface_mode == 1:
        # Get port from environment variable or use default
        try:
            port = int(os.environ.get('DIGISHELL_PORT', 8000))
        except ValueError:
            print("[ERROR] Invalid DIGISHELL_PORT value. Using default port 8000.")
            port = 8000

        # Check if port is available
        if not check_port_available(port):
            print()
            print("=" * 44)
            print(f"ERROR: Port {port} is already in use!")
            print("=" * 44)
            print()
            print("Another application is using this port.")
            print()
            print("Options:")
            print("1. Close the other application")
            print("2. Use a different port:")
            if sys.platform == "win32":
                print("   set DIGISHELL_PORT=8080")
            else:
                print("   export DIGISHELL_PORT=8080")
            print()
            print("Then restart DigiShell")
            print("=" * 44)
            input("\nPress Enter to exit...")
            sys.exit(1)

        print("DigiShell - Starting Server")
        print("=" * 44)
        print()
        print(f"[INFO] Server starting on http://localhost:{port}")
        print(f"[INFO] Open your browser and navigate to: http://localhost:{port}")
        print("[INFO] Press Ctrl+C to stop the server")
        print()

        if getattr(sys, 'frozen', False):
            import uvicorn
            from backend.main import app
            try:
                uvicorn.run(
                    app,
                    host="0.0.0.0",
                    port=port,
                    log_level="warning",
                    access_log=False
                )
            except OSError as e:
                if "address already in use" in str(e).lower() or "10048" in str(e):
                    print()
                    print("=" * 44)
                    print(f"ERROR: Failed to bind to port {port}")
                    print("=" * 44)
                    print()
                    print("The port became unavailable while starting.")
                    print("Please use DIGISHELL_PORT to set a different port.")
                    print("=" * 44)
                    input("\nPress Enter to exit...")
                    sys.exit(1)
                else:
                    raise
        else:
            subprocess.run([python_exe, "-m", "backend.main"])
    else:
        print("Starting DigiShell Terminal UI")
        print("=" * 44)
        print()
        print("[INFO] Starting terminal interface...")
        print("[INFO] Press Ctrl+C to exit")
        print()

        if getattr(sys, 'frozen', False):
            from run_tui import main as tui_main
            tui_main()
        else:
            subprocess.run([python_exe, "run_tui.py"])

    print()
    print("[INFO] DigiShell stopped")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("[INFO] DigiShell stopped")
        sys.exit(0)

import uvicorn
import logging
import signal
import sys
import os
from backend.utils import check_port_available, get_network_ips

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('pyfldigi').setLevel(logging.ERROR)
logging.getLogger('backend.fldigi_client').setLevel(logging.ERROR)
logging.getLogger('uvicorn').setLevel(logging.ERROR)
logging.getLogger('uvicorn.access').setLevel(logging.ERROR)


def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get port from environment variable or use default
    try:
        port = int(os.environ.get('DIGISHELL_PORT', 8000))
    except ValueError:
        print(f"ERROR: Invalid DIGISHELL_PORT value. Using default port 8000.")
        port = 8000

    # Check if port is available
    if not check_port_available(port):
        print()
        print("=" * 60)
        print(f"ERROR: Port {port} is already in use!")
        print("=" * 60)
        print()
        print("Another application is using this port. You have a few options:")
        print()
        print("1. Find and close the application using this port:")
        if sys.platform == "win32":
            print(f"   netstat -ano | findstr :{port}")
        else:
            print(f"   lsof -i :{port}")
            print(f"   netstat -tulpn | grep :{port}")
        print()
        print("2. Use a different port by setting the DIGISHELL_PORT environment variable:")
        if sys.platform == "win32":
            print("   Windows CMD:        set DIGISHELL_PORT=8080")
            print("   Windows PowerShell: $env:DIGISHELL_PORT=8080")
        else:
            print(f"   export DIGISHELL_PORT=8080")
        print()
        print("3. Then run DigiShell again")
        print()
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("FLDIGI Layer - Starting Server")
    print("=" * 60)
    print()
    print("Access URLs:")
    print(f"  Local:    http://localhost:{port}")

    network_ips = get_network_ips()
    if network_ips:
        for interface, ip in network_ips:
            label = f"({interface})" if interface else ""
            print(f"  Network:  http://{ip}:{port} {label}")

    print()
    print(f"API Docs:   http://localhost:{port}/docs")
    print(f"WebSocket:  ws://localhost:{port}/ws")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print()

    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="warning",
            access_log=False
        )
    except OSError as e:
        if "address already in use" in str(e).lower() or "10048" in str(e):
            print()
            print("=" * 60)
            print(f"ERROR: Failed to bind to port {port}")
            print("=" * 60)
            print()
            print("The port became unavailable while starting.")
            print("Please use a different port with DIGISHELL_PORT environment variable.")
            print("=" * 60)
            sys.exit(1)
        else:
            raise

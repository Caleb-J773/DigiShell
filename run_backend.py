import uvicorn
import logging
import signal
import sys
import socket
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('pyfldigi').setLevel(logging.ERROR)
logging.getLogger('backend.fldigi_client').setLevel(logging.ERROR)
logging.getLogger('uvicorn').setLevel(logging.ERROR)
logging.getLogger('uvicorn.access').setLevel(logging.ERROR)

def get_network_ips():
    ips = []
    try:
        import netifaces
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if ip != '127.0.0.1':
                        ips.append((interface, ip))
    except ImportError:
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
            if ip != '127.0.0.1':
                ips.append(('default', ip))
        except:
            pass
    return ips

def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get configuration from environment variables
    host = os.getenv("DIGISHELL_HOST", "0.0.0.0")
    port = int(os.getenv("DIGISHELL_PORT", "8000"))

    print("=" * 60)
    print("DigiShell - Starting Server")
    print("=" * 60)
    print()
    print(f"Bind Address: {host}")
    print(f"Port:         {port}")
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

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="warning",
        access_log=False
    )

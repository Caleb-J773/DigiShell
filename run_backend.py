import uvicorn
import logging
import signal
import sys
import socket

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

    print("=" * 60)
    print("FLDIGI Layer - Starting Server")
    print("=" * 60)
    print()
    print("Access URLs:")
    print(f"  Local:    http://localhost:8000")

    network_ips = get_network_ips()
    if network_ips:
        for interface, ip in network_ips:
            label = f"({interface})" if interface else ""
            print(f"  Network:  http://{ip}:8000 {label}")

    print()
    print("API Docs:   http://localhost:8000/docs")
    print("WebSocket:  ws://localhost:8000/ws")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print()

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="warning",
        access_log=False
    )

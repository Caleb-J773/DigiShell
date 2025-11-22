import socket


def check_port_available(port):
    """Check if a port is available for binding."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except OSError:
        return False


def get_network_ips():
    """Get list of network interface IPs (excluding localhost)."""
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
        except (OSError, socket.gaierror):
            pass
    return ips

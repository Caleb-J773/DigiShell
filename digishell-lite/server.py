#!/usr/bin/env python3
"""
DigiShell Lite - Minimal FLDigi Web Interface
Zero external dependencies - Python 3.10+ stdlib only
"""

import http.server
import socketserver
import json
import xmlrpc.client
import threading
import time
import os
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any


FLDIGI_HOST = os.getenv('FLDIGI_HOST', '127.0.0.1')
FLDIGI_PORT = int(os.getenv('FLDIGI_PORT', '7362'))
SERVER_PORT = int(os.getenv('SERVER_PORT', '8080'))


class FldigiXMLRPC:
    """Minimal XML-RPC client for FLDigi using stdlib only"""

    def __init__(self, host: str = FLDIGI_HOST, port: int = FLDIGI_PORT):
        self.url = f"http://{host}:{port}"
        self.proxy = None
        self.connected = False

    def connect(self) -> tuple[bool, Optional[str]]:
        try:
            self.proxy = xmlrpc.client.ServerProxy(self.url)
            self.proxy.fldigi.name()
            self.connected = True
            return True, None
        except Exception as e:
            self.connected = False
            return False, f"Failed to connect: {str(e)}"

    def call(self, method: str, *args):
        """Make an XML-RPC call to FLDigi"""
        if not self.proxy:
            return None
        try:
            parts = method.split('.')
            obj = self.proxy
            for part in parts:
                obj = getattr(obj, part)
            return obj(*args) if args else obj()
        except Exception as e:
            print(f"XML-RPC error calling {method}: {e}")
            return None

    def get_rx_text(self) -> str:
        """Get all received text"""
        length = self.call('text.get_rx_length')
        if length and length > 0:
            result = self.call('text.get_rx', 0, length)
            if result:
                if isinstance(result, xmlrpc.client.Binary):
                    return result.data.decode('utf-8', errors='replace')
                return str(result)
        return ""

    def add_tx_text(self, text: str) -> bool:
        """Add text to transmit buffer"""
        result = self.call('text.add_tx', text)
        return result is not None

    def clear_tx(self) -> bool:
        """Clear transmit buffer"""
        result = self.call('text.clear_tx')
        return result is not None

    def clear_rx(self) -> bool:
        """Clear receive buffer"""
        result = self.call('text.clear_rx')
        return result is not None

    def get_trx_status(self) -> str:
        """Get current TX/RX status"""
        status = self.call('main.get_trx_status')
        if status == 'tx':
            return 'tx'
        elif status == 'tune':
            return 'tune'
        else:
            return 'rx'

    def tx(self) -> bool:
        """Start transmitting"""
        result = self.call('main.tx')
        return result is not None

    def rx(self) -> bool:
        """Switch to receive"""
        result = self.call('main.rx')
        return result is not None

    def tune(self) -> bool:
        """Start tuning"""
        result = self.call('main.tune')
        return result is not None

    def abort(self) -> bool:
        """Abort TX/TUNE"""
        result = self.call('main.abort')
        return result is not None

    def get_modem(self) -> Optional[str]:
        """Get current modem name"""
        return self.call('modem.get_name')

    def set_modem(self, modem: str) -> bool:
        """Set modem by name"""
        result = self.call('modem.set_by_name', modem)
        return result is not None

    def get_modem_names(self) -> list:
        """Get list of available modems"""
        result = self.call('modem.get_names')
        return result if result else []

    def get_carrier(self) -> Optional[int]:
        """Get carrier frequency"""
        return self.call('modem.get_carrier')

    def set_carrier(self, freq: int) -> bool:
        """Set carrier frequency"""
        result = self.call('modem.set_carrier', freq)
        return result is not None

    def get_afc(self) -> Optional[bool]:
        """Get AFC state"""
        return self.call('main.get_afc')

    def set_afc(self, state: bool) -> bool:
        """Set AFC state"""
        result = self.call('main.set_afc', state)
        return result is not None


fldigi = FldigiXMLRPC()


class MinimalHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for the minimal interface"""

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/' or path == '/index.html':
            self.serve_html()
        elif path == '/api/status':
            self.api_status()
        elif path == '/api/rx':
            self.api_get_rx()
        elif path == '/api/modem':
            self.api_get_modem()
        elif path == '/api/modems':
            self.api_get_modems()
        elif path == '/api/carrier':
            self.api_get_carrier()
        elif path == '/api/afc':
            self.api_get_afc()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        if path == '/api/tx':
            self.api_tx(data)
        elif path == '/api/rx/switch':
            self.api_switch_rx()
        elif path == '/api/tune':
            self.api_tune()
        elif path == '/api/abort':
            self.api_abort()
        elif path == '/api/tx/text':
            self.api_add_tx_text(data)
        elif path == '/api/rx/clear':
            self.api_clear_rx()
        elif path == '/api/tx/clear':
            self.api_clear_tx()
        elif path == '/api/modem':
            self.api_set_modem(data)
        elif path == '/api/carrier':
            self.api_set_carrier(data)
        elif path == '/api/afc':
            self.api_set_afc(data)
        else:
            self.send_error(404)

    def serve_html(self):
        """Serve the main HTML interface"""
        html_path = os.path.join(os.path.dirname(__file__), 'index.html')
        try:
            with open(html_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "index.html not found")

    def json_response(self, data: dict, status: int = 200):
        """Send JSON response"""
        response = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response)

    def api_status(self):
        """Get TX/RX status"""
        if not fldigi.connected:
            self.json_response({"connected": False, "status": "disconnected"})
            return

        status = fldigi.get_trx_status()
        self.json_response({
            "connected": True,
            "status": status or "unknown"
        })

    def api_get_rx(self):
        """Get RX text"""
        text = fldigi.get_rx_text() if fldigi.connected else ""
        self.json_response({"text": text})

    def api_tx(self, data: dict):
        """Start TX"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        success = fldigi.tx()
        self.json_response({"success": success})

    def api_switch_rx(self):
        """Switch to RX"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        success = fldigi.rx()
        self.json_response({"success": success})

    def api_tune(self, data: dict):
        """Start TUNE"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        success = fldigi.tune()
        self.json_response({"success": success})

    def api_abort(self):
        """Abort TX/TUNE"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        success = fldigi.abort()
        self.json_response({"success": success})

    def api_add_tx_text(self, data: dict):
        """Add text to TX buffer"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        text = data.get('text', '')
        success = fldigi.add_tx_text(text)
        self.json_response({"success": success})

    def api_clear_rx(self):
        """Clear RX buffer"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        success = fldigi.clear_rx()
        self.json_response({"success": success})

    def api_clear_tx(self):
        """Clear TX buffer"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        success = fldigi.clear_tx()
        self.json_response({"success": success})

    def api_get_modem(self):
        """Get current modem"""
        modem = fldigi.get_modem() if fldigi.connected else None
        carrier = fldigi.get_carrier() if fldigi.connected else None
        self.json_response({
            "modem": modem,
            "carrier": carrier
        })

    def api_get_modems(self):
        """Get available modems"""
        modems = fldigi.get_modem_names() if fldigi.connected else []
        self.json_response({"modems": modems})

    def api_set_modem(self, data: dict):
        """Set modem"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        modem = data.get('modem', '')
        success = fldigi.set_modem(modem)
        self.json_response({"success": success})

    def api_get_carrier(self):
        """Get carrier frequency"""
        carrier = fldigi.get_carrier() if fldigi.connected else None
        self.json_response({"carrier": carrier})

    def api_set_carrier(self, data: dict):
        """Set carrier frequency"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        carrier = data.get('carrier', 0)
        success = fldigi.set_carrier(int(carrier))
        self.json_response({"success": success})

    def api_get_afc(self):
        """Get AFC state"""
        afc = fldigi.get_afc() if fldigi.connected else False
        self.json_response({"afc": afc})

    def api_set_afc(self, data: dict):
        """Set AFC state"""
        if not fldigi.connected:
            self.json_response({"success": False, "error": "Not connected"}, 500)
            return

        afc = data.get('afc', False)
        success = fldigi.set_afc(bool(afc))
        self.json_response({"success": success})

    def log_message(self, format, *args):
        """Override to suppress request logging"""
        pass


def main():
    print("=" * 60)
    print("DigiShell Lite - Minimal FLDigi Remote Interface")
    print("=" * 60)
    print(f"\nFLDigi Connection: {FLDIGI_HOST}:{FLDIGI_PORT}")

    print("\nConnecting to FLDigi...")
    success, error = fldigi.connect()

    if success:
        print("✓ Connected to FLDigi successfully!")
        modem = fldigi.get_modem()
        if modem:
            print(f"  Current modem: {modem}")
    else:
        print(f"✗ Warning: Could not connect to FLDigi")
        print(f"  {error}")
        print(f"  Make sure FLDigi is running with XML-RPC enabled")
        print(f"  The server will start anyway, but won't work until FLDigi is available")

    print(f"\nStarting web server on port {SERVER_PORT}...")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", SERVER_PORT), MinimalHandler) as httpd:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        print(f"\n{'=' * 60}")
        print("Server is running!")
        print(f"{'=' * 60}")
        print(f"\nAccess the interface at:")
        print(f"  Local:   http://localhost:{SERVER_PORT}")
        print(f"  Network: http://{local_ip}:{SERVER_PORT}")
        print(f"\nPress Ctrl+C to stop the server")
        print(f"{'=' * 60}\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            print("Goodbye!")


if __name__ == "__main__":
    main()

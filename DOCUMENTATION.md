# DigiShell - Technical Documentation

Complete technical documentation for the DigiShell project.

## Table of Contents
1. [Architecture](#architecture)
2. [API Reference](#api-reference)
3. [WebSocket Protocol](#websocket-protocol)
4. [Configuration](#configuration)
5. [Macro System](#macro-system)
6. [Keybind System](#keybind-system)
7. [Development](#development)
8. [Troubleshooting](#troubleshooting)

---

## Architecture

### System Overview
```
┌─────────────────┐         WebSocket/REST          ┌──────────────────┐
│   Web Browser   │◄────────────────────────────────┤  FastAPI Server  │
│   (Frontend)    │                                 │   (Backend)      │
└─────────────────┘                                 └────────┬─────────┘
                                                             │
       OR                                                    │ XML-RPC
                                                             │ (pyFldigi)
┌─────────────────┐                                         │
│   Terminal UI   │─────────────────────────────────────────┤
│   (run_tui.py)  │         Direct XML-RPC                  │
└─────────────────┘                                 ┌────────▼─────────┐
                                                    │   FLDIGI App     │
                                                    │  (localhost:7362)│
                                                    └──────────────────┘
```

### Backend Structure
- **FastAPI Application** (`backend/main.py`) - ASGI web server
- **FLDIGI Client** (`backend/fldigi_client.py`) - XML-RPC wrapper with live TX support
- **WebSocket Manager** (`backend/websocket_manager.py`) - Real-time client updates
- **Routers** - Modular API endpoint handlers:
  - `routers/modem.py` - Modem control
  - `routers/txrx.py` - Transmit/receive operations
  - `routers/rig.py` - Rig control (frequency, mode)
  - `routers/settings.py` - Configuration management
  - `routers/macros.py` - Macro system

### Frontend Structure
- **index.html** - Single-page application structure
- **static/css/main.css** - Complete styling system
- **static/js/app.js** - UI logic, theme, keybinds, toasts
- **static/js/main.js** - Application state and WebSocket client
- **static/js/api.js** - REST API wrapper
- **static/js/websocket.js** - WebSocket connection manager

---

## API Reference

### Base URL
```
http://localhost:8000
```

### Connection Endpoints

#### GET `/api/connection`
Get current connection status to FLDIGI.

**Response:**
```json
{
  "connected": true,
  "fldigi_name": "fldigi",
  "fldigi_version": "4.1.20"
}
```

#### POST `/api/connection/connect`
Establish connection to FLDIGI XML-RPC server.

**Response:**
```json
{
  "success": true,
  "message": "Connected to FLDIGI"
}
```

#### POST `/api/connection/disconnect`
Disconnect from FLDIGI.

**Response:**
```json
{
  "success": true,
  "message": "Disconnected from FLDIGI"
}
```

### Modem Endpoints

#### GET `/api/modem/`
Get current modem configuration.

**Response:**
```json
{
  "modem": "BPSK31",
  "carrier": 1500,
  "bandwidth": 31,
  "quality": 85.5,
  "rsid": "PSK31"
}
```

#### POST `/api/modem/set`
Change modem mode.

**Request Body:**
```json
{
  "modem": "BPSK31"
}
```

#### POST `/api/modem/carrier`
Set carrier frequency.

**Request Body:**
```json
{
  "frequency": 1500
}
```

#### GET `/api/modem/quality`
Get signal quality metrics.

**Response:**
```json
{
  "quality": 85.5
}
```

#### POST `/api/modem/txid`
Enable/disable TXID.

**Request Body:**
```json
{
  "enabled": true
}
```

### TX/RX Endpoints

#### GET `/api/txrx/status`
Get transmit/receive status.

**Response:**
```json
{
  "status": "RX",
  "ptt": false
}
```

#### POST `/api/txrx/tx`
Start transmitting.

**Response:**
```json
{
  "success": true,
  "message": "Started TX"
}
```

#### POST `/api/txrx/rx`
Switch to receive mode.

**Response:**
```json
{
  "success": true,
  "message": "Switched to RX"
}
```

#### POST `/api/txrx/tune`
Start tuning mode.

**Response:**
```json
{
  "success": true,
  "message": "Started tuning"
}
```

#### POST `/api/txrx/abort`
Abort current transmission/tuning.

**Response:**
```json
{
  "success": true,
  "message": "Aborted TX/Tune"
}
```

#### POST `/api/txrx/text/tx`
Send text for transmission.

**Request Body:**
```json
{
  "text": "CQ CQ CQ de W1ABC W1ABC W1ABC K"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Text sent"
}
```

#### POST `/api/txrx/text/tx-live`
Send text with live TX support (character-by-character).

**Request Body:**
```json
{
  "text": "Hello",
  "replace": true
}
```

#### GET `/api/txrx/text/rx`
Get received text buffer.

**Response:**
```json
{
  "text": "CQ CQ CQ de W1AW W1AW W1AW K"
}
```

#### POST `/api/txrx/text/clear-rx`
Clear received text buffer.

#### POST `/api/txrx/text/clear-tx`
Clear transmit text buffer.

### Rig Control Endpoints

#### GET `/api/rig/`
Get rig information.

**Response:**
```json
{
  "frequency": 14070000,
  "mode": "USB",
  "name": "IC-7300"
}
```

#### POST `/api/rig/frequency`
Set rig frequency.

**Request Body:**
```json
{
  "frequency": 14070000
}
```

#### POST `/api/rig/mode`
Set rig mode.

**Request Body:**
```json
{
  "mode": "USB"
}
```

### Settings Endpoints

#### GET `/api/settings/web-config`
Get web interface configuration.

**Response:**
```json
{
  "success": true,
  "config": {
    "theme": "dark",
    "hasSeenWelcome": true,
    "custom_keybinds": {...}
  }
}
```

#### POST `/api/settings/web-config`
Save web interface configuration.

**Request Body:**
```json
{
  "theme": "dark",
  "hasSeenWelcome": true,
  "custom_keybinds": {...}
}
```

### Macro Endpoints

#### GET `/api/macros/`
Get all available macros.

**Response:**
```json
{
  "macros": {
    "1": {
      "label": "CQ",
      "text": "CQ CQ CQ de <MYCALL> <MYCALL> <MYCALL> K"
    }
  }
}
```

#### POST `/api/macros/execute`
Execute a macro.

**Request Body:**
```json
{
  "macro_id": "1"
}
```

---

## WebSocket Protocol

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Message Format

**Server → Client:**
```json
{
  "type": "status_update",
  "data": {
    "modem": "BPSK31",
    "carrier": 1500,
    "txStatus": "RX",
    "signalQuality": 85.5,
    "rsid": "PSK31"
  }
}
```

```json
{
  "type": "rx_text",
  "data": {
    "text": "New received text"
  }
}
```

### Update Frequency
- Status updates: Every 500ms
- RX text updates: Every 200ms (when receiving)

---

## Configuration

### FLDIGI XML-RPC Settings

**Default Configuration:**
- Host: `127.0.0.1`
- Port: `7362`

**Enable in FLDIGI:**
1. Open FLDIGI
2. Configure → Misc → XML-RPC Server
3. Check "Enable XML-RPC server"
4. Set Address: `127.0.0.1`
5. Set Port: `7362`
6. Click "Apply" and restart FLDIGI

### Web Server Configuration

**Port Configuration** (`backend/main.py`):
```python
uvicorn.run(
    "backend.main:app",
    host="0.0.0.0",
    port=8000,  # Change port here
    reload=False,
    log_level="info"
)
```

### TUI Configuration

**Config File:** `.fldigi_tui.json`

**Example:**
```json
{
  "mycall": "W1ABC",
  "myname": "John",
  "myqth": "Massachusetts",
  "last_contacted_call": "W1AW",
  "macros": {
    "1": {
      "label": "CQ",
      "text": "CQ CQ CQ de <MYCALL> <MYCALL> <MYCALL> K"
    },
    "2": {
      "label": "Greeting",
      "text": "Hello <CALL>, thanks for the call! Name here is <MYNAME> and QTH is <MYQTH>."
    }
  }
}
```

---

## Macro System

### Placeholder Variables

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `<MYCALL>` | Your callsign | W1ABC |
| `<MYNAME>` | Your name | John |
| `<MYQTH>` | Your location | Massachusetts |
| `<CALL>` | Last contacted station | W1AW |
| `<DATE>` | Current date | 2025-01-15 |
| `<TIME>` | Local time | 14:30 |
| `<UTC>` | UTC time | 19:30 |

### Default Macros

1. **CQ** - Calling CQ
2. **Greeting** - Reply with name/QTH
3. **73** - Sign-off
4. **QSL** - Confirm reception
5. **Signal Report** - Send RST report

### Custom Macros

**Web Interface:**
- Settings → Macros → Add/Edit

**TUI:**
- Edit `.fldigi_tui.json`
- Add under `"macros"` section

**Example:**
```json
"10": {
  "label": "Contest",
  "text": "<CALL> 5NN <MYQTH> <MYCALL>"
}
```

---

## Keybind System

### Default Keybinds (Web Interface)

| Action | Default Shortcut | Description |
|--------|-----------------|-------------|
| Connect | `Ctrl+Shift+C` | Connect to FLDIGI |
| Start TX | `Ctrl+T` | Start transmitting |
| Stop TX | `Ctrl+R` | Switch to receive |
| Clear RX | `Ctrl+Shift+X` | Clear RX buffer |
| Clear TX | `Ctrl+Shift+Z` | Clear TX buffer |
| Save RX | `Ctrl+S` | Save RX to file |

### Custom Keybinds

**Setup:**
1. Click Settings icon (⚙️)
2. Navigate to "Keybinds" tab
3. Click keybind to rebind
4. Press new key combination
5. Click "Save All Keybinds"

**Macro Shortcuts:**
1. Click "Add Macro Shortcut"
2. Select macro
3. Press key combination
4. Click "Save"

---

## Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/your-repo/digishell.git
cd digishell

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend (with auto-reload)
python -m backend.main

# Or start TUI
python run_tui.py
```

### Project Dependencies

**Python Packages:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pyfldigi` - FLDIGI XML-RPC client
- `python-multipart` - File upload support
- `prompt_toolkit` - TUI library

### Adding New API Endpoints

1. Create route handler in appropriate router file
2. Add endpoint to router
3. Update `backend/main.py` to include router
4. Test with API docs at `http://localhost:8000/docs`

**Example:**
```python
# backend/routers/custom.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/custom", tags=["custom"])

@router.get("/test")
async def test_endpoint():
    return {"message": "Test successful"}
```

### Frontend Development

**File Structure:**
- Edit HTML: `frontend/index.html`
- Edit CSS: `frontend/static/css/main.css`
- Edit JS: `frontend/static/js/app.js`, `main.js`, `api.js`, `websocket.js`

**Testing:**
1. Make changes to files
2. Refresh browser (no build step required)
3. Check browser console for errors

---

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to FLDIGI
**Solutions:**
1. Verify FLDIGI is running
2. Enable XML-RPC in FLDIGI settings
3. Check port 7362 is not blocked by firewall
4. Verify no other application is using port 7362
5. Try restarting FLDIGI

**Problem:** WebSocket connection fails
**Solutions:**
1. Check backend server is running
2. Verify port 8000 is accessible
3. Check browser console for specific errors
4. Try different browser
5. Disable browser extensions that might block WebSockets

### TX/RX Issues

**Problem:** Text not transmitting
**Solutions:**
1. Verify FLDIGI is in TX mode
2. Check FLDIGI TX buffer is not full
3. Ensure audio device is configured in FLDIGI
4. Verify rig control is working
5. Check for FLDIGI errors in main window

**Problem:** No received text appearing
**Solutions:**
1. Check FLDIGI is receiving signals
2. Verify correct modem mode selected
3. Adjust carrier frequency
4. Check audio input levels in FLDIGI
5. Enable AFC (Automatic Frequency Control)

### Performance Issues

**Problem:** Slow/laggy interface
**Solutions:**
1. Clear RX buffer regularly
2. Close unnecessary browser tabs
3. Disable browser extensions
4. Reduce WebSocket update frequency (in code)
5. Check system resource usage

**Problem:** High CPU usage
**Solutions:**
1. Reduce polling frequency in TUI
2. Use Web interface instead of TUI for lower overhead
3. Check FLDIGI CPU usage
4. Close other applications

### TUI Issues

**Problem:** Display corruption or artifacts
**Solutions:**
1. Resize terminal window
2. Ensure terminal supports 256 colors
3. Use a modern terminal emulator
4. Check terminal TERM environment variable

**Problem:** Keys not working
**Solutions:**
1. Check terminal key bindings
2. Try different terminal emulator
3. Disable conflicting keyboard shortcuts
4. Check system language/keyboard settings

---

## Advanced Topics

### Live TX Editing

The system supports FLDIGI-style live TX editing where text appears as you type.

**How it works:**
1. System detects when TX mode starts
2. Monitors textarea for changes
3. Sends only new characters to FLDIGI
4. Tracks what's been transmitted
5. Supports backspace/editing

**Configuration:**
- Enabled by default in web interface
- Automatically activates when TX starts
- Can be toggled via checkbox

### Production Deployment

**Using Gunicorn:**
```bash
pip install gunicorn
gunicorn backend.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**Using systemd:**
```ini
[Unit]
Description=DigiShell Web Interface
After=network.target

[Service]
Type=notify
User=radio
WorkingDirectory=/home/radio/digishell
ExecStart=/home/radio/digishell/venv/bin/gunicorn backend.main:app \
  -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Security Considerations

**For Local Use:**
- Default configuration binds to `0.0.0.0` (all interfaces)
- No authentication required
- Suitable for trusted local networks

**For Remote Access:**
- Add authentication middleware
- Use reverse proxy (nginx, Apache)
- Enable HTTPS with SSL certificates
- Restrict CORS origins
- Implement rate limiting

---

## API Changelog

### v1.0
- Initial release
- Basic modem, TX/RX, rig control
- WebSocket status updates
- Macro system

### v1.1
- Added live TX editing support
- Web config persistence
- Custom keybind system
- Toast notifications
- Save RX buffer to file

---

## License

GNU General Public License v3.0 - See LICENSE file for details.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

**73! 📡**

# DigiShell

A fun and simple interface wrapper for FLDIGI. Works in your browser or terminal. This is a work in progress project and it is possibly unstable and has bugs and other issues.

**Website:** [digishell.kc3vpb.com](https://digishell.kc3vpb.com) 

![Image](https://iili.io/KygYH5x.png)

**This isn't meant to replace FLDIGI at all**, it's just a wrapper around FLDIGI's XML-RPC interface that also uses a library of pyFldigi that gives you a cleaner way to control it. FLDIGI still does all the actual work with the modems and signal processing. I built this because I wanted something simpler to interact with during portable operations and field day setups, and figured it might be useful for others too.

It doesn't have all the bells and whistles that FLDIGI has, that's by design and also because of XML-RPC limitations. This is just the essentials for making contacts: modem control, TX/RX, and its own macro system. If you need FLDIGI's advanced features (waterfall, waterfall clicking, macro editing in the app, adjust config/modes, etc.), you'll still use FLDIGI directly for those.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg) ![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg) ![Claude](https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=claude&logoColor=white)

## !! DO NOT EXPOSE DIGISHELL TO THE INTERNET !!
This is not designed and has not been secured for the public web. Its purpose is for local devices, LAN, or remote operations via a secured VPN tunnel. **Do not expose the port to the web or port forward.** If you need remote operations, use Tailscale, OpenVPN, or similar services.


## Features
DigiShell only has the essentials. Built with Python so it works on most platforms

**Web Interface**
Access from any browser over a LAN or VPN (**do not expose to internet for safety reasons**). Good for remote stations or operating from a tablet/phone during field operations.

**Terminal Interface**
CLI interface for headless setups, SSH sessions, and terminal users.

**Portable Friendly**
Lightweight and responsive. Works on small computers and field setups. 

## Other Info About This Project
This is also a personal research and learning project for fun to understand how Large Language Models (LLMs) work to develop projects like this. The majority of the code was written by Claude Code (Anthropic's AI coding assistant), and then I went through it, tested everything, fixed issues, and adjusted things to work properly.

It took multiple iterations, planning it out step by step, a lot of testing, debugging weird issues, figuring out what worked and what didn't, and learning how to communicate what I wanted to an LLM. 


## What it actually does

**Web Interface**
- Works on desktop, tablet, or phone (responsive design)
- Real-time updates via WebSocket
- Custom keyboard shortcuts
- Macro system with auto-fill (callsigns, QTH, date/time, etc.)
- Save your RX buffer to a file
- Works completely offline 

**Terminal Interface (TUI)**
- Full-screen terminal UI
- Chat-style RX/TX display
- Slash commands for quick actions
- Same macro system as the web version
- Works over SSH
  
**Macro System** 
- Pre-made macros for common stuff (CQ, greetings, 73, signal reports)
- Create your own custom macros
- Auto-fill your callsign, name, QTH, date/time, and the station you're working

## You'll need

1. **FLDIGI** installed with XML-RPC enabled (it should be by default)

2. **Python 3.10 or newer**

## Quick Start

### Windows (easiest way)

1. Make sure FLDIGI is running with XML-RPC enabled
2. Double-click `DigiShell.bat`
3. First time it'll set up the virtual environment and install everything (takes a couple minutes)
4. After that, it'll just start right up and you can use the IP's it gives to go to the interface. 

### Linux (Shell Script)
Run `./digishell.sh` - should work but hasn't been fully tested yet. 


### Manual way (all platforms)

```bash
# Get the code
git clone https://github.com/Caleb-J773/DigiShell/
cd digishell

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install stuff
pip install -r requirements.txt

# make sure FlDigi is running before starting either the web or terminal versions

# Start the web interface 
python -m backend.main

# OR start the terminal version
python run_tui.py
```

## Using it

### Web Interface

1. Make sure FLDIGI is running with XML-RPC enabled
2. Start DigiShell: `python -m backend.main`
3. Open browser to `http://localhost:8000`
4. Pick your modem mode, adjust the carrier frequency if needed
5. Type in the TX box and hit Send to transmit. While transmitting, you can add more text but can only backspace from the end.

**Keyboard shortcuts:**
- You can rebind anything or create shortcuts for macros
- Settings icon → Keybinds
- Example: Set `Ctrl+Alt+1` to send your CQ macro
- Click the save icon next to the RX buffer

You can also manually edit the `.fldigi_tui.json` to add your own custom macros. The configuration file is saved in your user folder (e.g., C:/Users/YourUsername on Windows)

#### Some issues and problems with it to work on
- Currently right now, it doesn't actively track the transmitted characters unlike FlDigi. I'm not too experienced to figure this issue out and my attempts to resolve it have resulted in various issues with the transmit buffer being cleared. I'm unsure if this is an API issue or something with the library
-  You can't edit lines in between other lines. FlDigi does let you do this, but I hadn't been able to find a way to do this.

### Project Structure

```
digishell/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── fldigi_client.py     # FLDIGI XML-RPC wrapper
│   ├── websocket_manager.py # WebSocket handler
│   ├── models.py            # Data models
│   └── routers/             # API endpoints
│       ├── macros.py        # Macro management
│       ├── modem.py         # Modem control
│       ├── rig.py           # Rig operations
│       ├── settings.py      # Settings management
│       └── txrx.py          # TX/RX operations
├── frontend/
│   ├── index.html           # Main interface
│   └── static/
│       ├── css/
│       │   └── main.css     # Styling
│       ├── js/
│       │   ├── api.js       # API client
│       │   ├── app.js       # Main app logic
│       │   ├── main.js      # Initialization
│       │   └── websocket.js # WebSocket handler
│       ├── fontawesome/     # Font Awesome CSS
│       └── webfonts/        # Font Awesome fonts (self-hosted)
├── run_tui.py               # Terminal interface
├── run_backend.py           # Backend runner
├── launcher.py              # Unified launcher
├── DigiShell.bat            # Windows launcher
├── BUILD.md                 # Build instructions
├── DOCUMENTATION.md         # Additional documentation
└── requirements.txt         # Python dependencies
```

### Built with

**Backend:**
- FastAPI - Modern async Python framework
- pyFldigi - FLDIGI XML-RPC client
- Uvicorn - ASGI server

**Frontend:**
- Vanilla JavaScript (no frameworks, keeps it simple)
- Custom CSS
- Font Awesome (self-hosted)

**Terminal:**
- prompt_toolkit - terminal UI library

## Troubleshooting

### Port 8000 Already in Use

If you see an error like:
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000):
only one usage of each socket address (protocol/network address/port) is normally permitted
```

This means another application is already using port 8000. To fix this:

1. **Find what's using the port:**
   - Windows: `netstat -ano | findstr :8000`
   - Linux/Mac: `lsof -i :8000` or `netstat -tulpn | grep :8000`

2. **Close the other application** using port 8000, or

3. **Change DigiShell's port** (see "Changing the Port" below)

### Changing the Port

You can set a custom port with the `DIGISHELL_PORT` environment variable:

**Windows (Command Prompt):**
```cmd
set DIGISHELL_PORT=8080
python -m backend.main
```

**Windows (PowerShell):**
```powershell
$env:DIGISHELL_PORT=8080
python -m backend.main
```

**Linux/Mac:**
```bash
export DIGISHELL_PORT=8080
python -m backend.main
```

Then access DigiShell at `http://localhost:8080` (or whatever port you chose).

### FlDigi Connection Issues

If you see errors like:
```
ERROR - Error getting RX text: HTTPConnectionPool(host='127.0.0.1', port=7362):
Max retries exceeded... Failed to establish a new connection
```

**Possible causes:**
1. **FlDigi is not running** - Start FlDigi before starting DigiShell
2. **XML-RPC is disabled** - In FlDigi: Configure → Misc → XML-RPC Server, make sure "Enable XML-RPC server" is checked
3. **FlDigi crashed** - Restart FlDigi and use the reconnect option (web: Connect button, TUI: `/reconnect` command)

### Can't Connect on Web Interface

1. **Check the URL** - Make sure you're using `http://localhost:8000` (or the correct port if you changed it)
2. **Check firewall** - Your firewall might be blocking the connection
3. **Wrong network interface** - If accessing from another device on your LAN, use your computer's IP address instead of `localhost`
## Want to contribute?

Feel free to open issues or submit pull requests. I'm happy to look at improvements or bug fixes.


---

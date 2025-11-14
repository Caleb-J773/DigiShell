# DigiShell

A fun and simple interface wrapper for FLDIGI. Works in your browser or terminal. This is a work in progress project and it is possibly unstable and has bugs and other issues.
![Image](https://iili.io/KygYH5x.png)

**This isn't meant to replace FLDIGI at all**, it's just a wrapper around FLDIGI's XML-RPC interface that also uses a library of pyFldigi that gives you a cleaner way to control it. FLDIGI still does all the actual work with the modems and signal processing. I built this because I wanted something simpler to interact with during portable operations and field day setups, and figured it might be useful for others too.

It doesn't have all the bells and whistles that FLDIGI has, that's by design and also because of XML-RPC limitations. This is just the essentials for making contacts: modem control, TX/RX, and it's own macro system. If you need FLDIGI's advanced features (waterfall,  waterfall clicking, macro editing in the app, adjust config/ modes, etc.), you'll still use FLDIGI directly for those.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg) ![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg) ![Claude](https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=claude&logoColor=white)

## ⚠️ IMPORTANT SECURITY WARNING ⚠️

**NEVER expose DigiShell directly to the public internet!**

This application is designed for **LOCAL USE ONLY** or access over a **TRUSTED LOCAL NETWORK (LAN)** or **VPN connection**.

**Why this matters:**
- DigiShell has **NO authentication or security features**
- It provides direct control over your radio equipment and FLDIGI
- Exposing it to the internet allows **anyone** to control your station
- It could be abused for unauthorized transmissions or malicious activity

**Safe usage:**
- ✅ Local machine only (localhost)
- ✅ Trusted LAN (home/shack network)
- ✅ VPN connection to your network
- ❌ **NEVER** port forward to the internet
- ❌ **NEVER** expose on public WiFi
- ❌ **NEVER** run on a public-facing server

If you need remote access, use a VPN solution like WireGuard, OpenVPN, or Tailscale to securely connect to your home network first.

## Some notable features that is being work on.

**Web Interface**  
Access from any browser over a LAN or VPN (**do not expose to internet for safety reasons**), which could be good for remote stations or operating from a tablet, phone/small screen during field operations. No need to be at your main shack computer.

**Terminal Ready**  
CLI interface for headless setups, SSH sessions, and if you just prefer working in the terminal. 

**Simplified Controls**  
Only the essentials. No confusing menus or hidden settings buried somewhere. Just the controls you actually need for making contacts.

**Python Powered**  
Built with Python so it works pretty much anywhere and you can customize it if you want.

**Portable Friendly**  
Lightweight and responsive. Works great on small computers, (testing Raspberry Pi's though atm), and field operations 

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

**Modem Control**
- Switch between digital modes (PSK, RTTY, Olivia, etc.)
- Adjust carrier frequency with a slider

**Macro System** 
- Pre-made macros for common stuff (CQ, greetings, 73, signal reports)
- Create your own custom macros
- Auto-fill your callsign, name, QTH, date/time, and the station you're working

## You'll need

1. **FLDIGI** installed with XML-RPC enabled (it should by default)

2. **Python 3.10 or newer**

That's it. Pretty straightforward.

## Quick Start

### Windows (easiest way)

1. Make sure FLDIGI is running with XML-RPC enabled
2. Double-click `DigiShell.bat`
3. First time it'll set up the virtual environment and install everything (takes a couple minutes)
4. Choose option **[1] Web Interface** when prompted
5. When asked to customize settings, choose **[N] No** to use defaults (recommended for most users)
6. Open your browser and go to `http://localhost:8000`
7. Click the **Connect** button and you're ready to operate!

**Note:** The default settings (`0.0.0.0:8000`) work for **everyone** - local use, LAN access, and VPN connections. You only need to customize if port 8000 is already in use or you want extra security.

### Linux/Mac (easiest way)

1. Make sure FLDIGI is running with XML-RPC enabled
2. Open terminal in the DigiShell folder
3. Run: `chmod +x digishell.sh` (first time only, makes it executable)
4. Run: `./digishell.sh`
5. First time it'll set up the virtual environment and install everything (takes a couple minutes)
6. Choose option **[1] Web Interface** when prompted
7. When asked to customize settings, type **N** and press Enter to use defaults (recommended for most users)
8. Open your browser and go to `http://localhost:8000`
9. Click the **Connect** button and you're ready to operate!

**Note:** The default settings (`0.0.0.0:8000`) work for **everyone** - local use, LAN access, and VPN connections. You only need to customize if port 8000 is already in use or you want extra security.

**Accessing from other devices on your LAN:**
When DigiShell starts, it will show you the network addresses you can use. Look for the "Network:" line in the startup message - that's the address to use from other devices on your network!

Example startup message:
```
Access URLs:
  Local:    http://localhost:8000
  Network:  http://192.168.1.100:8000
```

Use the "Network" address (`http://192.168.1.100:8000` in this example) from your tablet, phone, or other computer on the same network.

### Manual way (all platforms - if you're comfortable with command line)

```bash
# Get the code
git clone https://github.com/your-repo/digishell.git
cd digishell

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install stuff
pip install -r requirements.txt

# Start the web interface
python -m backend.main

# OR start the terminal version
python run_tui.py
```

## Server Configuration (Advanced - Optional)

**Most users can skip this section!** The defaults work fine for typical use.

Only customize these settings if you:
- Need to use a different port (e.g., 8000 is already in use)
- Want localhost-only access for extra security
- Have specific networking requirements

### Method 1: Interactive (Easiest)

When running `DigiShell.bat` (Windows) or `digishell.sh` (Linux/Mac), you'll be asked if you want to customize:
- **Bind Address**:
  - `0.0.0.0` = Access from this computer AND other devices on your LAN/VPN (default, works for everyone)
  - `127.0.0.1` = ONLY accessible from this computer (extra security, no LAN access)
- **Port**: Default is 8000, but you can use any available port (1024-65535)

**Most users should choose No** - the defaults support local, LAN, and VPN access!

### Method 2: Environment Variables (Advanced)

Set these environment variables before starting DigiShell:

**Windows (Command Prompt):**
```cmd
set DIGISHELL_HOST=127.0.0.1
set DIGISHELL_PORT=8080
python -m backend.main
```

**Windows (PowerShell):**
```powershell
$env:DIGISHELL_HOST="127.0.0.1"
$env:DIGISHELL_PORT="8080"
python -m backend.main
```

**Linux/Mac:**
```bash
export DIGISHELL_HOST=127.0.0.1
export DIGISHELL_PORT=8080
python -m backend.main
```

### Method 3: Configuration File

1. Copy the example config: `cp .env.example .env` (or `copy .env.example .env` on Windows)
2. Edit `.env` and set your preferences:
   ```
   DIGISHELL_HOST=127.0.0.1
   DIGISHELL_PORT=8080
   ```
3. Run DigiShell normally - it will automatically load these settings

**Bind Address Options:**
- `127.0.0.1` - Localhost only (most secure, only accessible from the same machine)
- `0.0.0.0` - All interfaces (allows LAN access from other devices on your network)
- Specific IP - Bind to a specific network interface

## Using it

### Web Interface

1. Make sure FLDIGI is running with XML-RPC enabled
2. Start DigiShell: `python -m backend.main`
3. Open browser to `http://localhost:8000`
4. Pick your modem mode, adjust the carrier frequency if needed
5. Type in the TX box and hit the TX button to transmit, while it is transmitting, you can also type to add more to the TX buffer, though due to current limits, this will not allow you to edit / remove text in between, you can only backspace.

**Keyboard shortcuts:**
- You can rebind anything or create shortcuts for macros
- Settings icon → Keybinds
- Example: Set `Ctrl+Alt+1` to send your CQ macro

**Saving RX buffer:**
- Click the save icon next to the RX buffer
- Downloads a timestamped text file

### Terminal Interface (TUI)

```bash
python run_tui.py
```

**First time setup:**
```
/config W1ABC John Pennsylvania
```
(use your actual callsign, name, and QTH obviously)

**Common commands:**
- Just type and hit Enter to transmit
- `/m BPSK31` - Change modem
- `/modes` - List available modes
- `/carrier 1500` - Set carrier frequency  
- `/call W1AW` - Set the station you're working
- `/macro 1` - Send macro #1 (CQ)
- `/save` - Save RX buffer
- `/clear` - Clear RX buffer
- `/quit` - Exit

**Macro placeholders you can use:**
- `<MYCALL>` - Your callsign
- `<MYNAME>` - Your name  
- `<MYQTH>` - Your location
- `<CALL>` - Station you're working
- `<DATE>` - Current date
- `<TIME>` - Local time
- `<UTC>` - UTC time

You can also manually edit the `.fldigi_tui.json` to add your own custom macros. The configuration file is saved in your user folder (e.g., C:/Users/YourUsername on Windows)

## Project Structure

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
├── digishell.sh             # Unix/Linux launcher
├── DigiShell.spec           # PyInstaller build spec
├── BUILD.md                 # Build instructions
├── DOCUMENTATION.md         # Additional documentation
└── requirements.txt         # Python dependencies
```

## Built with

**Backend:**
- FastAPI - Modern async Python framework
- pyFldigi - FLDIGI XML-RPC client
- Uvicorn - ASGI server

**Frontend:**
- Vanilla JavaScript (no frameworks, keeps it simple)
- Custom CSS
- Font Awesome (self-hosted)

**Terminal:**
- prompt_toolkit - Professional terminal UI library

## Common Issues

**Can't connect to FLDIGI:**
1. Make sure FLDIGI is actually running
2. Check that XML-RPC is enabled in FLDIGI settings
3. Verify port 7362 isn't being blocked
4. Check your firewall if you're still having issues

**Web interface not updating:**
1. Check browser console (F12) for errors
2. Make sure the WebSocket is connected
3. Verify FLDIGI is responding

**TUI looks weird:**
1. Your terminal might not support colors - try a different terminal
2. Try resizing the window
3. Make sure you're using Python 3.10 or newer

## Want to contribute?

Feel free to open issues or submit pull requests. I'm happy to look at improvements or bug fixes.

---
Built as a fun project to make portable digital operations simpler. It's not meant to replace FLDIGI, just make it easier to control when you're in the field or accessing your station remotely.

- Caleb KC3VPB

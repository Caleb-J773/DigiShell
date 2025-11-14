# DigiShell

A fun and simple interface wrapper for FLDIGI. Works in your browser or terminal. This is a work in progress project and it is possibly unstable and has bugs and other issues.
![Image](https://iili.io/KygYH5x.png)

**This isn't meant to replace FLDIGI at all**, it's just a wrapper around FLDIGI's XML-RPC interface that also uses a library of pyFldigi that gives you a cleaner way to control it. FLDIGI still does all the actual work with the modems and signal processing. I built this because I wanted something simpler to interact with during portable operations and field day setups, and figured it might be useful for others too.

It doesn't have all the bells and whistles that FLDIGI has, that's by design and also because of XML-RPC limitations. This is just the essentials for making contacts: modem control, TX/RX, and it's own macro system. If you need FLDIGI's advanced features (waterfall,  waterfall clicking, macro editing in the app, adjust config/ modes, etc.), you'll still use FLDIGI directly for those.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg) ![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg) ![Claude](https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=claude&logoColor=white)

## !! DO NOT EXPOSE DIGISHELL TO THE INTERNET !!
This is not designed and has not been secured for the public web. It's purpose is not to be that way either. It's meant for local devices, a LAN or when it comes to remote operations, via secured VPN tunnel. **Do not expose the port to the web and or port forward.** If you need remote operations, use tailscale, OpenVPN or other services.


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
2. Double-click `start.bat`
3. First time it'll set up the virtual environment and install everything (takes a couple minutes)
4. After that, it'll just start right up and you can use the IP's it gives to go to the interface. 

### Linux (Shell Script)
This might work, but I hadn't had the chance just yet to test it, but you can test out the digishell.sh that is included. 


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
- prompt_toolkit - terminal UI library

## Common Issues

**Can't connect to FLDIGI:**
1. Make sure FLDIGI is actually running
2. Check that XML-RPC is enabled in FLDIGI settings
3. Verify port 7362 isn't being blocked
4. Check your firewall if you're still having issues

5. 
**TUI looks weird:**
1. Your terminal might not support colors - try a different terminal
2. Try resizing the window
3. Make sure you're using Python 3.10 or newer

## Want to contribute?

Feel free to open issues or submit pull requests. I'm happy to look at improvements or bug fixes.

---
Built as a fun project to make portable digital operations simpler. It's not meant to replace FLDIGI, just make it easier to control when you're in the field or accessing your station remotely.

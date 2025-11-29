<div align="center">

# DigiShell

**A simple interface wrapper for FLDIGI**

Browser-based and terminal-friendly

[digishell.kc3vpb.com](https://digishell.kc3vpb.com)

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)
![Claude](https://img.shields.io/badge/Claude-D97757?logo=claude&logoColor=white)

</div>

---

![DigiShell Interface](https://iili.io/KygYH5x.png)

## What is this?

DigiShell wraps around FLDIGI's XML-RPC interface using the pyFldigi library to give you a cleaner way to control it. FLDIGI still does all the actual work with the modems and signal processing.

I built this because I wanted something simpler to interact with during portable operations and field day setups, and figured it might be useful for others too.

**This isn't meant to replace FLDIGI at all.** It doesn't have all the bells and whistles, and that's by design. This is just the essentials for making contacts: modem control, TX/RX, and its own macro system. If you need FLDIGI's advanced features (waterfall clicking, macro editing in the app, config adjustments, etc.), you'll still use FLDIGI directly for those.

> **Note:** This is a work in progress. It's possibly unstable and has bugs and other issues.

---

## Security Warning

**Do not expose DigiShell to the internet.**

This has not been secured for the public web. It's designed for local devices, LAN, or remote operations via a secured VPN tunnel. Don't expose the port to the web or port forward it. If you need remote access, use Tailscale, OpenVPN, or similar services.

---

## Features

Digishell has two different ways that you can interact with, the first way is via the **web interface**. The web version is a more styled, more customizable and feature rich. It can be accessed from any browser over a LAN or VPN. While building the web interface, I also took into account the need for remote stations and or in general operating away from the computer hooked up to FlDigi. It works pretty well for remote stations or operating from a tablet/phone during field operations. The web interface will work on a desktop, tablet, or phone via a mobile layout.

Some notable features with the web interface include themes (dark mode + light mode, and varying colors) with being able to custom set your own, a full macro system, many different layouts you can choose from for your screen/operating preferences and also you are able to freely adjust the size of the TX and RX windows.

The second way is via it's **terminal interface** otherwise known as a (TUI) terminal user interface. The terminal interface is great for SSH sessions, smaller screens and or in general just users who would like a terminal interface. The terminal interface doesn't have all the features like the web interface.

![DigiShell Terminal](https://digishell.kc3vpb.com/shell1.png)

---

## Requirements

1. **FLDIGI** installed with XML-RPC enabled (should be on by default)
2. **Python 3.10 or newer**

---

## Quick Start

### Windows

1. Make sure FLDIGI is running with XML-RPC enabled
2. Double-click `DigiShell.bat`
3. First time it'll set up the virtual environment and install everything (takes a couple minutes)
4. After that, it'll just start right up and you can use the IPs it gives to access the interface

### Linux

Run `./digishell.sh` - should work but hasn't been fully tested yet.

### Manual Installation

```bash
# Get the code
git clone https://github.com/Caleb-J773/DigiShell/
cd digishell

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make sure FLDIGI is running before starting

# Start the web interface
python -m backend.main

# OR start the terminal version
python run_tui.py
```

---

## Usage

### Web Interface

1. Make sure FLDIGI is running with XML-RPC enabled
2. Start DigiShell: `python -m backend.main`
3. Open browser to `http://localhost:8000`
4. Pick your modem mode, adjust the carrier frequency if needed
5. Type in the TX box and hit Send to transmit

While transmitting, you can add more text but can only backspace from the end.

**Keyboard Shortcuts:** You can rebind anything or create shortcuts for macros. Go to Settings → Keybinds. For example, set `Ctrl+Alt+1` to send your CQ macro.

You can also manually edit `.fldigi_tui.json` in your user folder to add custom macros.

---

## Known Issues

- Currently doesn't actively track transmitted characters unlike FLDIGI. My attempts to fix this have caused issues with the transmit buffer being cleared. Not sure if this is an API issue or something with the library.
- You can't edit lines in between other lines. FLDIGI lets you do this, but I haven't found a way to implement it yet.

---

## Built With

| Backend | Frontend | Terminal |
|---------|----------|----------|
| FastAPI | Vanilla JavaScript | prompt_toolkit |
| pyFldigi | Custom CSS | |
| Uvicorn | Font Awesome (self-hosted) | |

---

## Troubleshooting

### Port 8000 Already in Use

If you see an error about the port being in use, find what's using it:

```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

Then either close that application or change DigiShell's port.

### Changing the Port

Set a custom port with the `DIGISHELL_PORT` environment variable:

```bash
# Windows (Command Prompt)
set DIGISHELL_PORT=8080
python -m backend.main

# Windows (PowerShell)
$env:DIGISHELL_PORT=8080
python -m backend.main

# Linux/Mac
export DIGISHELL_PORT=8080
python -m backend.main
```

Then access DigiShell at `http://localhost:8080`.

---
## AI-Generated Codebase Disclaimer

The majority of the code in this project was generated using Claude Code, Anthropic's LLM and also local Large Lanaguge Models. Some of the local model consisted of Qwen etc. Overall this means that the initial code structure, logic, and implementation were produced by an LLM based on my instructions, planning and requirements.
Which then I reviewed, tested, debugged, and modified the LLM-generated code to ensure it works correctly.

It took multiple iterations, planning it out step by step, a lot of testing, debugging weird issues, figuring out what worked and what didn't, and learning how to communicate what I wanted to an LLM. This is also a personal research and learning project to understand how Large Language Models work for development.

This project has taken dozen of hours to create. It is not a "one shot" prompt. 


---

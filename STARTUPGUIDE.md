# FLDIGI Layer - Startup Guide

Complete step-by-step guide to get FLDIGI Layer up and running.

## Quick Start Options

Choose your preferred method:
- **[Windows Quick Start](#windows-quick-start)** - Double-click and go (recommended for Windows)
- **[Manual Setup](#manual-setup)** - Step-by-step installation for any platform
- **[TUI Interface](#tui-terminal-interface)** - Terminal-based interface

---

## Windows Quick Start

### Prerequisites
1. **FLDIGI** installed and configured
2. **Python 3.8+** installed with PATH enabled

### Steps

1. **Start FLDIGI**
   - Launch FLDIGI application
   - Configure → Misc → XML-RPC Server
   - Enable XML-RPC server
   - Verify port is `7362`
   - Click Apply

2. **Run start.bat**
   - Navigate to `fldigi-layer` folder
   - Double-click `start.bat`
   - First run will:
     - Create virtual environment
     - Install all dependencies (takes 2-3 minutes)
     - Start the web server
   - Subsequent runs start immediately

3. **Open Browser**
   - Browser should open automatically to `http://localhost:8000`
   - If not, manually navigate to `http://localhost:8000`

4. **Connect**
   - Click the **Connect** button in top-right
   - Status should change to "Connected"
   - You're ready to operate!

**That's it!** 🎉

---

## Manual Setup

### Step 1: Install FLDIGI

**Windows:**
1. Download from http://www.w1hkj.com/
2. Run installer
3. Launch FLDIGI
4. Complete initial setup wizard

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install fldigi

# Fedora
sudo dnf install fldigi

# Arch
sudo pacman -S fldigi
```

**macOS:**
```bash
brew install fldigi
```

### Step 2: Configure FLDIGI XML-RPC

1. Open FLDIGI
2. Menu: **Configure → Misc → XML-RPC Server**
3. Settings:
   - ☑ Enable XML-RPC server
   - Address: `127.0.0.1`
   - Port: `7362`
4. Click **Apply**
5. Restart FLDIGI

**Verify XML-RPC:**
- You should see "xmlrpc server" in FLDIGI status bar
- Port 7362 should be listening

### Step 3: Install Python

**Check if Python is installed:**
```bash
python --version
```

**If not installed:**

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ⚠️ **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"

**Linux:**
```bash
# Usually pre-installed, if not:
sudo apt-get install python3 python3-venv  # Ubuntu/Debian
sudo dnf install python3                    # Fedora
```

**macOS:**
```bash
brew install python3
```

### Step 4: Download FLDIGI Layer

**Option A: Download ZIP**
1. Go to GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract to desired location

**Option B: Git Clone**
```bash
git clone https://github.com/yourusername/fldigi-layer.git
cd fldigi-layer
```

### Step 5: Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (web server)
- pyFldigi (FLDIGI client)
- prompt_toolkit (TUI support)

**Installation takes 2-3 minutes.**

### Step 7: Start the Server

```bash
python -m backend.main
```

You should see:
```
============================================================
🚀 Starting FLDIGI Backend API Server
============================================================
📡 API will be available at: http://localhost:8000
🔌 WebSocket will be available at: ws://localhost:8000/ws
📚 API docs at: http://localhost:8000/docs
============================================================
```

### Step 8: Open Web Interface

Open browser to: **http://localhost:8000**

### Step 9: Connect to FLDIGI

1. Click **Connect** button (top-right)
2. Wait for status to change to "Connected"
3. You should see current modem mode and carrier frequency

**Success!** You're ready to operate.

---

## TUI (Terminal Interface)

### Starting TUI

**Windows:**
```cmd
venv\Scripts\activate
python run_tui.py
```

**Linux/macOS:**
```bash
source venv/bin/activate
python run_tui.py
```

### First-Time TUI Setup

**Configure Your Station:**
```
/config W1ABC John Massachusetts
```
Replace with:
- Your callsign
- Your name
- Your QTH (location)

**Configuration is saved to `.fldigi_tui.json`**

### Basic TUI Usage

**Send a Message:**
1. Type your message
2. Press Enter
3. Text is transmitted immediately

**Change Modem:**
```
/m BPSK31
```

**See Available Modes:**
```
/modes
```

**Set Carrier Frequency:**
```
/carrier 1500
```

**Set Last Contacted Station:**
```
/call W1AW
```

**Send a Macro:**
```
/macro 1
```

**Save RX Buffer:**
```
/save
```

**Clear RX Buffer:**
```
/clear
```

**Exit:**
```
/quit
```

### TUI Keyboard Shortcuts

- **Ctrl+C** - Force quit
- **Up/Down Arrows** - Command history
- **Page Up/Down** - Scroll RX buffer
- **Enter** - Send message/command

---

## First Operation

### Web Interface

1. **Select Modem Mode**
   - Click modem dropdown (e.g., "BPSK31")
   - Choose desired mode
   - Click "Set Mode"

2. **Adjust Carrier**
   - Use slider to set carrier frequency
   - Typical: 1000-2000 Hz
   - Match waterfall signal

3. **Send CQ**
   - Type in TX textarea:
     ```
     CQ CQ CQ de W1ABC W1ABC W1ABC K
     ```
   - Click **TX** button
   - Watch your text appear in FLDIGI
   - Click **RX** when done

4. **Receive**
   - Watch RX buffer for incoming text
   - Adjust carrier to match signal
   - Enable AFC for auto-tuning

5. **Use Macros**
   - Settings → Macros
   - Click macro to send instantly
   - Create custom macros

### TUI Interface

1. **Change Mode**
   ```
   /m BPSK31
   ```

2. **Set Station**
   ```
   /call W1AW
   ```

3. **Send CQ (using macro)**
   ```
   /macro 1
   ```

4. **Reply to Station**
   ```
   /macro 2
   ```

5. **Sign Off**
   ```
   /macro 3
   ```

---

## Common Issues & Solutions

### "Cannot connect to FLDIGI"

**Check:**
1. FLDIGI is running
2. XML-RPC is enabled (Configure → Misc → XML-RPC Server)
3. Port is 7362
4. No firewall blocking port 7362

**Fix:**
```bash
# Test if port is open (Linux/macOS)
telnet localhost 7362

# Test if port is open (Windows)
Test-NetConnection localhost -Port 7362
```

### "Python not found"

**Windows:**
- Reinstall Python with "Add to PATH" checked
- Restart terminal

**Linux/macOS:**
- Try `python3` instead of `python`
- Install Python from package manager

### "Permission denied" (Linux/macOS)

```bash
# Make scripts executable
chmod +x run_tui.py
```

### "Module not found"

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "Port 8000 already in use"

**Option A: Stop other service using port 8000**

**Option B: Change port in `backend/main.py`:**
```python
uvicorn.run(
    "backend.main:app",
    port=8080,  # Change to different port
    ...
)
```

### Web interface not loading

1. Check backend is running (no errors in terminal)
2. Try different browser
3. Clear browser cache
4. Check browser console for errors (F12)
5. Disable browser extensions

### No text appearing in RX buffer

1. Check FLDIGI is receiving (waterfall shows signals)
2. Verify modem mode matches signal
3. Adjust carrier frequency to match signal
4. Enable squelch in FLDIGI
5. Check FLDIGI RX buffer has text

### TUI display corrupted

1. Resize terminal window
2. Type `/clear` to reset display
3. Use different terminal emulator
4. Ensure terminal is at least 80x24 characters

---

## Advanced Configuration

### Custom FLDIGI Port

If FLDIGI uses different port:

**Edit `backend/fldigi_client.py`:**
```python
fldigi_client = FldigiClient(host="127.0.0.1", port=7362)  # Change port
```

### Remote FLDIGI Access

To connect to FLDIGI on another computer:

**Edit `backend/fldigi_client.py`:**
```python
fldigi_client = FldigiClient(host="192.168.1.100", port=7362)  # Remote IP
```

**Enable in FLDIGI:**
- Configure → Misc → XML-RPC Server
- Set Address: `0.0.0.0` (listen on all interfaces)
- ⚠️ Only on trusted networks!

### Custom Macros

**Web Interface:**
1. Settings → Macros
2. Click "Add Macro"
3. Enter label and text
4. Use placeholders: `<MYCALL>`, `<MYNAME>`, etc.
5. Save

**TUI:**
Edit `.fldigi_tui.json`:
```json
{
  "macros": {
    "10": {
      "label": "My Custom Macro",
      "text": "Hello <CALL> de <MYCALL>"
    }
  }
}
```

### Auto-Start on Boot (Linux)

**Create systemd service:**
```bash
sudo nano /etc/systemd/system/fldigi-layer.service
```

**Add:**
```ini
[Unit]
Description=FLDIGI Layer Web Interface
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/fldigi-layer
ExecStart=/home/YOUR_USERNAME/fldigi-layer/venv/bin/python -m backend.main
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable:**
```bash
sudo systemctl enable fldigi-layer
sudo systemctl start fldigi-layer
```

---

## Next Steps

### Learn More
- Read [DOCUMENTATION.md](DOCUMENTATION.md) for API reference
- Check [README.md](README.md) for feature overview
- Explore macro system with custom templates

### Customize
- Create custom macros for contests
- Set up custom keybinds
- Configure theme (dark/light)
- Adjust carrier and modem defaults

### Experiment
- Try different modem modes
- Use live TX editing
- Save RX logs for later analysis
- Integrate with logging software

---

## Getting Help

### Check These First
1. FLDIGI status bar (look for errors)
2. Terminal output (backend errors)
3. Browser console (F12) for web interface errors
4. This guide's troubleshooting section

### Report Issues
- GitHub Issues: https://github.com/yourusername/fldigi-layer/issues
- Include:
  - Operating system and version
  - Python version
  - FLDIGI version
  - Error messages
  - Steps to reproduce

---

## Glossary

**FLDIGI** - Fast Light Digital modem application for amateur radio

**XML-RPC** - Remote procedure call protocol used by FLDIGI

**Modem** - Digital mode (BPSK, RTTY, Olivia, etc.)

**Carrier** - Audio frequency of digital signal (Hz)

**TX** - Transmit mode

**RX** - Receive mode

**PTT** - Push-To-Talk (triggers transmitter)

**RSID** - Reed-Solomon ID (automatic mode detection)

**AFC** - Automatic Frequency Control (auto-tuning)

**QTH** - Location/station

**CQ** - General call to all stations

**73** - Best regards (amateur radio goodbye)

**K** - Over (invitation to transmit)

**DE** - From (in callsign context)

---

**73! 📡**

Welcome to FLDIGI Layer. Happy operating!

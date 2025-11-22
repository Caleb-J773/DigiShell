# CLAUDE.md - AI Assistant Guide for DigiShell

This document provides comprehensive guidance for AI assistants (like Claude) working on the DigiShell codebase. It explains the architecture, development workflows, code conventions, and important context needed to effectively contribute to this project.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Structure](#architecture--structure)
3. [Key Technologies](#key-technologies)
4. [Development Guidelines](#development-guidelines)
5. [Code Conventions](#code-conventions)
6. [Common Tasks & Workflows](#common-tasks--workflows)
7. [Important Files](#important-files)
8. [Testing & Debugging](#testing--debugging)
9. [Things to Avoid](#things-to-avoid)

---

## Project Overview

**DigiShell** is a web and terminal interface wrapper for FLDIGI, a popular amateur radio digital modem application. It provides a simplified, modern interface for controlling FLDIGI through its XML-RPC API.

### Core Purpose
- Provide a clean web interface for FLDIGI accessible from browsers, tablets, and phones
- Offer a terminal UI (TUI) for headless/SSH operations
- Simplify common digital mode operations (CQ calls, macros, TX/RX)
- Enable remote operation via LAN or VPN (NOT for public internet exposure)

### Key Features
- Real-time WebSocket communication for status updates
- Custom macro system with placeholder variables
- Live TX editing (character-by-character transmission)
- Configurable keyboard shortcuts
- Theme support (dark/light)
- Signal quality metrics and RST/RSQ estimates
- Preset frequency management

### Important Context
This project was primarily developed using AI assistance (Claude Code) as a learning experiment. The codebase reflects modern Python/FastAPI patterns with vanilla JavaScript on the frontend (no frameworks).

---

## Architecture & Structure

### High-Level Architecture

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

### Directory Structure

```
digishell/
├── backend/                    # FastAPI backend server
│   ├── main.py                # Main FastAPI app, WebSocket handler, startup logic
│   ├── fldigi_client.py       # FldigiClient class - XML-RPC wrapper
│   ├── websocket_manager.py   # ConnectionManager for WebSocket broadcasts
│   ├── models.py              # Pydantic models for API requests/responses
│   └── routers/               # Modular API endpoint handlers
│       ├── macros.py          # Macro management endpoints
│       ├── modem.py           # Modem control (mode, carrier, bandwidth)
│       ├── presets.py         # Frequency preset management
│       ├── rig.py             # Rig control (frequency, mode)
│       ├── settings.py        # Configuration persistence
│       └── txrx.py            # TX/RX operations, text buffers
│
├── frontend/                   # Web interface
│   ├── index.html             # Single-page app structure
│   └── static/
│       ├── css/
│       │   ├── main.css       # Main styles
│       │   └── layouts.css    # Layout system styles
│       ├── js/
│       │   ├── main.js        # Core app initialization, WebSocket client
│       │   ├── app.js         # UI controls, themes, toasts, keybinds
│       │   ├── api.js         # REST API wrapper functions
│       │   ├── websocket.js   # WebSocket connection management
│       │   ├── ui-controls.js # UI interaction handlers
│       │   ├── layouts.js     # Layout system logic
│       │   ├── presets.js     # Preset management UI
│       │   ├── themes.js      # Theme management
│       │   └── theme-ui.js    # Theme UI controls
│       ├── fontawesome/       # Self-hosted Font Awesome CSS
│       └── webfonts/          # Font Awesome font files
│
├── run_tui.py                 # Terminal UI (standalone, direct XML-RPC)
├── run_backend.py             # Backend runner helper
├── launcher.py                # Unified launcher with auto-setup
├── DigiShell.bat              # Windows batch launcher
├── digishell.sh               # Linux/Mac shell launcher
├── requirements.txt           # Python dependencies
├── README.md                  # User-facing documentation
├── DOCUMENTATION.md           # Technical API documentation
└── CLAUDE.md                  # This file - AI assistant guide
```

---

## Key Technologies

### Backend
- **FastAPI** - Modern async Python web framework
- **Uvicorn** - ASGI server for FastAPI
- **pyFldigi** - Python client library for FLDIGI XML-RPC API
- **Pydantic** - Data validation and settings management
- **WebSockets** - Real-time bidirectional communication

### Frontend
- **Vanilla JavaScript** - No frameworks (keep it simple)
- **WebSocket API** - For real-time updates
- **Fetch API** - For REST API calls
- **Font Awesome** - Self-hosted icon library
- **Custom CSS** - No CSS frameworks

### Terminal UI
- **prompt_toolkit** - Terminal UI library for Python
- **rich** - Terminal formatting and styling

### External Dependencies
- **FLDIGI** - The actual digital modem application (XML-RPC server on port 7362)

---

## Development Guidelines

### General Principles

1. **Simplicity Over Complexity**
   - Avoid over-engineering
   - Prefer straightforward solutions
   - No unnecessary abstractions
   - Vanilla JS preferred over frameworks

2. **Read Before Writing**
   - Always read existing files before modifying
   - Understand the current implementation
   - Maintain consistency with existing patterns

3. **Error Handling**
   - Handle FLDIGI disconnections gracefully
   - Provide clear error messages to users
   - Log errors appropriately (WARNING level for user-facing issues)
   - Avoid cascading error spam

4. **Connection Management**
   - The system must handle FLDIGI closing/crashing
   - Implement connection health checks
   - Provide reconnection capabilities
   - Don't spam errors when FLDIGI is disconnected

### Code Style

#### Python (Backend)
- Use type hints where appropriate
- Follow PEP 8 style guide
- Async/await for I/O operations
- Pydantic models for data validation
- Logging levels:
  - ERROR: For connection errors, critical failures
  - WARNING: For user-facing issues (FLDIGI disconnected)
  - INFO: For important state changes
  - DEBUG: For verbose debugging (not used much)

#### JavaScript (Frontend)
- Use modern ES6+ syntax
- Prefer `const` over `let`, avoid `var`
- Use async/await for promises
- Keep functions focused and small
- Comment complex logic

#### Logging
- Most logging is set to WARNING or ERROR level to reduce noise
- pyFldigi logger set to ERROR only
- Connection errors should be logged once, not repeatedly

### State Management

#### Backend State
- `FldigiClient` singleton (`fldigi_client`) maintains connection state
- Connection state tracked with `_connected` flag
- Background polling task runs continuously (100ms interval)
- Status updates broadcast via WebSocket (500ms interval)

#### Frontend State
- Application state managed in `main.js`
- WebSocket connection managed by `ConnectionManager`
- UI state updated via WebSocket messages
- Configuration persisted to server via `/api/settings/web-config`

### Connection Health Monitoring

The system implements robust connection monitoring:

```python
# backend/main.py - poll_fldigi_status()
- Polls every 100ms for RX text
- Checks connection health every 5 seconds
- Tracks consecutive failures
- After 10 consecutive failures, marks as disconnected
- Broadcasts connection status changes to all clients
```

Key patterns:
- **Health checks**: Periodic lightweight API calls to verify connection
- **Failure tracking**: Count consecutive failures before marking disconnected
- **Graceful degradation**: Stop error spam when FLDIGI closes
- **User notification**: Clear status messages via WebSocket

---

## Code Conventions

### Backend Patterns

#### Router Structure
```python
from fastapi import APIRouter, HTTPException
from backend.fldigi_client import fldigi_client
from backend.models import SomeRequest, StatusResponse

router = APIRouter(prefix="/api/something", tags=["something"])

@router.get("/")
async def get_something():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    result = fldigi_client.get_something()
    return {"success": True, "data": result}

@router.post("/action")
async def do_action(request: SomeRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.do_action(request.param)
    if success:
        return {"success": True, "message": "Action completed"}
    else:
        return {"success": False, "message": "Action failed"}
```

#### FldigiClient Method Pattern
```python
def get_something(self) -> Optional[str]:
    if not self.is_connected():
        return None
    try:
        return self.client.something.value
    except Exception as e:
        logger.debug(f"Error getting something: {e}")
        return None

def set_something(self, value: str) -> bool:
    if not self.is_connected():
        return False
    try:
        self.client.something.value = value
        logger.info(f"Set something to: {value}")
        return True
    except Exception as e:
        logger.debug(f"Error setting something: {e}")
        return False
```

#### Connection Error Detection
```python
def _is_connection_error(self, error: Exception) -> bool:
    """Check if an exception indicates a connection problem."""
    error_str = str(error).lower()
    error_type = type(error).__name__

    connection_indicators = [
        'connection', 'refused', '10054', '10061',
        'forcibly closed', 'max retries', 'failed to establish',
        'target machine actively refused'
    ]

    return any(keyword in error_str for keyword in connection_indicators) or \
           error_type in ['ConnectionError', 'ConnectionRefusedError', 'ConnectionResetError']
```

### Frontend Patterns

#### API Call Pattern
```javascript
// api.js
async function callApi(endpoint, method = 'GET', body = null) {
    const options = {
        method: method,
        headers: {'Content-Type': 'application/json'}
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(endpoint, options);
    return await response.json();
}
```

#### WebSocket Message Handling
```javascript
// main.js
ws.onMessage((message) => {
    switch(message.type) {
        case 'status_update':
            updateStatus(message.data);
            break;
        case 'text_update':
            updateText(message.data);
            break;
        case 'connection_status':
            updateConnectionStatus(message.data);
            break;
        case 'error':
            showToast(message.data.error, 'error');
            break;
    }
});
```

#### Toast Notifications
```javascript
// app.js
window.showToast('Message here', 'success'); // success, error, warning, info
```

### Configuration Files

#### User Configuration (.fldigi_tui.json)
Stored in user's home directory:
```json
{
  "mycall": "W1ABC",
  "myname": "John",
  "myqth": "Massachusetts",
  "last_contacted_call": "W1AW",
  "macros": {
    "1": {"label": "CQ", "text": "CQ CQ CQ de <MYCALL> <MYCALL> <MYCALL> K"},
    "2": {"label": "Greeting", "text": "Hello <CALL>..."}
  },
  "presets": [
    {
      "id": "preset-1",
      "name": "20m PSK31",
      "modem": "BPSK31",
      "rig_frequency": 14070000,
      "carrier_frequency": 1500,
      "band": "20m"
    }
  ]
}
```

#### Web Configuration (.fldigi_web_config.json)
Stored in user's home directory:
```json
{
  "theme": "dark",
  "hasSeenWelcome": true,
  "custom_keybinds": {
    "connectFldigi": {"key": "c", "ctrl": true, "shift": true},
    "macro_1": {"key": "1", "ctrl": true, "alt": true}
  },
  "betaFeatures": false
}
```

---

## Common Tasks & Workflows

### Adding a New API Endpoint

1. **Choose the appropriate router** (or create new one in `backend/routers/`)
2. **Add endpoint function** with proper typing
3. **Check connection state** before calling FLDIGI
4. **Return consistent response format**
5. **Add corresponding FldigiClient method** if needed
6. **Update frontend API client** in `frontend/static/js/api.js`
7. **Test via FastAPI docs** at http://localhost:8000/docs

Example:
```python
# backend/routers/modem.py
@router.post("/some-new-action")
async def new_action(request: SomeRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.perform_action(request.value)
    return {"success": success, "message": "Action completed" if success else "Action failed"}
```

### Adding a New FldigiClient Method

1. **Check pyFldigi documentation** for available XML-RPC calls
2. **Follow the method pattern** (see Code Conventions)
3. **Handle disconnection gracefully** (return None or False)
4. **Log at appropriate level** (INFO for state changes, DEBUG for errors)
5. **Add type hints** for parameters and return values

Example:
```python
# backend/fldigi_client.py
def get_new_property(self) -> Optional[int]:
    if not self.is_connected():
        return None
    try:
        return self.client.some.property
    except Exception as e:
        logger.debug(f"Error getting property: {e}")
        return None
```

### Adding Frontend Features

1. **Update HTML** in `frontend/index.html` if needed
2. **Add styles** to `frontend/static/css/main.css`
3. **Add JavaScript** to appropriate file:
   - Core logic → `main.js`
   - UI interactions → `app.js` or `ui-controls.js`
   - API calls → `api.js`
   - WebSocket → `websocket.js`
4. **Test in browser** - no build step required, just refresh

### Adding Macro Placeholders

Placeholders are replaced when macros execute. Current placeholders:

- `<MYCALL>` - User's callsign
- `<MYNAME>` - User's name
- `<MYQTH>` - User's location
- `<CALL>` - Last contacted station
- `<DATE>` - Current date (YYYY-MM-DD)
- `<TIME>` - Local time (HH:MM)
- `<UTC>` - UTC time (HH:MM)

To add new placeholders:
1. **Backend**: Update `backend/routers/macros.py` - `expand_macro_variables()`
2. **TUI**: Update `run_tui.py` - `expand_macro_placeholders()`
3. **Document** in README.md and DOCUMENTATION.md

### Modifying WebSocket Updates

Status polling happens in `backend/main.py` - `poll_fldigi_status()`:

```python
# Text updates: Every 100ms
await asyncio.sleep(0.1)

# Status updates: Every 500ms (5 iterations * 100ms)
status_poll_counter += 1
if status_poll_counter >= 5:
    status_poll_counter = 0
    # Send status update
```

Be careful changing polling frequency - too fast causes performance issues, too slow feels unresponsive.

---

## Important Files

### Backend Core Files

#### `backend/main.py`
- **Purpose**: FastAPI application entry point
- **Key Components**:
  - `poll_fldigi_status()` - Background task for status polling
  - `lifespan()` - Startup/shutdown context manager
  - WebSocket endpoint `/ws`
  - Connection management endpoints
- **Important**: Contains connection health monitoring logic

#### `backend/fldigi_client.py`
- **Purpose**: Wrapper around pyFldigi XML-RPC client
- **Key Components**:
  - `FldigiClient` class - Singleton instance
  - Connection management methods
  - All FLDIGI API operations
  - Signal metrics and RST/RSQ calculation
- **Important**: Connection state tracking with `_connected` flag

#### `backend/websocket_manager.py`
- **Purpose**: Manage WebSocket connections and broadcasts
- **Key Components**:
  - `ConnectionManager` class
  - Broadcast methods for different message types
  - Connection tracking
- **Important**: Used for real-time updates to all clients

#### `backend/models.py`
- **Purpose**: Pydantic models for data validation
- **Key Components**:
  - Request models (for API inputs)
  - Response models (for API outputs)
  - Status update models
- **Important**: Ensures type safety and validation

### Frontend Core Files

#### `frontend/index.html`
- **Purpose**: Main HTML structure
- **Key Sections**:
  - Tabs system (Main, Settings)
  - RX/TX display areas
  - Control panels
  - Modals (settings, welcome)
- **Important**: Single-page app structure

#### `frontend/static/js/main.js`
- **Purpose**: Core application logic
- **Key Components**:
  - WebSocket connection setup
  - Message routing
  - Application state management
  - Initialization
- **Important**: Entry point for JavaScript execution

#### `frontend/static/js/app.js`
- **Purpose**: UI controls and interactions
- **Key Components**:
  - Toast notification system
  - Theme management
  - Keybind system
  - Web config persistence
- **Important**: User interaction handlers

#### `frontend/static/js/api.js`
- **Purpose**: REST API wrapper
- **Key Components**:
  - API call functions
  - Connection management
  - Modem control
  - TX/RX operations
- **Important**: Single source of truth for API calls

### Configuration & Launch Files

#### `launcher.py`
- **Purpose**: Unified launcher with auto-setup
- **Key Features**:
  - Virtual environment creation
  - Dependency installation
  - FLDIGI detection and launch
  - Port availability checking
- **Important**: Main entry point for users

#### `requirements.txt`
- **Purpose**: Python dependencies
- **Key Packages**:
  - FastAPI, uvicorn
  - pyfldigi
  - WebSockets
  - prompt_toolkit, rich (for TUI)
- **Important**: Keep minimal, only necessary packages

### Standalone Files

#### `run_tui.py`
- **Purpose**: Terminal UI (independent of web backend)
- **Key Features**:
  - Direct XML-RPC communication
  - Full-screen terminal interface
  - Same macro system as web
  - Slash commands
- **Important**: Completely separate from web backend

---

## Testing & Debugging

### Testing Locally

1. **Start FLDIGI** with XML-RPC enabled (port 7362)
2. **Start backend**: `python -m backend.main`
3. **Open browser**: http://localhost:8000
4. **Check connection**: Look for green "Connected" status
5. **Test features**: Try TX/RX, macros, modem changes

### Common Development Issues

#### Port 8000 Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Use different port
export DIGISHELL_PORT=8080    # Linux/Mac
set DIGISHELL_PORT=8080       # Windows CMD
$env:DIGISHELL_PORT=8080      # Windows PowerShell
```

#### FLDIGI Not Connecting
1. Verify FLDIGI is running
2. Check Configure → Misc → XML-RPC Server
3. Ensure "Enable XML-RPC server" is checked
4. Verify port 7362 is correct
5. Check firewall settings

#### WebSocket Not Connecting
1. Check browser console for errors
2. Verify backend is running
3. Check for CORS issues (should be allowed)
4. Try different browser
5. Check WebSocket URL in `main.js`

### Debugging Tools

#### FastAPI Interactive Docs
- **URL**: http://localhost:8000/docs
- **Features**: Test all API endpoints, see request/response schemas
- **Useful for**: Quick API testing without frontend

#### Browser DevTools
- **Console**: JavaScript errors, logs
- **Network tab**: WebSocket messages, API calls
- **Application tab**: LocalStorage, config data

#### Backend Logging
```python
# Temporarily increase log level for debugging
logging.getLogger('backend.fldigi_client').setLevel(logging.DEBUG)
```

### Performance Monitoring

Monitor for these issues:
- **High CPU usage**: Reduce polling frequency
- **Memory leaks**: Check WebSocket connection cleanup
- **Slow responses**: Check FLDIGI responsiveness
- **Error spam**: Implement better error throttling

---

## Things to Avoid

### Don't Do This

1. **DON'T expose to the internet**
   - No authentication implemented
   - Designed for LAN/VPN only
   - Security not hardened for public exposure

2. **DON'T use frameworks unnecessarily**
   - Keep frontend vanilla JavaScript
   - Avoid introducing React, Vue, etc.
   - Simplicity is a feature

3. **DON'T spam error logs**
   - Use connection state tracking
   - Log disconnection once, not repeatedly
   - Throttle error messages

4. **DON'T assume FLDIGI is always running**
   - Always check `is_connected()` first
   - Handle `None` return values gracefully
   - Provide clear user feedback

5. **DON'T block the async event loop**
   - Use async/await for I/O operations
   - Keep polling intervals reasonable
   - Avoid synchronous operations in async functions

6. **DON'T hardcode configuration**
   - Use environment variables (e.g., DIGISHELL_PORT)
   - Store user settings in config files
   - Allow customization

7. **DON'T break backward compatibility without consideration**
   - Config file formats should be versioned
   - Provide migration paths for breaking changes
   - Document changes clearly

8. **DON'T add dependencies lightly**
   - Evaluate if built-in solutions exist
   - Consider package size and maintenance
   - Keep requirements.txt lean

9. **DON'T use interactive commands**
   - No `git rebase -i`, `git add -i`, etc.
   - Scripts must be non-interactive
   - Automated launchers can't handle prompts

10. **DON'T commit without testing**
    - Test with FLDIGI running
    - Test with FLDIGI stopped (disconnection handling)
    - Test on the target platform when possible

### Best Practices

1. **DO read existing code first**
   - Understand current patterns
   - Maintain consistency
   - Learn from existing implementations

2. **DO handle errors gracefully**
   - Clear user messages
   - Proper logging levels
   - Graceful degradation

3. **DO test connection scenarios**
   - FLDIGI running
   - FLDIGI stopped
   - FLDIGI crashes during operation
   - Network issues

4. **DO document complex logic**
   - Add comments for non-obvious code
   - Update DOCUMENTATION.md for API changes
   - Update README.md for user-facing changes

5. **DO use type hints**
   - Python: Use proper type hints
   - JavaScript: Add JSDoc comments for complex functions

6. **DO keep it simple**
   - KISS principle
   - Avoid premature optimization
   - Readable code > clever code

---

## Development Workflow Summary

### Typical Change Process

1. **Read relevant files** to understand current implementation
2. **Make changes** following established patterns
3. **Test locally** with FLDIGI running
4. **Test disconnection** by stopping FLDIGI
5. **Check logs** for errors or warnings
6. **Test in browser** (for frontend changes)
7. **Verify API docs** (for backend changes)
8. **Update documentation** if needed
9. **Commit with clear message**

### Git Commit Messages

Follow conventional commit style:
- `feat: Add new feature`
- `fix: Fix bug in component`
- `docs: Update documentation`
- `refactor: Refactor code`
- `style: Code style changes`
- `test: Add tests`

Examples from this project:
- `Add layout system for web interface`
- `Fix error spam and improve disconnection detection`
- `Remove automatic FlDigi reconnection`
- `Improve setup experience and error handling`

### Working on Feature Branches

- Create branch: `claude/feature-name-<session-id>`
- Make changes and commit regularly
- Push with: `git push -u origin <branch-name>`
- Create PR when ready
- Squash commits if needed before merging

---

## Additional Resources

### External Documentation

- **FastAPI**: https://fastapi.tiangolo.com/
- **pyFldigi**: https://pyfldigi.readthedocs.io/
- **FLDIGI XML-RPC**: http://www.w1hkj.com/FldigiHelp/xmlrpc_control.html
- **WebSocket API**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

### Project Documentation

- **README.md**: User-facing documentation, setup instructions
- **DOCUMENTATION.md**: Technical API reference, advanced topics
- **CLAUDE.md**: This file - development guide for AI assistants

### Code Comments

Key sections are commented in the code:
- Connection health monitoring in `main.py`
- RST/RSQ calculation in `fldigi_client.py`
- WebSocket message routing in `main.js`
- Macro placeholder expansion in `macros.py` and `run_tui.py`

---

## Questions to Ask Before Making Changes

1. **Does this align with the project's simplicity goals?**
2. **Am I maintaining consistency with existing patterns?**
3. **Have I read the relevant existing code?**
4. **How does this handle FLDIGI being disconnected?**
5. **Is this change backward compatible with user configs?**
6. **Does this need documentation updates?**
7. **Have I tested both connected and disconnected scenarios?**
8. **Am I introducing new dependencies unnecessarily?**
9. **Is the error handling appropriate?**
10. **Will this work on both Windows and Linux?**

---

## Final Notes

**Philosophy**: DigiShell aims to be a simple, reliable interface wrapper for FLDIGI. It's not trying to replace FLDIGI or implement advanced features. Keep changes focused on improving the user experience for common digital mode operations.

**AI Development Context**: This project was primarily developed with AI assistance as a learning exercise. The codebase reflects best practices for working with AI assistants: clear structure, consistent patterns, and comprehensive documentation.

**Security Note**: This application is designed for local/LAN use only. Do NOT expose to the public internet without adding proper authentication, HTTPS, and security hardening.

**73!** 📡

---

*Last Updated: 2025-11-22*
*For questions or clarifications about this guide, refer to the commit history or open an issue.*

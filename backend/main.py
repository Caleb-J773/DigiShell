import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.fldigi_client import fldigi_client
from backend.websocket_manager import manager
from backend.models import ConnectionStatus, StatusUpdate
from backend.routers import modem, txrx, rig, macros, settings, presets
from backend.dependencies import require_fldigi_connected
from backend.config import (
    STATUS_POLL_INTERVAL,
    CONNECTION_CHECK_INTERVAL,
    POLL_SLEEP_INTERVAL,
    CONSECUTIVE_FAILURE_THRESHOLD,
    ERROR_RETRY_INTERVAL
)

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logging.getLogger('pyfldigi').setLevel(logging.ERROR)
logging.getLogger('backend.fldigi_client').setLevel(logging.ERROR)
logging.getLogger('uvicorn').setLevel(logging.ERROR)
logging.getLogger('uvicorn.access').setLevel(logging.ERROR)

background_task = None


async def poll_fldigi_status():
    status_poll_counter = 0
    last_status = None
    connection_check_counter = 0
    last_connection_state = None
    consecutive_failures = 0

    while True:
        try:
            if fldigi_client.is_connected():
                connection_check_counter += 1
                if connection_check_counter >= CONNECTION_CHECK_INTERVAL:
                    connection_check_counter = 0
                    if not fldigi_client.check_connection_health():
                        logger.warning("FlDigi connection lost")
                        consecutive_failures = 0
                        await manager.broadcast_connection_status(
                            connected=False,
                            details={"error": "FlDigi disconnected. Use the Connect button to reconnect."}
                        )
                        last_connection_state = False
                        await asyncio.sleep(POLL_SLEEP_INTERVAL)
                        continue

                new_rx_text = fldigi_client.get_rx_text()
                if new_rx_text:
                    await manager.broadcast_text(new_rx_text, text_type="rx")
                    consecutive_failures = 0

                status_poll_counter += 1
                if status_poll_counter >= STATUS_POLL_INTERVAL:
                    status_poll_counter = 0

                    # Get signal metrics
                    signal_metrics = fldigi_client.get_signal_metrics()

                    status = StatusUpdate(
                        modem=fldigi_client.get_modem(),
                        carrier=fldigi_client.get_carrier(),
                        bandwidth=fldigi_client.get_bandwidth(),
                        tx_status=fldigi_client.get_trx_status(),
                        rig_frequency=fldigi_client.get_rig_frequency(),
                        rig_mode=fldigi_client.get_rig_mode(),
                        rig_name=fldigi_client.get_rig_name(),
                        quality=signal_metrics.get("quality"),
                        snr=signal_metrics.get("snr"),
                        rst_estimate=signal_metrics.get("rst_estimate"),
                        rsq_estimate=signal_metrics.get("rsq_estimate"),
                        connected=True
                    )

                    status_dict = status.model_dump(exclude_none=True)
                    if status_dict != last_status:
                        await manager.broadcast_status(status_dict)
                        last_status = status_dict

                    # Broadcast connection status if it changed to connected
                    if last_connection_state != True:
                        await manager.broadcast_connection_status(
                            connected=True,
                            details={
                                "version": fldigi_client.get_version(),
                                "name": fldigi_client.get_name()
                            }
                        )
                        last_connection_state = True
                        consecutive_failures = 0

            else:
                if last_connection_state != False:
                    await manager.broadcast_connection_status(
                        connected=False,
                        details={"error": "Not connected to FlDigi. Use the Connect button to reconnect."}
                    )
                    last_connection_state = False

            await asyncio.sleep(POLL_SLEEP_INTERVAL)

        except Exception as e:
            consecutive_failures += 1

            if consecutive_failures == 1 or consecutive_failures % 50 == 0:
                logger.error(f"Error in status polling: {e}")

            if consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD:
                if fldigi_client.is_connected():
                    logger.warning("Multiple consecutive failures, marking connection as lost")
                    fldigi_client.disconnect()
                    if last_connection_state != False:
                        await manager.broadcast_connection_status(
                            connected=False,
                            details={"error": "Connection to FlDigi lost. Use the Connect button to reconnect."}
                        )
                        last_connection_state = False
                consecutive_failures = 0

            await asyncio.sleep(ERROR_RETRY_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    success, error = fldigi_client.connect()
    if not success:
        logger.warning(f"Could not connect to FLDIGI: {error}. Will retry on WebSocket connection.")

    global background_task
    background_task = asyncio.create_task(poll_fldigi_status())

    yield

    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass

    fldigi_client.disconnect()


app = FastAPI(
    title="FLDIGI Web Wrapper",
    description="Modern web interface for FLDIGI digital modem application",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

app.include_router(modem.router)
app.include_router(txrx.router)
app.include_router(rig.router)
app.include_router(macros.router)
app.include_router(settings.router)
app.include_router(presets.router)



@app.get("/api/connection", response_model=ConnectionStatus)
async def get_connection_status():
    if fldigi_client.is_connected():
        return ConnectionStatus(
            connected=True,
            fldigi_version=fldigi_client.get_version(),
            fldigi_name=fldigi_client.get_name()
        )
    else:
        return ConnectionStatus(
            connected=False,
            error="Not connected to FLDIGI"
        )


@app.post("/api/connection/connect")
async def connect_to_fldigi():
    if fldigi_client.is_connected():
        return {"success": True, "message": "Already connected"}

    success, error = fldigi_client.connect()
    if success:
        await manager.broadcast_connection_status(
            connected=True,
            details={
                "version": fldigi_client.get_version(),
                "name": fldigi_client.get_name()
            }
        )
        return {"success": True, "message": "Connected to FLDIGI"}
    else:
        return {"success": False, "message": error or "Failed to connect to FLDIGI"}


@app.post("/api/connection/disconnect")
async def disconnect_from_fldigi():
    fldigi_client.disconnect()
    await manager.broadcast_connection_status(connected=False)
    return {"success": True, "message": "Disconnected from FLDIGI"}


@app.get("/api/status")
async def get_full_status(_: None = Depends(require_fldigi_connected)):
    return fldigi_client.get_status()



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        status = ConnectionStatus(
            connected=fldigi_client.is_connected(),
            fldigi_version=fldigi_client.get_version() if fldigi_client.is_connected() else None,
            fldigi_name=fldigi_client.get_name() if fldigi_client.is_connected() else None
        )
        await manager.send_personal_message(
            status.model_dump_json(),
            websocket
        )

        while True:
            data = await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)



@app.get("/")
async def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))



@app.get("/api")
async def read_root():
    return {
        "name": "FLDIGI Web Wrapper API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "fldigi_connected": fldigi_client.is_connected()
    }



@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "fldigi_connected": fldigi_client.is_connected(),
        "websocket_connections": manager.get_connection_count()
    }


if __name__ == "__main__":
    import uvicorn
    import signal
    import sys
    import os
    from backend.utils import check_port_available, get_network_ips

    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get port from environment variable or use default
    try:
        port = int(os.environ.get('DIGISHELL_PORT', 8000))
    except ValueError:
        print(f"ERROR: Invalid DIGISHELL_PORT value. Using default port 8000.")
        port = 8000

    # Check if port is available
    if not check_port_available(port):
        print()
        print("=" * 60)
        print(f"ERROR: Port {port} is already in use!")
        print("=" * 60)
        print()
        print("Another application is using this port. You have a few options:")
        print()
        print("1. Find and close the application using this port:")
        if sys.platform == "win32":
            print(f"   netstat -ano | findstr :{port}")
        else:
            print(f"   lsof -i :{port}")
            print(f"   netstat -tulpn | grep :{port}")
        print()
        print("2. Use a different port by setting the DIGISHELL_PORT environment variable:")
        if sys.platform == "win32":
            print("   Windows CMD:        set DIGISHELL_PORT=8080")
            print("   Windows PowerShell: $env:DIGISHELL_PORT=8080")
        else:
            print(f"   export DIGISHELL_PORT=8080")
        print()
        print("3. Then run DigiShell again")
        print()
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("FLDIGI Layer - Starting Server")
    print("=" * 60)
    print()
    print("Access URLs:")
    print(f"  Local:    http://localhost:{port}")

    network_ips = get_network_ips()
    if network_ips:
        for interface, ip in network_ips:
            label = f"({interface})" if interface else ""
            print(f"  Network:  http://{ip}:{port} {label}")

    print()
    print(f"API Docs:   http://localhost:{port}/docs")
    print(f"WebSocket:  ws://localhost:{port}/ws")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print()

    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="warning",
            access_log=False
        )
    except OSError as e:
        if "address already in use" in str(e).lower() or "10048" in str(e):
            print()
            print("=" * 60)
            print(f"ERROR: Failed to bind to port {port}")
            print("=" * 60)
            print()
            print("The port became unavailable while starting.")
            print("Please use a different port with DIGISHELL_PORT environment variable.")
            print("=" * 60)
            sys.exit(1)
        else:
            raise

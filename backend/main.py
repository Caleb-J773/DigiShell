import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.fldigi_client import fldigi_client
from backend.websocket_manager import manager
from backend.models import ConnectionStatus, StatusUpdate
from backend.routers import modem, txrx, rig, macros, settings

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

    while True:
        try:
            if fldigi_client.is_connected():
                new_rx_text = fldigi_client.get_rx_text()
                if new_rx_text:
                    await manager.broadcast_text(new_rx_text, text_type="rx")

                status_poll_counter += 1
                if status_poll_counter >= 5:
                    status_poll_counter = 0

                    status = StatusUpdate(
                        modem=fldigi_client.get_modem(),
                        carrier=fldigi_client.get_carrier(),
                        bandwidth=fldigi_client.get_bandwidth(),
                        tx_status=fldigi_client.get_trx_status(),
                        connected=True
                    )

                    status_dict = status.model_dump(exclude_none=True)
                    if status_dict != last_status:
                        await manager.broadcast_status(status_dict)
                        last_status = status_dict

            await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in status polling: {e}")
            await asyncio.sleep(1)


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
async def get_full_status():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

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
    import socket
    import os
    from dotenv import load_dotenv

    # Load environment variables from .env file if it exists
    load_dotenv()

    def get_network_ips():
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
            except:
                pass
        return ips

    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get configuration from environment variables
    host = os.getenv("DIGISHELL_HOST", "0.0.0.0")
    port = int(os.getenv("DIGISHELL_PORT", "8000"))

    print("=" * 60)
    print("DigiShell - Starting Server")
    print("=" * 60)
    print()
    print(f"Bind Address: {host}")
    print(f"Port:         {port}")
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

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="warning",
        access_log=False
    )

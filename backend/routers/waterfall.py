"""
FlDigi Waterfall Streaming Router

Provides REST API and WebSocket endpoints for the waterfall capture feature.
This is a BETA feature and disabled by default.
Supports both Linux (X11) and Windows platforms.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.waterfall_capture import waterfall_service


router = APIRouter(prefix="/api/waterfall", tags=["waterfall"])


class WaterfallStatusResponse(BaseModel):
    """Response model for waterfall status."""
    available: bool
    enabled: bool
    running: bool
    window_found: bool
    subscribers: int
    platform: str


class WaterfallEnableRequest(BaseModel):
    """Request to enable/disable waterfall streaming."""
    enabled: bool


class WaterfallEnableResponse(BaseModel):
    """Response for enable/disable requests."""
    success: bool
    message: str
    status: WaterfallStatusResponse


@router.get("/status", response_model=WaterfallStatusResponse)
async def get_waterfall_status():
    """
    Get the current status of the waterfall capture service.

    Returns availability, enabled state, running state, and subscriber count.
    """
    status = waterfall_service.get_status()
    return WaterfallStatusResponse(**status)


@router.post("/enable", response_model=WaterfallEnableResponse)
async def set_waterfall_enabled(request: WaterfallEnableRequest):
    """
    Enable or disable the waterfall capture service.

    Note: This is a beta feature.
    Requires platform-specific dependencies:
    - Linux: X11, python-xlib, Pillow
    - Windows: pywin32, Pillow
    """
    try:
        if request.enabled:
            if not waterfall_service.is_available():
                import sys
                if sys.platform == "linux":
                    req_msg = "Requires Linux with X11, python-xlib, and Pillow."
                elif sys.platform == "win32":
                    req_msg = "Requires Windows with pywin32 and Pillow."
                else:
                    req_msg = "Not supported on this platform."

                raise HTTPException(
                    status_code=400,
                    detail=f"Waterfall capture not available on this system. {req_msg}"
                )

            await waterfall_service.enable()
            message = "Waterfall streaming enabled"
        else:
            await waterfall_service.disable()
            message = "Waterfall streaming disabled"

        status = waterfall_service.get_status()
        return WaterfallEnableResponse(
            success=True,
            message=message,
            status=WaterfallStatusResponse(**status)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to {'enable' if request.enabled else 'disable'} waterfall streaming: {str(e)}"
        )


@router.websocket("/ws")
async def waterfall_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for receiving waterfall frames.

    Clients connect to this endpoint to receive real-time JPEG frames
    of the FlDigi waterfall window. Frames are sent as JSON with base64-encoded images.

    Message format:
    {
        "type": "waterfall_frame",
        "image": "<base64-encoded JPEG>",
        "timestamp": 1234567890.123
    }
    """
    await websocket.accept()

    # Add subscriber to service
    waterfall_service.add_subscriber(websocket)

    try:
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client (e.g., mouse clicks)
                message = await websocket.receive_json()

                # Handle different message types
                if message.get("type") == "mouse_click":
                    # Send click to FlDigi window
                    x = message.get("x")
                    y = message.get("y")
                    canvas_width = message.get("canvasWidth")
                    canvas_height = message.get("canvasHeight")

                    if x is not None and y is not None and canvas_width and canvas_height:
                        success = waterfall_service.send_mouse_click(
                            int(x), int(y), int(canvas_width), int(canvas_height)
                        )
                        await websocket.send_json({
                            "type": "click_ack",
                            "success": success,
                            "x": x,
                            "y": y
                        })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid click coordinates"
                        })

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error in waterfall websocket: {e}")
                break

    finally:
        # Remove subscriber when connection closes
        waterfall_service.remove_subscriber(websocket)

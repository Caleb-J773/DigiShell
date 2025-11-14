from fastapi import APIRouter, HTTPException
from backend.models import (
    TextTransmitRequest,
    TxRxStatus,
    TextResponse,
    StatusResponse,
    BackspaceRequest
)
from backend.fldigi_client import fldigi_client
from backend.websocket_manager import manager

router = APIRouter(prefix="/api/txrx", tags=["txrx"])


@router.get("/status", response_model=TxRxStatus)
async def get_status():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    status = fldigi_client.get_trx_status()
    if not status:
        raise HTTPException(status_code=500, detail="Failed to get status")

    return TxRxStatus(status=status)


@router.post("/tx", response_model=StatusResponse)
async def start_tx():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.tx()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start TX")

    return StatusResponse(success=True, message="Started transmitting")


@router.post("/rx", response_model=StatusResponse)
async def start_rx():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.rx()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to switch to RX")

    return StatusResponse(success=True, message="Switched to receive mode")


@router.post("/tune", response_model=StatusResponse)
async def start_tune():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.tune()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start TUNE")

    return StatusResponse(success=True, message="Started tuning")


@router.post("/abort", response_model=StatusResponse)
async def abort_tx():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.abort()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to abort")

    return StatusResponse(success=True, message="Aborted TX/TUNE")


@router.get("/text/rx", response_model=TextResponse)
async def get_rx_text():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    text = fldigi_client.get_rx_text()
    return TextResponse(text=text or "")


@router.post("/text/tx", response_model=StatusResponse)
async def add_tx_text(request: TextTransmitRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.add_tx_text(request.text)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add text to TX queue")

    return StatusResponse(
        success=True,
        message="Text added to transmit queue"
    )


@router.post("/text/clear/rx", response_model=StatusResponse)
async def clear_rx():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.clear_rx()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear RX buffer")

    return StatusResponse(success=True, message="RX buffer cleared")


@router.post("/text/clear/tx", response_model=StatusResponse)
async def clear_tx():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.clear_tx()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear TX buffer")

    return StatusResponse(success=True, message="TX buffer cleared")


@router.post("/text/tx/live/start", response_model=StatusResponse)
async def start_live_tx(request: TextTransmitRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.start_live_tx(request.text)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start live TX")

    return StatusResponse(success=True, message=f"Started live TX with {len(request.text)} characters")

@router.post("/text/tx/live/add", response_model=StatusResponse)
async def add_tx_chars_live(request: TextTransmitRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    start_tx = request.start_tx if request.start_tx is not None else True

    success = fldigi_client.add_tx_chars(request.text, start_tx=start_tx)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add characters to TX buffer")

    return StatusResponse(
        success=True,
        message=f"Added {len(request.text)} characters to TX buffer"
    )


@router.post("/text/tx/live/backspace", response_model=StatusResponse)
async def send_backspace_live(request: BackspaceRequest = BackspaceRequest()):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    for _ in range(request.count):
        success = fldigi_client.send_backspace()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send backspace")

    return StatusResponse(success=True, message=f"Sent {request.count} backspace(s)")


@router.post("/text/tx/live/end", response_model=StatusResponse)
async def end_tx_live():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.end_tx_live()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to end TX")

    return StatusResponse(success=True, message="TX ended, returning to RX")


@router.get("/text/tx/buffer-length")
async def get_tx_buffer_length():
    """Get the current TX buffer length (characters waiting to be transmitted)"""
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    length = fldigi_client.get_tx_buffer_length()
    if length is None:
        raise HTTPException(status_code=500, detail="Failed to get TX buffer length")

    return {"buffer_length": length}


@router.get("/text/tx/transmitted-data")
async def get_transmitted_data():
    """Get data that has been transmitted since last query (incremental)"""
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    data = fldigi_client.get_transmitted_data()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to get transmitted data")

    return {"data": data, "length": len(data)}

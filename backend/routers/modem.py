from fastapi import APIRouter, HTTPException
from backend.models import (
    ModemSetRequest,
    CarrierRequest,
    BandwidthRequest,
    ModemInfo,
    StatusResponse
)
from backend.fldigi_client import fldigi_client

router = APIRouter(prefix="/api/modem", tags=["modem"])


@router.get("/", response_model=ModemInfo)
@router.get("/info", response_model=ModemInfo)
async def get_modem_info():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    return ModemInfo(
        name=fldigi_client.get_modem() or "Unknown",
        carrier=fldigi_client.get_carrier() or 0,
        bandwidth=fldigi_client.get_bandwidth() or 0
    )


@router.get("/list")
async def list_modems():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    try:
        modem_names = fldigi_client.client.modem.names
        return {"modems": modem_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get modem list: {e}")


@router.post("/set", response_model=StatusResponse)
async def set_modem(request: ModemSetRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.set_modem(request.modem_name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set modem")

    return StatusResponse(
        success=True,
        message=f"Modem set to {request.modem_name}"
    )


@router.post("/carrier", response_model=StatusResponse)
async def set_carrier(request: CarrierRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.set_carrier(request.frequency)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set carrier")

    return StatusResponse(
        success=True,
        message=f"Carrier set to {request.frequency} Hz"
    )


@router.get("/carrier")
async def get_carrier():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    carrier = fldigi_client.get_carrier()
    if carrier is None:
        raise HTTPException(status_code=500, detail="Failed to get carrier")

    return {"carrier": carrier}


@router.post("/bandwidth", response_model=StatusResponse)
async def set_bandwidth(request: BandwidthRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.set_bandwidth(request.bandwidth)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set bandwidth")

    return StatusResponse(
        success=True,
        message=f"Bandwidth set to {request.bandwidth} Hz"
    )


@router.get("/bandwidth")
async def get_bandwidth():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    bandwidth = fldigi_client.get_bandwidth()
    if bandwidth is None:
        raise HTTPException(status_code=500, detail="Failed to get bandwidth")

    return {"bandwidth": bandwidth}


@router.get("/rsid")
async def get_rsid():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    rsid = fldigi_client.get_rsid()
    return {"rsid": rsid if rsid is not None else False}


@router.post("/rsid", response_model=StatusResponse)
async def set_rsid(enabled: bool):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.set_rsid(enabled)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set RSID")

    return StatusResponse(
        success=True,
        message=f"RSID {'enabled' if enabled else 'disabled'}"
    )


@router.get("/txid")
async def get_txid():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    txid = fldigi_client.get_txid()
    return {"txid": txid if txid is not None else False}


@router.post("/txid", response_model=StatusResponse)
async def set_txid(enabled: bool):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.set_txid(enabled)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set TXID")

    return StatusResponse(
        success=True,
        message=f"TXID {'enabled' if enabled else 'disabled'}"
    )

from fastapi import APIRouter, HTTPException, Depends
from backend.models import (
    ModemSetRequest,
    CarrierRequest,
    BandwidthRequest,
    ModemInfo,
    StatusResponse
)
from backend.fldigi_client import fldigi_client
from backend.dependencies import require_fldigi_connected

router = APIRouter(prefix="/api/modem", tags=["modem"])


@router.get("/", response_model=ModemInfo)
@router.get("/info", response_model=ModemInfo)
async def get_modem_info(_: None = Depends(require_fldigi_connected)):
    return ModemInfo(
        name=fldigi_client.get_modem() or "Unknown",
        carrier=fldigi_client.get_carrier() or 0,
        bandwidth=fldigi_client.get_bandwidth() or 0
    )


@router.get("/list")
async def list_modems(_: None = Depends(require_fldigi_connected)):
    try:
        modem_names = fldigi_client.client.modem.names
        return {"modems": modem_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get modem list: {e}")


@router.post("/set", response_model=StatusResponse)
async def set_modem(request: ModemSetRequest, _: None = Depends(require_fldigi_connected)):
    success = fldigi_client.set_modem(request.modem_name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set modem")

    return StatusResponse(
        success=True,
        message=f"Modem set to {request.modem_name}"
    )


@router.post("/carrier", response_model=StatusResponse)
async def set_carrier(request: CarrierRequest, _: None = Depends(require_fldigi_connected)):
    success = fldigi_client.set_carrier(request.frequency)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set carrier")

    return StatusResponse(
        success=True,
        message=f"Carrier set to {request.frequency} Hz"
    )


@router.get("/carrier")
async def get_carrier(_: None = Depends(require_fldigi_connected)):
    carrier = fldigi_client.get_carrier()
    if carrier is None:
        raise HTTPException(status_code=500, detail="Failed to get carrier")

    return {"carrier": carrier}


@router.post("/bandwidth", response_model=StatusResponse)
async def set_bandwidth(request: BandwidthRequest, _: None = Depends(require_fldigi_connected)):
    success = fldigi_client.set_bandwidth(request.bandwidth)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set bandwidth")

    return StatusResponse(
        success=True,
        message=f"Bandwidth set to {request.bandwidth} Hz"
    )


@router.get("/bandwidth")
async def get_bandwidth(_: None = Depends(require_fldigi_connected)):
    bandwidth = fldigi_client.get_bandwidth()
    if bandwidth is None:
        raise HTTPException(status_code=500, detail="Failed to get bandwidth")

    return {"bandwidth": bandwidth}


@router.get("/rsid")
async def get_rsid(_: None = Depends(require_fldigi_connected)):
    rsid = fldigi_client.get_rsid()
    return {"rsid": rsid if rsid is not None else False}


@router.post("/rsid", response_model=StatusResponse)
async def set_rsid(enabled: bool, _: None = Depends(require_fldigi_connected)):
    success = fldigi_client.set_rsid(enabled)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set RSID")

    return StatusResponse(
        success=True,
        message=f"RSID {'enabled' if enabled else 'disabled'}"
    )


@router.get("/txid")
async def get_txid(_: None = Depends(require_fldigi_connected)):
    txid = fldigi_client.get_txid()
    return {"txid": txid if txid is not None else False}


@router.post("/txid", response_model=StatusResponse)
async def set_txid(enabled: bool, _: None = Depends(require_fldigi_connected)):
    success = fldigi_client.set_txid(enabled)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set TXID")

    return StatusResponse(
        success=True,
        message=f"TXID {'enabled' if enabled else 'disabled'}"
    )


@router.get("/quality")
async def get_quality(_: None = Depends(require_fldigi_connected)):
    """Get modem signal quality (0-100)"""
    quality = fldigi_client.get_quality()
    if quality is None:
        raise HTTPException(status_code=500, detail="Failed to get quality")

    return {"quality": quality}


@router.get("/signal-metrics")
async def get_signal_metrics(_: None = Depends(require_fldigi_connected)):
    """Get comprehensive signal metrics including quality, SNR, and calculated RST/RSQ"""
    try:
        metrics = fldigi_client.get_signal_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get signal metrics: {e}")

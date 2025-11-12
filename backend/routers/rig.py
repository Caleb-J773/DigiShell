from fastapi import APIRouter, HTTPException
from backend.models import (
    RigFrequencyRequest,
    RigModeRequest,
    RigInfo,
    StatusResponse
)
from backend.fldigi_client import fldigi_client

router = APIRouter(prefix="/api/rig", tags=["rig"])


@router.get("/", response_model=RigInfo)
async def get_rig_info():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    return RigInfo(
        name=fldigi_client.get_rig_name(),
        frequency=fldigi_client.get_rig_frequency(),
        mode=fldigi_client.get_rig_mode()
    )


@router.post("/frequency", response_model=StatusResponse)
async def set_rig_frequency(request: RigFrequencyRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.set_rig_frequency(request.frequency)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set rig frequency")

    return StatusResponse(
        success=True,
        message=f"Rig frequency set to {request.frequency} Hz"
    )


@router.get("/frequency")
async def get_rig_frequency():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    frequency = fldigi_client.get_rig_frequency()
    return {"frequency": frequency}


@router.post("/mode", response_model=StatusResponse)
async def set_rig_mode(request: RigModeRequest):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    success = fldigi_client.set_rig_mode(request.mode)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set rig mode")

    return StatusResponse(
        success=True,
        message=f"Rig mode set to {request.mode}"
    )


@router.get("/mode")
async def get_rig_mode():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    mode = fldigi_client.get_rig_mode()
    return {"mode": mode}

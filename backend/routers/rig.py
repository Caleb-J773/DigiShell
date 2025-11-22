from fastapi import APIRouter, HTTPException, Depends
from backend.models import (
    RigFrequencyRequest,
    RigModeRequest,
    RigInfo,
    StatusResponse
)
from backend.fldigi_client import fldigi_client
from backend.dependencies import require_fldigi_connected

router = APIRouter(prefix="/api/rig", tags=["rig"])


@router.get("/", response_model=RigInfo)
async def get_rig_info(_: None = Depends(require_fldigi_connected)):
    return RigInfo(
        name=fldigi_client.get_rig_name(),
        frequency=fldigi_client.get_rig_frequency(),
        mode=fldigi_client.get_rig_mode()
    )


@router.post("/frequency", response_model=StatusResponse)
async def set_rig_frequency(request: RigFrequencyRequest, _: None = Depends(require_fldigi_connected)):
    success = fldigi_client.set_rig_frequency(request.frequency)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set rig frequency")

    return StatusResponse(
        success=True,
        message=f"Rig frequency set to {request.frequency} Hz"
    )


@router.get("/frequency")
async def get_rig_frequency(_: None = Depends(require_fldigi_connected)):
    frequency = fldigi_client.get_rig_frequency()
    return {"frequency": frequency}


@router.post("/mode", response_model=StatusResponse)
async def set_rig_mode(request: RigModeRequest, _: None = Depends(require_fldigi_connected)):
    success = fldigi_client.set_rig_mode(request.mode)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set rig mode")

    return StatusResponse(
        success=True,
        message=f"Rig mode set to {request.mode}"
    )


@router.get("/mode")
async def get_rig_mode(_: None = Depends(require_fldigi_connected)):
    mode = fldigi_client.get_rig_mode()
    return {"mode": mode}

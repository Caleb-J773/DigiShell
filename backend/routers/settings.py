import json
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.fldigi_client import fldigi_client

router = APIRouter(prefix="/api/settings", tags=["settings"])

WEB_CONFIG_FILE = Path.home() / ".fldigi_web.json"


class BooleanSetting(BaseModel):
    enabled: bool


class FloatSetting(BaseModel):
    value: float


class SettingResponse(BaseModel):
    success: bool
    message: str


class BooleanSettingResponse(BaseModel):
    enabled: bool


class FloatSettingResponse(BaseModel):
    value: float


class WebConfig(BaseModel):
    theme: Optional[str] = "dark"
    hasSeenWelcome: Optional[bool] = False
    custom_keybinds: Optional[Dict[str, Any]] = None


class WebConfigResponse(BaseModel):
    success: bool
    config: Optional[WebConfig] = None
    message: Optional[str] = None


def load_web_config() -> WebConfig:
    if WEB_CONFIG_FILE.exists():
        try:
            with open(WEB_CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return WebConfig(**data)
        except Exception as e:
            return WebConfig()
    return WebConfig()


def save_web_config(config: WebConfig) -> bool:
    try:
        with open(WEB_CONFIG_FILE, 'w') as f:
            json.dump(config.model_dump(exclude_none=True), f, indent=2)
        return True
    except Exception as e:
        return False


@router.get("/web-config", response_model=WebConfigResponse)
async def get_web_config():
    try:
        config = load_web_config()
        return WebConfigResponse(success=True, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load web config: {str(e)}")


@router.post("/web-config", response_model=WebConfigResponse)
async def save_web_config_endpoint(config: WebConfig):
    try:
        if save_web_config(config):
            return WebConfigResponse(
                success=True,
                config=config,
                message="Configuration saved successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save web config: {str(e)}")


@router.get("/afc", response_model=BooleanSettingResponse)
async def get_afc():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    afc = fldigi_client.get_afc()
    return BooleanSettingResponse(enabled=afc if afc is not None else False)


@router.post("/afc", response_model=SettingResponse)
async def set_afc(request: BooleanSetting):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    if fldigi_client.set_afc(request.enabled):
        return SettingResponse(
            success=True,
            message=f"AFC {'enabled' if request.enabled else 'disabled'}"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to set AFC")


@router.get("/squelch", response_model=BooleanSettingResponse)
async def get_squelch():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    squelch = fldigi_client.get_squelch()
    if squelch is None:
        raise HTTPException(status_code=500, detail="Failed to get squelch status")

    return BooleanSettingResponse(enabled=squelch)


@router.post("/squelch", response_model=SettingResponse)
async def set_squelch(request: BooleanSetting):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    if fldigi_client.set_squelch(request.enabled):
        return SettingResponse(
            success=True,
            message=f"Squelch {'enabled' if request.enabled else 'disabled'}"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to set squelch")


@router.get("/reverse", response_model=BooleanSettingResponse)
async def get_reverse():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    reverse = fldigi_client.get_reverse()
    return BooleanSettingResponse(enabled=reverse if reverse is not None else False)


@router.post("/reverse", response_model=SettingResponse)
async def set_reverse(request: BooleanSetting):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    if fldigi_client.set_reverse(request.enabled):
        return SettingResponse(
            success=True,
            message=f"Reverse sideband {'enabled' if request.enabled else 'disabled'}"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to set reverse")


@router.get("/squelch-level", response_model=FloatSettingResponse)
async def get_squelch_level():
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    level = fldigi_client.get_squelch_level()
    if level is None:
        raise HTTPException(status_code=500, detail="Failed to get squelch level")

    return FloatSettingResponse(value=level)


@router.post("/squelch-level", response_model=SettingResponse)
async def set_squelch_level(request: FloatSetting):
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

    if fldigi_client.set_squelch_level(request.value):
        return SettingResponse(
            success=True,
            message=f"Squelch level set to {request.value:.2f}"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to set squelch level")

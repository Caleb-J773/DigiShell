import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/macros", tags=["macros"])

CONFIG_FILE = Path.home() / ".fldigi_tui.json"

class Config(BaseModel):
    callsign: str
    name: str
    qth: str
    macros: Dict[str, str]

class ConfigUpdate(BaseModel):
    callsign: Optional[str] = None
    name: Optional[str] = None
    qth: Optional[str] = None

class MacroExpandRequest(BaseModel):
    text: str
    last_call: Optional[str] = None

class SetLastCallRequest(BaseModel):
    callsign: str

class MacroUpdateRequest(BaseModel):
    key: str
    text: str

class MacroDeleteRequest(BaseModel):
    key: str


def load_config() -> Config:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return Config(**data)
        except Exception:
            pass

    return Config(
        callsign="NOCALL",
        name="Operator",
        qth="Somewhere",
        macros={
            "1": "CQ CQ CQ de <MYCALL> <MYCALL> <MYCALL> pse k",
            "2": "<CALL> de <MYCALL> = Good morning! Name here is <MYNAME>. QTH is <MYQTH>. How copy? <CALL> de <MYCALL> k",
            "3": "<CALL> de <MYCALL> = Thanks for the report. 73 and best DX! <MYCALL> sk",
            "4": "<CALL> de <MYCALL> = QSL QSL, roger that. <MYCALL> k",
            "5": "<CALL> de <MYCALL> = Signal report is 5x9. <MYCALL> k"
        }
    )


def save_config(config: Config) -> bool:
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config.dict(), f, indent=2)
        return True
    except Exception:
        return False


def expand_macros(text: str, config: Config, last_call: Optional[str] = None) -> str:
    now = datetime.now()
    from datetime import timezone
    utc_now = datetime.now(timezone.utc)

    replacements = {
        '<MYCALL>': config.callsign,
        '<MYNAME>': config.name,
        '<MYQTH>': config.qth,
        '<CALL>': last_call or 'NOCALL',
        '<DATE>': now.strftime('%Y-%m-%d'),
        '<TIME>': now.strftime('%H:%M'),
        '<UTC>': utc_now.strftime('%H:%MZ'),
    }

    result = text
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


@router.get("/config", response_model=Config)
async def get_config():
    return load_config()


@router.post("/config")
async def update_config(update: ConfigUpdate):
    config = load_config()

    if update.callsign is not None:
        config.callsign = update.callsign.upper()
    if update.name is not None:
        config.name = update.name
    if update.qth is not None:
        config.qth = update.qth

    if save_config(config):
        return {"success": True, "config": config}
    else:
        raise HTTPException(status_code=500, detail="Failed to save configuration")


@router.post("/expand")
async def expand_macro(request: MacroExpandRequest):
    config = load_config()
    expanded = expand_macros(request.text, config, request.last_call)
    return {"expanded_text": expanded}


@router.get("/macros")
async def get_macros():
    config = load_config()
    return {"macros": config.macros}


@router.post("/add")
async def add_or_update_macro(request: MacroUpdateRequest):
    config = load_config()
    config.macros[request.key] = request.text

    if save_config(config):
        return {"success": True, "message": f"Macro '{request.key}' saved", "macros": config.macros}
    else:
        raise HTTPException(status_code=500, detail="Failed to save macro")


@router.post("/delete")
async def delete_macro(request: MacroDeleteRequest):
    config = load_config()

    if request.key not in config.macros:
        raise HTTPException(status_code=404, detail=f"Macro '{request.key}' not found")

    del config.macros[request.key]

    if save_config(config):
        return {"success": True, "message": f"Macro '{request.key}' deleted", "macros": config.macros}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete macro")

import json
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from backend.models import PresetFrequency, PresetFrequencyCreate, StatusResponse

router = APIRouter(prefix="/api/presets", tags=["presets"])

PRESETS_FILE = Path.home() / ".fldigi_tui_presets.json"

# Default preset frequencies for common modes and bands
# Based on standard amateur radio digital mode calling frequencies
DEFAULT_PRESETS = [
    # PSK31 - Common calling frequencies
    PresetFrequency(id="default-psk31-80m", name="80m PSK31", modem="PSK31", rig_frequency=3580150, carrier_frequency=1500, is_default=True, band="80m"),
    PresetFrequency(id="default-psk31-40m", name="40m PSK31", modem="PSK31", rig_frequency=7080150, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-psk31-30m", name="30m PSK31", modem="PSK31", rig_frequency=10142000, carrier_frequency=1500, is_default=True, band="30m"),
    PresetFrequency(id="default-psk31-20m", name="20m PSK31", modem="PSK31", rig_frequency=14070150, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-psk31-17m", name="17m PSK31", modem="PSK31", rig_frequency=18100000, carrier_frequency=1500, is_default=True, band="17m"),
    PresetFrequency(id="default-psk31-15m", name="15m PSK31", modem="PSK31", rig_frequency=21080000, carrier_frequency=1500, is_default=True, band="15m"),
    PresetFrequency(id="default-psk31-10m", name="10m PSK31", modem="PSK31", rig_frequency=28120000, carrier_frequency=1500, is_default=True, band="10m"),

    # PSK63
    PresetFrequency(id="default-psk63-20m", name="20m PSK63", modem="PSK63", rig_frequency=14070150, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-psk63-40m", name="40m PSK63", modem="PSK63", rig_frequency=7080150, carrier_frequency=1500, is_default=True, band="40m"),

    # RTTY - DX calling frequencies
    PresetFrequency(id="default-rtty-80m", name="80m RTTY", modem="RTTY", rig_frequency=3580000, carrier_frequency=2125, is_default=True, band="80m"),
    PresetFrequency(id="default-rtty-40m", name="40m RTTY", modem="RTTY", rig_frequency=7040000, carrier_frequency=2125, is_default=True, band="40m"),
    PresetFrequency(id="default-rtty-20m", name="20m RTTY", modem="RTTY", rig_frequency=14080000, carrier_frequency=2125, is_default=True, band="20m"),
    PresetFrequency(id="default-rtty-15m", name="15m RTTY", modem="RTTY", rig_frequency=21080000, carrier_frequency=2125, is_default=True, band="15m"),
    PresetFrequency(id="default-rtty-10m", name="10m RTTY", modem="RTTY", rig_frequency=28080000, carrier_frequency=2125, is_default=True, band="10m"),

    # Olivia - 16/500 and 8/250 are common calling modes
    PresetFrequency(id="default-olivia-80m", name="80m Olivia", modem="Olivia-16-500", rig_frequency=3583000, carrier_frequency=1500, is_default=True, band="80m"),
    PresetFrequency(id="default-olivia-40m", name="40m Olivia", modem="Olivia-16-500", rig_frequency=7073000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-olivia-20m", name="20m Olivia", modem="Olivia-16-500", rig_frequency=14070000, carrier_frequency=1500, is_default=True, band="20m"),

    # Contestia - 8/250 common for calling
    PresetFrequency(id="default-contestia-40m", name="40m Contestia", modem="Contestia-8-250", rig_frequency=7073000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-contestia-20m", name="20m Contestia", modem="Contestia-8-250", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),

    # MT63 - Common calling frequencies
    PresetFrequency(id="default-mt63-40m", name="40m MT63", modem="MT63-2000L", rig_frequency=7035000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-mt63-20m", name="20m MT63", modem="MT63-2000L", rig_frequency=14109000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-mt63-15m", name="15m MT63", modem="MT63-2000L", rig_frequency=21109000, carrier_frequency=1500, is_default=True, band="15m"),
    PresetFrequency(id="default-mt63-10m", name="10m MT63", modem="MT63-2000L", rig_frequency=28120000, carrier_frequency=1500, is_default=True, band="10m"),

    # Thor
    PresetFrequency(id="default-thor-40m", name="40m Thor", modem="Thor-16", rig_frequency=7043000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-thor-20m", name="20m Thor", modem="Thor-16", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),

    # DominoEX
    PresetFrequency(id="default-dominoex-40m", name="40m DominoEX", modem="DominoEX-16", rig_frequency=7073000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-dominoex-20m", name="20m DominoEX", modem="DominoEX-16", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),

    # MFSK
    PresetFrequency(id="default-mfsk16-40m", name="40m MFSK16", modem="MFSK-16", rig_frequency=7070000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-mfsk16-20m", name="20m MFSK16", modem="MFSK-16", rig_frequency=14070000, carrier_frequency=1500, is_default=True, band="20m"),

    # CW - CW portions of bands
    PresetFrequency(id="default-cw-80m", name="80m CW", modem="CW", rig_frequency=3550000, carrier_frequency=700, is_default=True, band="80m"),
    PresetFrequency(id="default-cw-40m", name="40m CW", modem="CW", rig_frequency=7030000, carrier_frequency=700, is_default=True, band="40m"),
    PresetFrequency(id="default-cw-20m", name="20m CW", modem="CW", rig_frequency=14050000, carrier_frequency=700, is_default=True, band="20m"),
    PresetFrequency(id="default-cw-15m", name="15m CW", modem="CW", rig_frequency=21050000, carrier_frequency=700, is_default=True, band="15m"),
    PresetFrequency(id="default-cw-10m", name="10m CW", modem="CW", rig_frequency=28050000, carrier_frequency=700, is_default=True, band="10m"),
]


def load_custom_presets() -> List[PresetFrequency]:
    """Load custom user presets from file"""
    if PRESETS_FILE.exists():
        try:
            with open(PRESETS_FILE, 'r') as f:
                data = json.load(f)
                return [PresetFrequency(**preset) for preset in data]
        except Exception:
            return []
    return []


def save_custom_presets(presets: List[PresetFrequency]) -> bool:
    """Save custom user presets to file"""
    try:
        with open(PRESETS_FILE, 'w') as f:
            json.dump([p.dict() for p in presets], f, indent=2)
        return True
    except Exception:
        return False


@router.get("/", response_model=List[PresetFrequency])
async def get_all_presets(mode_filter: str = None):
    """
    Get all presets (both default and custom).
    Optionally filter by modem mode.
    """
    all_presets = DEFAULT_PRESETS + load_custom_presets()

    if mode_filter:
        all_presets = [p for p in all_presets if p.modem.lower() == mode_filter.lower()]

    return all_presets


@router.get("/defaults", response_model=List[PresetFrequency])
async def get_default_presets():
    """Get only the default hardcoded presets"""
    return DEFAULT_PRESETS


@router.get("/custom", response_model=List[PresetFrequency])
async def get_custom_presets():
    """Get only user-created custom presets"""
    return load_custom_presets()


@router.post("/", response_model=PresetFrequency)
async def create_preset(request: PresetFrequencyCreate):
    """Create a new custom preset"""
    custom_presets = load_custom_presets()

    # Generate unique ID
    new_preset = PresetFrequency(
        id=f"custom-{uuid.uuid4()}",
        name=request.name,
        modem=request.modem,
        rig_frequency=request.rig_frequency,
        carrier_frequency=request.carrier_frequency,
        is_default=False,
        band=request.band
    )

    custom_presets.append(new_preset)

    if save_custom_presets(custom_presets):
        return new_preset
    else:
        raise HTTPException(status_code=500, detail="Failed to save preset")


@router.delete("/{preset_id}", response_model=StatusResponse)
async def delete_preset(preset_id: str):
    """Delete a custom preset (cannot delete default presets)"""
    # Check if trying to delete a default preset
    if preset_id.startswith("default-"):
        raise HTTPException(status_code=403, detail="Cannot delete default presets")

    custom_presets = load_custom_presets()

    # Find and remove the preset
    preset_found = False
    custom_presets = [p for p in custom_presets if p.id != preset_id]
    preset_found = len(custom_presets) < len(load_custom_presets())

    if not preset_found:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")

    if save_custom_presets(custom_presets):
        return StatusResponse(success=True, message=f"Preset deleted successfully")
    else:
        raise HTTPException(status_code=500, detail="Failed to delete preset")


@router.post("/{preset_id}/apply", response_model=StatusResponse)
async def apply_preset(preset_id: str):
    """
    Apply a preset (set modem mode, rig frequency, and carrier frequency).
    Returns the preset data to be applied by the frontend.
    """
    all_presets = DEFAULT_PRESETS + load_custom_presets()

    preset = next((p for p in all_presets if p.id == preset_id), None)

    if not preset:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")

    # Return the preset data for the frontend to apply
    return StatusResponse(
        success=True,
        message=f"Apply preset: {preset.name}",
        data=preset.dict()
    )

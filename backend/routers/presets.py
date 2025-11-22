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

    PresetFrequency(id="default-qpsk31-40m", name="40m QPSK31", modem="QPSK31", rig_frequency=7080150, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-qpsk31-20m", name="20m QPSK31", modem="QPSK31", rig_frequency=14070150, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-qpsk31-17m", name="17m QPSK31", modem="QPSK31", rig_frequency=18100000, carrier_frequency=1500, is_default=True, band="17m"),
    PresetFrequency(id="default-qpsk31-15m", name="15m QPSK31", modem="QPSK31", rig_frequency=21080000, carrier_frequency=1500, is_default=True, band="15m"),

    PresetFrequency(id="default-qpsk63-40m", name="40m QPSK63", modem="QPSK63", rig_frequency=7080150, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-qpsk63-20m", name="20m QPSK63", modem="QPSK63", rig_frequency=14070150, carrier_frequency=1500, is_default=True, band="20m"),

    PresetFrequency(id="default-8psk125-40m", name="40m 8PSK125", modem="8PSK125", rig_frequency=7080150, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-8psk125-20m", name="20m 8PSK125", modem="8PSK125", rig_frequency=14070150, carrier_frequency=1500, is_default=True, band="20m"),

    PresetFrequency(id="default-olivia-8-250-40m", name="40m Olivia 8/250", modem="Olivia-8-250", rig_frequency=7073000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-olivia-8-250-20m", name="20m Olivia 8/250", modem="Olivia-8-250", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-olivia-8-500-40m", name="40m Olivia 8/500", modem="Olivia-8-500", rig_frequency=7073000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-olivia-8-500-20m", name="20m Olivia 8/500", modem="Olivia-8-500", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-olivia-16-500-15m", name="15m Olivia 16/500", modem="Olivia-16-500", rig_frequency=21073000, carrier_frequency=1500, is_default=True, band="15m"),
    PresetFrequency(id="default-olivia-32-1000-20m", name="20m Olivia 32/1000", modem="Olivia-32-1000", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),

    PresetFrequency(id="default-contestia-4-125-40m", name="40m Contestia 4/125", modem="Contestia-4-125", rig_frequency=7073000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-contestia-8-250-15m", name="15m Contestia 8/250", modem="Contestia-8-250", rig_frequency=21073000, carrier_frequency=1500, is_default=True, band="15m"),
    PresetFrequency(id="default-contestia-16-500-20m", name="20m Contestia 16/500", modem="Contestia-16-500", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-contestia-32-1000-20m", name="20m Contestia 32/1000", modem="Contestia-32-1000", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),

    PresetFrequency(id="default-mfsk32-40m", name="40m MFSK32", modem="MFSK-32", rig_frequency=7070000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-mfsk32-20m", name="20m MFSK32", modem="MFSK-32", rig_frequency=14070000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-mfsk64-20m", name="20m MFSK64", modem="MFSK-64", rig_frequency=14070000, carrier_frequency=1500, is_default=True, band="20m"),

    PresetFrequency(id="default-thor-8-40m", name="40m Thor-8", modem="Thor-8", rig_frequency=7043000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-thor-11-20m", name="20m Thor-11", modem="Thor-11", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-thor-22-20m", name="20m Thor-22", modem="Thor-22", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),

    PresetFrequency(id="default-dominoex-8-40m", name="40m DominoEX-8", modem="DominoEX-8", rig_frequency=7073000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-dominoex-11-20m", name="20m DominoEX-11", modem="DominoEX-11", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-dominoex-22-20m", name="20m DominoEX-22", modem="DominoEX-22", rig_frequency=14073000, carrier_frequency=1500, is_default=True, band="20m"),

    PresetFrequency(id="default-hell-fm-40m", name="40m Hell-FM", modem="Hell-FM", rig_frequency=7040000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-hell-fm-20m", name="20m Hell-FM", modem="Hell-FM", rig_frequency=14063000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-hell-sl-40m", name="40m Hell-SL", modem="Hell-SL", rig_frequency=7040000, carrier_frequency=1500, is_default=True, band="40m"),

    PresetFrequency(id="default-throb-x1-40m", name="40m ThrobX-1", modem="ThrobX-1", rig_frequency=7070000, carrier_frequency=1500, is_default=True, band="40m"),
    PresetFrequency(id="default-throb-x1-20m", name="20m ThrobX-1", modem="ThrobX-1", rig_frequency=14070000, carrier_frequency=1500, is_default=True, band="20m"),
    PresetFrequency(id="default-throb-x2-20m", name="20m ThrobX-2", modem="ThrobX-2", rig_frequency=14070000, carrier_frequency=1500, is_default=True, band="20m"),
]


def load_custom_presets() -> List[PresetFrequency]:
    """Load custom user presets from file"""
    if PRESETS_FILE.exists():
        try:
            with open(PRESETS_FILE, 'r') as f:
                data = json.load(f)
                return [PresetFrequency(**preset) for preset in data]
        except (json.JSONDecodeError, OSError, ValueError):
            return []
    return []


def save_custom_presets(presets: List[PresetFrequency]) -> bool:
    """Save custom user presets to file"""
    try:
        with open(PRESETS_FILE, 'w') as f:
            json.dump([p.dict() for p in presets], f, indent=2)
        return True
    except (OSError, TypeError):
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
    if preset_id.startswith("default-"):
        raise HTTPException(status_code=403, detail="Cannot delete default presets")

    custom_presets = load_custom_presets()
    original_count = len(custom_presets)

    custom_presets = [p for p in custom_presets if p.id != preset_id]

    if len(custom_presets) == original_count:
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

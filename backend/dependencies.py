from fastapi import HTTPException, Depends
from backend.fldigi_client import fldigi_client


def require_fldigi_connected():
    """FastAPI dependency to ensure FLDIGI is connected."""
    if not fldigi_client.is_connected():
        raise HTTPException(status_code=503, detail="Not connected to FLDIGI")

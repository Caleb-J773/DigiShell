from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ModemSetRequest(BaseModel):
    modem_name: str = Field(..., description="Name of the modem (e.g., 'PSK31', 'RTTY')")


class CarrierRequest(BaseModel):
    frequency: int = Field(..., ge=0, le=4000, description="Carrier frequency in Hz")


class BandwidthRequest(BaseModel):
    bandwidth: int = Field(..., ge=0, description="Bandwidth in Hz")


class TextTransmitRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to transmit")
    start_tx: Optional[bool] = Field(True, description="Start transmission (for live TX mode)")


class BackspaceRequest(BaseModel):
    count: int = Field(1, ge=1, le=1000, description="Number of backspaces to send")


class RigFrequencyRequest(BaseModel):
    frequency: float = Field(..., ge=0, description="Frequency in Hz")


class RigModeRequest(BaseModel):
    mode: str = Field(..., description="Rig mode (e.g., 'USB', 'LSB')")


class StatusResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


class ModemInfo(BaseModel):
    name: str
    carrier: int
    bandwidth: int


class TxRxStatus(BaseModel):
    status: Literal["RX", "TX", "TUNE"]
    tx_queue_length: Optional[int] = None


class TextResponse(BaseModel):
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RigInfo(BaseModel):
    name: Optional[str] = None
    frequency: Optional[float] = None
    mode: Optional[str] = None


class ConnectionStatus(BaseModel):
    connected: bool
    fldigi_version: Optional[str] = None
    fldigi_name: Optional[str] = None
    error: Optional[str] = None


class WSMessage(BaseModel):
    type: str
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatusUpdate(BaseModel):
    modem: Optional[str] = None
    carrier: Optional[int] = None
    bandwidth: Optional[int] = None
    tx_status: Optional[str] = None
    rx_text: Optional[str] = None
    connected: bool = True
    rig_frequency: Optional[float] = None
    rig_mode: Optional[str] = None
    rig_name: Optional[str] = None
    quality: Optional[float] = None
    snr: Optional[float] = None
    rst_estimate: Optional[str] = None
    rsq_estimate: Optional[str] = None


class PresetFrequency(BaseModel):
    id: str = Field(..., description="Unique identifier for the preset")
    name: str = Field(..., min_length=1, max_length=50, description="Display name for the preset")
    modem: str = Field(..., description="Modem mode (e.g., 'PSK31', 'RTTY')")
    rig_frequency: float = Field(..., ge=0, description="Rig frequency in Hz")
    carrier_frequency: int = Field(1500, ge=500, le=3000, description="Carrier frequency in Hz")
    is_default: bool = Field(False, description="Whether this is a hardcoded default preset")
    band: Optional[str] = Field(None, description="Band name (e.g., '20m', '40m')")


class PresetFrequencyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Display name for the preset")
    modem: str = Field(..., description="Modem mode (e.g., 'PSK31', 'RTTY')")
    rig_frequency: float = Field(..., ge=0, description="Rig frequency in Hz")
    carrier_frequency: int = Field(1500, ge=500, le=3000, description="Carrier frequency in Hz")
    band: Optional[str] = Field(None, description="Band name (e.g., '20m', '40m')")

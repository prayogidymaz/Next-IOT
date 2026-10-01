from typing import Literal

from pydantic import BaseModel, Field


class CyberdeckMeshNode(BaseModel):
    node_id: str
    label: str
    device_type: str
    latitude: float | None = None
    longitude: float | None = None
    rssi: float | None = None
    snr: float | None = None
    battery_pct: float | None = None
    channel: int = 1
    online: bool = True


class CyberdeckMeshResponse(BaseModel):
    count: int
    nodes: list[CyberdeckMeshNode]


class CyberdeckHealthResponse(BaseModel):
    cpu_temp_c: float
    ram_used_pct: float
    battery_pct: float
    power_source: str
    uptime_sec: int
    lora_channel: int = 1
    encryption: str = "AES-128-GCM"


class PttTextDispatchRequest(BaseModel):
    target_node_id: str | None = Field(default=None, description="None = mesh broadcast")
    channel: int = Field(ge=1, le=8, default=1)
    message: str = Field(min_length=1, max_length=160)
    encrypt: bool = True


class PttBeaconRequest(BaseModel):
    channel: int = Field(ge=1, le=8, default=1)
    latitude: float | None = None
    longitude: float | None = None
    severity: Literal["info", "warning", "critical"] = "critical"


class PttDispatchResponse(BaseModel):
    ok: bool = True
    packet_id: str
    encrypted: bool
    channel: int
    message: str

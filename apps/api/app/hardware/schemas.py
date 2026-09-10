from pydantic import BaseModel, Field


class GatewayStatusResponse(BaseModel):
    serial_connected: bool = False
    serial_port: str | None = None
    lora_link: str = "disconnected"
    last_packet_at: str | None = None
    node_id: str | None = None
    rssi: float | None = None
    snr: float | None = None
    packets_received: int = 0
    updated_at: str | None = None


class LoRaTelemetryEvent(BaseModel):
    node_id: str
    device_id: str | None = None
    latitude: float
    longitude: float
    altitude_m: float
    rssi: float | None = None
    snr: float | None = None
    recorded_at: str
    source: str = Field(default="lora_bridge")

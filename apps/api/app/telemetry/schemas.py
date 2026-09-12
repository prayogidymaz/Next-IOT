import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TelemetryIngestRequest(BaseModel):
    timestamp: datetime = Field(description="ISO-8601 timestamp when sensor data was recorded")
    metrics: dict[str, float | int] = Field(min_length=1, description="Sensor readings e.g. temperature, humidity")

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value: dict[str, float | int]) -> dict[str, float | int]:
        for key in value:
            normalized = key.replace("_", "").replace(".", "")
            if not normalized.isalnum():
                raise ValueError(f"Invalid metric key: {key}")
        return value


class TelemetryIngestResponse(BaseModel):
    reading_id: uuid.UUID
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    recorded_at: datetime
    metrics: dict[str, Any]
    cached: bool = True
    rules_triggered: int = 0


class TelemetryLatestResponse(BaseModel):
    device_id: uuid.UUID
    reading_id: str | None = None
    recorded_at: str | None = None
    metrics: dict[str, Any]
    cached_at: str | None = None
    source: str = "redis"


class TelemetryHistoryItem(BaseModel):
    reading_id: uuid.UUID
    recorded_at: datetime
    metrics: dict[str, Any]
    ingested_at: datetime


class TelemetryHistoryResponse(BaseModel):
    device_id: uuid.UUID
    count: int
    items: list[TelemetryHistoryItem]


class SignalHeatmapPoint(BaseModel):
    lat: float
    lon: float
    rssi: float
    snr: float | None = None
    signal_score: int
    signal_strength: str
    recorded_at: datetime


class SignalHeatmapResponse(BaseModel):
    device_id: uuid.UUID
    hours: int
    count: int
    points: list[SignalHeatmapPoint]


class TelemetryAnomalyItem(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    severity: str
    anomaly_type: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    recorded_at: datetime
    detected_at: datetime


class TelemetryAnomalyResponse(BaseModel):
    device_id: uuid.UUID
    hours: int
    count: int
    items: list[TelemetryAnomalyItem]


class FlightReplayAnomalyBrief(BaseModel):
    id: uuid.UUID
    severity: str
    anomaly_type: str
    message: str


class FlightReplaySample(BaseModel):
    timestamp: datetime
    lat: float
    lon: float
    alt: float | None = None
    speed: float | None = None
    heading: float | None = None
    rssi: float | None = None
    anomalies: list[FlightReplayAnomalyBrief] = Field(default_factory=list)


class FlightReplayResponse(BaseModel):
    device_id: uuid.UUID
    session_start: datetime
    session_end: datetime
    hours: int | None = None
    count: int
    samples: list[FlightReplaySample]


class SwarmLinkItem(BaseModel):
    device_a_id: str
    device_b_id: str
    distance_m: float
    collision_risk: bool
    warning: str | None = None


class SwarmMatrixResponse(BaseModel):
    node_count: int
    link_count: int
    collision_threshold_m: float
    has_collision_risk: bool
    links: list[SwarmLinkItem]


class WeatherVectorPoint(BaseModel):
    lat: float
    lon: float
    wind_speed_m_s: float
    wind_direction_deg: float


class WeatherVectorResponse(BaseModel):
    lat: float
    lon: float
    radius_m: float
    wind_speed_m_s: float
    wind_direction_deg: float
    visibility_m: float
    rain_rate_mm_h: float
    flight_safety_status: str
    vector_count: int
    vectors: list[WeatherVectorPoint]


class TelemetryAnalyticsResponse(BaseModel):
    device_id: uuid.UUID
    hours: int
    reading_count: int
    max_speed_m_s: float | None = None
    avg_altitude_m: float | None = None
    min_voltage_v: float | None = None
    total_distance_m: float
    anomaly_count: int

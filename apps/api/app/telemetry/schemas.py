import uuid
from datetime import datetime

from pydantic import BaseModel, Field, JsonValue, field_validator

from app.telemetry.smart_home_metrics import normalize_telemetry_metrics


class TelemetryIngestRequest(BaseModel):
    timestamp: datetime = Field(description="ISO-8601 timestamp when sensor data was recorded")
    metrics: dict[str, JsonValue] = Field(
        min_length=1,
        description=(
            "Sensor readings e.g. temperature, humidity. "
            "Smart Home keys: relay_state (ON/OFF), pir_motion (bool), "
            "hvac_temp (numeric), lock_state (LOCKED/UNLOCKED)."
        ),
    )

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        for key in value:
            normalized = key.replace("_", "").replace(".", "")
            if not normalized.isalnum():
                raise ValueError(f"Invalid metric key: {key}")
        return normalize_telemetry_metrics(value)


class TelemetryIngestResponse(BaseModel):
    reading_id: uuid.UUID
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    recorded_at: datetime
    metrics: dict[str, JsonValue]
    cached: bool = True
    rules_triggered: int = 0


class TelemetryBulkIngestItem(BaseModel):
    device_id: uuid.UUID
    timestamp: datetime
    metrics: dict[str, JsonValue] = Field(min_length=1)

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        return TelemetryIngestRequest.validate_metrics(value)


class TelemetryBulkIngestRequest(BaseModel):
    items: list[TelemetryBulkIngestItem] = Field(min_length=1, max_length=200)


class TelemetryBulkIngestResponse(BaseModel):
    accepted: int
    failed: int
    reading_ids: list[uuid.UUID]
    errors: list[dict[str, str]] = Field(default_factory=list)


class TelemetryLatestResponse(BaseModel):
    device_id: uuid.UUID
    reading_id: str | None = None
    recorded_at: str | None = None
    metrics: dict[str, JsonValue]
    cached_at: str | None = None
    source: str = "redis"


class TelemetryHistoryItem(BaseModel):
    reading_id: uuid.UUID
    recorded_at: datetime
    metrics: dict[str, JsonValue]
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
    metadata: dict[str, JsonValue] = Field(default_factory=dict)
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


class MetricStatsSummary(BaseModel):
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    latest: float | None = None


class TimeSeriesBucketPoint(BaseModel):
    bucket_start: datetime
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    count: int = 0


class MetricTimeSeries(BaseModel):
    metric: str
    stats: MetricStatsSummary
    points: list[TimeSeriesBucketPoint] = Field(default_factory=list)


class TelemetryAnalyticsResponse(BaseModel):
    device_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    interval: str | None = None
    hours: int | None = None
    reading_count: int
    max_speed_m_s: float | None = None
    avg_altitude_m: float | None = None
    min_voltage_v: float | None = None
    total_distance_m: float = 0
    anomaly_count: int = 0
    series: list[MetricTimeSeries] = Field(default_factory=list)

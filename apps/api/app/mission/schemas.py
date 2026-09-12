import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SarGridPatternEnum(StrEnum):
    EXPANDING_SQUARE = "expanding_square"
    PARALLEL_TRACK = "parallel_track"


class SarGridRequest(BaseModel):
    lkp_lat: float = Field(..., ge=-90, le=90)
    lkp_lon: float = Field(..., ge=-180, le=180)
    radius_m: float = Field(..., gt=0, le=50_000)
    pattern: SarGridPatternEnum = SarGridPatternEnum.EXPANDING_SQUARE
    leg_spacing_m: float = Field(default=100.0, gt=0, le=5_000)


class GeoPoint(BaseModel):
    lat: float
    lon: float


class SarGridWaypoint(BaseModel):
    sequence: int
    lat: float
    lon: float
    label: str | None = None


class SarGridTrack(BaseModel):
    track_index: int
    points: list[GeoPoint]


class SarGridSearchArea(BaseModel):
    label: str
    points: list[GeoPoint]


class SarGridResponse(BaseModel):
    pattern: str
    lkp: GeoPoint
    radius_m: float
    leg_spacing_m: float
    waypoint_count: int
    waypoints: list[SarGridWaypoint]
    tracks: list[SarGridTrack]
    search_areas: list[SarGridSearchArea]


class GeofenceActionEnum(StrEnum):
    WARN = "WARN"
    RTL = "RTL"
    LAND = "LAND"


class GeofenceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    polygon_coords: list[GeoPoint] = Field(..., min_length=3)
    max_altitude: float = Field(default=120.0, gt=0, le=10_000)
    min_altitude: float = Field(default=0.0, ge=0)
    action_on_breach: GeofenceActionEnum = GeofenceActionEnum.WARN


class GeofenceUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    polygon_coords: list[GeoPoint] | None = Field(default=None, min_length=3)
    max_altitude: float | None = Field(default=None, gt=0, le=10_000)
    min_altitude: float | None = Field(default=None, ge=0)
    action_on_breach: GeofenceActionEnum | None = None


class GeofenceZoneResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    polygon_coords: list[GeoPoint]
    max_altitude: float
    min_altitude: float
    action_on_breach: str
    created_at: datetime
    updated_at: datetime


class GeofenceListResponse(BaseModel):
    count: int
    items: list[GeofenceZoneResponse]


class SarIncidentTypeEnum(StrEnum):
    PERSON_LOST = "PERSON_LOST"
    VEHICLE_CRASH = "VEHICLE_CRASH"
    DRONE_DOWN = "DRONE_DOWN"


class SarIncidentStatusEnum(StrEnum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"


class SarIncidentCreateRequest(BaseModel):
    incident_type: SarIncidentTypeEnum
    target_lat: float = Field(..., ge=-90, le=90)
    target_lon: float = Field(..., ge=-180, le=180)
    severity: str = Field(default="critical", min_length=1, max_length=16)
    assigned_device_id: uuid.UUID | None = None
    message: str | None = None
    metadata: dict | None = None


class SarIncidentUpdateRequest(BaseModel):
    status: SarIncidentStatusEnum | None = None
    assigned_device_id: uuid.UUID | None = None
    severity: str | None = Field(default=None, min_length=1, max_length=16)
    message: str | None = None
    regenerate_grid: bool = False


class SarIncidentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    incident_type: str
    status: str
    target_lat: float
    target_lon: float
    severity: str
    assigned_device_id: uuid.UUID | None
    message: str | None
    sar_grid: dict
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None


class SarIncidentListResponse(BaseModel):
    count: int
    items: list[SarIncidentResponse]

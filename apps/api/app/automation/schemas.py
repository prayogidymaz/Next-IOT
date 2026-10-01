import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, JsonValue


class PipelineNodeType(StrEnum):
    TRIGGER = "TRIGGER"
    CONDITION = "CONDITION"
    ACTION = "ACTION"


class TriggerSubtype(StrEnum):
    AI_DETECTION = "AI_DETECTION"
    TELEMETRY_ANOMALY = "TELEMETRY_ANOMALY"
    GEOFENCE_BREACH = "GEOFENCE_BREACH"
    WEATHER_HAZARD = "WEATHER_HAZARD"
    TELEMETRY_THRESHOLD = "TELEMETRY_THRESHOLD"


class ConditionSubtype(StrEnum):
    WIND_SPEED_LESS_THAN = "WIND_SPEED_LESS_THAN"
    BATTERY_ABOVE = "BATTERY_ABOVE"
    TIME_WINDOW = "TIME_WINDOW"
    LOGIC_AND = "LOGIC_AND"
    LOGIC_OR = "LOGIC_OR"


class ActionSubtype(StrEnum):
    MAVLINK_ARM = "MAVLINK_ARM"
    MAVLINK_RTL = "MAVLINK_RTL"
    MAVLINK_LAND = "MAVLINK_LAND"
    DISPATCH_SAR_GRID = "DISPATCH_SAR_GRID"
    TRIGGER_ALARM = "TRIGGER_ALARM"
    TRIGGER_ALERT = "TRIGGER_ALERT"
    WEBSOCKET_ALERT = "WEBSOCKET_ALERT"
    DEVICE_COMMAND = "DEVICE_COMMAND"
    SEND_WEBHOOK = "SEND_WEBHOOK"


class PipelineNode(BaseModel):
    id: str
    type: PipelineNodeType
    subtype: str
    config: dict[str, JsonValue] = Field(default_factory=dict)


class PipelineEdge(BaseModel):
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")

    model_config = {"populate_by_name": True}


class AutomationPipelineCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    is_active: bool = True
    nodes_json: list[dict[str, JsonValue]] = Field(default_factory=list)
    edges_json: list[dict[str, JsonValue]] = Field(default_factory=list)


class AutomationPipelineUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    is_active: bool | None = None
    nodes_json: list[dict[str, JsonValue]] | None = None
    edges_json: list[dict[str, JsonValue]] | None = None


class AutomationPipelineResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    nodes_json: list[dict[str, JsonValue]]
    edges_json: list[dict[str, JsonValue]]
    created_at: datetime
    updated_at: datetime


class AutomationPipelineListResponse(BaseModel):
    count: int
    items: list[AutomationPipelineResponse]


class PipelineTestRunRequest(BaseModel):
    event_type: str
    context: dict[str, JsonValue] = Field(default_factory=dict)
    nodes: list[dict[str, JsonValue]] | None = None
    edges: list[dict[str, JsonValue]] | None = None


class PipelineDryRunRequest(BaseModel):
    event_type: str
    context: dict[str, JsonValue] = Field(default_factory=dict)
    nodes: list[dict[str, JsonValue]] = Field(default_factory=list)
    edges: list[dict[str, JsonValue]] = Field(default_factory=list)
    pipeline_name: str = "Dry Run"


class PipelineExecutionStep(BaseModel):
    node_id: str
    node_type: str
    subtype: str
    matched: bool
    result: dict[str, JsonValue] = Field(default_factory=dict)


class PipelineTestRunResponse(BaseModel):
    pipeline_id: uuid.UUID
    pipeline_name: str
    event_type: str
    executed: bool
    steps: list[PipelineExecutionStep]

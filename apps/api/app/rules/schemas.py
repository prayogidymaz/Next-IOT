import uuid
from datetime import datetime

from pydantic import BaseModel, Field, JsonValue, field_validator, model_validator

from app.models.rule import RuleActionType, RuleOperator, RuleTriggerType
from app.rules.rule_validation import validate_actions, validate_trigger_config

VALID_OPERATORS = frozenset(o.value for o in RuleOperator)
VALID_ACTION_TYPES = frozenset(a.value for a in RuleActionType)
VALID_TRIGGER_TYPES = frozenset(t.value for t in RuleTriggerType)


class RuleActionConfig(BaseModel):
    type: str
    config: dict[str, JsonValue] = Field(default_factory=dict)


class RuleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    trigger_type: str | None = None
    trigger_config: dict[str, JsonValue] | None = None
    condition_expr: str | None = None
    actions: list[RuleActionConfig] | None = None
    enabled: bool = True
    priority: int = Field(default=100, ge=0, le=1000)
    device_id: uuid.UUID | None = None
    metric: str | None = Field(default=None, min_length=1, max_length=100)
    operator: str | None = None
    threshold: float | None = None
    action_type: str = RuleActionType.ALERT
    is_active: bool = True

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_OPERATORS:
            raise ValueError(f"Invalid operator. Allowed: {sorted(VALID_OPERATORS)}")
        return value

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, value: str) -> str:
        if value not in VALID_ACTION_TYPES:
            raise ValueError(f"Invalid action_type. Allowed: {sorted(VALID_ACTION_TYPES)}")
        return value

    @field_validator("trigger_type")
    @classmethod
    def validate_trigger_type(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_TRIGGER_TYPES:
            raise ValueError(f"Invalid trigger_type. Allowed: {sorted(VALID_TRIGGER_TYPES)}")
        return value

    @field_validator("metric")
    @classmethod
    def validate_metric(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.replace("_", "").replace(".", "")
        if not normalized.isalnum():
            raise ValueError(f"Invalid metric key: {value}")
        return value

    @model_validator(mode="after")
    def validate_shape(self) -> "RuleCreateRequest":
        if self.trigger_type is None:
            if self.device_id is None or self.metric is None or self.operator is None or self.threshold is None:
                raise ValueError("Legacy rules require device_id, metric, operator, threshold")
            return self
        assert self.trigger_type is not None
        config = dict(self.trigger_config or {})
        errors = validate_trigger_config(self.trigger_type, config)
        action_dicts = [
            {"type": a.type, "config": a.config} for a in (self.actions or [])
        ]
        errors.extend(validate_actions(action_dicts))
        if errors:
            raise ValueError("; ".join(errors))
        return self


class RuleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    operator: str | None = None
    threshold: float | None = None
    action_type: str | None = None
    is_active: bool | None = None
    enabled: bool | None = None
    trigger_type: str | None = None
    trigger_config: dict[str, JsonValue] | None = None
    condition_expr: str | None = None
    actions: list[RuleActionConfig] | None = None
    priority: int | None = Field(default=None, ge=0, le=1000)

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_OPERATORS:
            raise ValueError(f"Invalid operator. Allowed: {sorted(VALID_OPERATORS)}")
        return value

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_ACTION_TYPES:
            raise ValueError(f"Invalid action_type. Allowed: {sorted(VALID_ACTION_TYPES)}")
        return value


class RulePutRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    trigger_type: str
    trigger_config: dict[str, JsonValue] = Field(default_factory=dict)
    condition_expr: str | None = None
    actions: list[RuleActionConfig] = Field(min_length=1)
    enabled: bool = True
    priority: int = Field(default=100, ge=0, le=1000)
    device_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def validate_put(self) -> "RulePutRequest":
        errors = validate_trigger_config(self.trigger_type, dict(self.trigger_config))
        errors.extend(
            validate_actions([{"type": a.type, "config": a.config} for a in self.actions])
        )
        if errors:
            raise ValueError("; ".join(errors))
        return self


class RuleTestRequest(BaseModel):
    sample_context: dict[str, JsonValue] = Field(default_factory=dict)


class RuleTestResponse(BaseModel):
    rendered_actions: list[dict[str, JsonValue]]
    would_execute: bool
    errors: list[str]


class RuleExecutionLogItem(BaseModel):
    id: uuid.UUID
    rule_id: uuid.UUID
    triggered_at: datetime
    trigger_context: dict[str, JsonValue]
    status: str
    actions_executed: int
    error_message: str | None
    duration_ms: int | None

    model_config = {"from_attributes": True}


class PipelineValidateRequest(BaseModel):
    document: dict[str, JsonValue] = Field(default_factory=dict)


class PipelineValidateResponse(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PipelineImportRequest(BaseModel):
    document: dict[str, JsonValue] = Field(default_factory=dict)


class PipelineExportResponse(BaseModel):
    schema_version: str
    exported_at: datetime | None = None
    pipeline: dict[str, JsonValue]


class RuleResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    device_id: uuid.UUID | None
    name: str
    metric: str
    operator: str
    threshold: float
    action_type: str
    is_active: bool
    enabled: bool
    trigger_type: str
    trigger_config: dict[str, JsonValue]
    condition_expr: str | None
    actions: list[dict[str, JsonValue]]
    last_executed_at: datetime | None
    execution_count: int
    last_error: str | None
    priority: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

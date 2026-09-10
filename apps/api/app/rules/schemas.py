import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.rule import RuleActionType, RuleOperator

VALID_OPERATORS = frozenset(o.value for o in RuleOperator)
VALID_ACTION_TYPES = frozenset(a.value for a in RuleActionType)


class RuleCreateRequest(BaseModel):
    device_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    metric: str = Field(min_length=1, max_length=100)
    operator: str
    threshold: float
    action_type: str = RuleActionType.ALERT
    is_active: bool = True

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, value: str) -> str:
        if value not in VALID_OPERATORS:
            raise ValueError(f"Invalid operator. Allowed: {sorted(VALID_OPERATORS)}")
        return value

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, value: str) -> str:
        if value not in VALID_ACTION_TYPES:
            raise ValueError(f"Invalid action_type. Allowed: {sorted(VALID_ACTION_TYPES)}")
        return value

    @field_validator("metric")
    @classmethod
    def validate_metric(cls, value: str) -> str:
        normalized = value.replace("_", "").replace(".", "")
        if not normalized.isalnum():
            raise ValueError(f"Invalid metric key: {value}")
        return value


class RuleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    operator: str | None = None
    threshold: float | None = None
    action_type: str | None = None
    is_active: bool | None = None

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


class RuleResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    device_id: uuid.UUID
    name: str
    metric: str
    operator: str
    threshold: float
    action_type: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

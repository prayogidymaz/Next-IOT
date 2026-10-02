"""Device profile thing-model specification (Pydantic v2, strict typing)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

KEY_PATTERN = re.compile(r"^[a-z0-9_]{1,64}$")
MAX_TELEMETRY_KEYS = 200


class AttributeScope(StrEnum):
    SERVER = "server"
    SHARED = "shared"
    CLIENT = "client"


def _validate_key(value: str) -> str:
    if not KEY_PATTERN.match(value):
        raise ValueError("key must use [a-z0-9_] only and be at most 64 characters")
    return value


def _unique_keys(items: Sequence[object], attr: str = "key") -> None:
    seen: set[str] = set()
    for item in items:
        key = getattr(item, attr)
        if key in seen:
            raise ValueError(f"duplicate key: {key}")
        seen.add(key)


class TelemetryKeyNumber(BaseModel):
    key: str
    label: str
    unit: str | None = None
    data_type: Literal["number"]
    min: float | None = None
    max: float | None = None
    precision: int | None = Field(default=None, ge=0, le=10)

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)

    @model_validator(mode="after")
    def _range(self) -> TelemetryKeyNumber:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("min cannot exceed max")
        return self


class TelemetryKeyInteger(BaseModel):
    key: str
    label: str
    unit: str | None = None
    data_type: Literal["integer"]
    min: int | None = None
    max: int | None = None

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)

    @model_validator(mode="after")
    def _range(self) -> TelemetryKeyInteger:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("min cannot exceed max")
        return self


class TelemetryKeyBoolean(BaseModel):
    key: str
    label: str
    unit: str | None = None
    data_type: Literal["boolean"]

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class TelemetryKeyString(BaseModel):
    key: str
    label: str
    unit: str | None = None
    data_type: Literal["string"]

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class TelemetryKeyEnum(BaseModel):
    key: str
    label: str
    unit: str | None = None
    data_type: Literal["enum"]
    values: list[str] = Field(min_length=1)

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


TelemetryKey = Annotated[
    TelemetryKeyNumber
    | TelemetryKeyInteger
    | TelemetryKeyBoolean
    | TelemetryKeyString
    | TelemetryKeyEnum,
    Field(discriminator="data_type"),
]


class AttributeDefNumber(BaseModel):
    key: str
    label: str
    scope: AttributeScope
    data_type: Literal["number"]
    default: float | None = None
    min: float | None = None
    max: float | None = None
    precision: int | None = Field(default=None, ge=0, le=10)

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class AttributeDefInteger(BaseModel):
    key: str
    label: str
    scope: AttributeScope
    data_type: Literal["integer"]
    default: int | None = None
    min: int | None = None
    max: int | None = None

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class AttributeDefBoolean(BaseModel):
    key: str
    label: str
    scope: AttributeScope
    data_type: Literal["boolean"]
    default: bool | None = None

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class AttributeDefString(BaseModel):
    key: str
    label: str
    scope: AttributeScope
    data_type: Literal["string"]
    default: str | None = None

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class AttributeDefEnum(BaseModel):
    key: str
    label: str
    scope: AttributeScope
    data_type: Literal["enum"]
    values: list[str] = Field(min_length=1)
    default: str | None = None

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)

    @model_validator(mode="after")
    def _default_in_values(self) -> AttributeDefEnum:
        if self.default is not None and self.default not in self.values:
            raise ValueError("default must be one of values")
        return self


AttributeDef = Annotated[
    AttributeDefNumber
    | AttributeDefInteger
    | AttributeDefBoolean
    | AttributeDefString
    | AttributeDefEnum,
    Field(discriminator="data_type"),
]


class CommandParamNumber(BaseModel):
    key: str
    data_type: Literal["number"]
    required: bool = True
    min: float | None = None
    max: float | None = None
    precision: int | None = Field(default=None, ge=0, le=10)

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class CommandParamInteger(BaseModel):
    key: str
    data_type: Literal["integer"]
    required: bool = True
    min: int | None = None
    max: int | None = None

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class CommandParamBoolean(BaseModel):
    key: str
    data_type: Literal["boolean"]
    required: bool = True

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class CommandParamString(BaseModel):
    key: str
    data_type: Literal["string"]
    required: bool = True

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


class CommandParamEnum(BaseModel):
    key: str
    data_type: Literal["enum"]
    required: bool = True
    values: list[str] = Field(min_length=1)

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)


CommandParam = Annotated[
    CommandParamNumber
    | CommandParamInteger
    | CommandParamBoolean
    | CommandParamString
    | CommandParamEnum,
    Field(discriminator="data_type"),
]


class CommandDef(BaseModel):
    key: str
    label: str
    params: list[CommandParam] = Field(default_factory=list)
    timeout_seconds: int = Field(default=30, ge=1, le=300)

    @field_validator("key")
    @classmethod
    def _key(cls, value: str) -> str:
        return _validate_key(value)

    @model_validator(mode="after")
    def _unique_params(self) -> CommandDef:
        _unique_keys(self.params)
        return self


class ThingModelSpec(BaseModel):
    telemetry: list[TelemetryKey] = Field(default_factory=list, max_length=MAX_TELEMETRY_KEYS)
    attributes: list[AttributeDef] = Field(default_factory=list)
    commands: list[CommandDef] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_definition_keys(self) -> ThingModelSpec:
        _unique_keys(self.telemetry)
        _unique_keys(self.attributes)
        _unique_keys(self.commands)
        return self


def parse_thing_model_spec(raw: dict[str, object]) -> ThingModelSpec:
    return ThingModelSpec.model_validate(raw)


def spec_to_storage(spec: ThingModelSpec) -> dict[str, object]:
    return spec.model_dump(mode="json")


TelemetryKeyDef = TelemetryKeyNumber | TelemetryKeyInteger | TelemetryKeyBoolean | TelemetryKeyString | TelemetryKeyEnum

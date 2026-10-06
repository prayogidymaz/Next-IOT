"""Pydantic schemas for EMQX HTTP authentication and authorization."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class MqttAuthResult(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    IGNORE = "ignore"


class MqttAuthRequest(BaseModel):
    username: str = Field(default="")
    password: str = Field(default="")
    clientid: str = Field(default="")
    listener: str | None = None
    protocol: str | None = None
    peerhost: str | None = None


class MqttAuthResponse(BaseModel):
    result: MqttAuthResult
    is_superuser: bool = False


class MqttAclRequest(BaseModel):
    username: str = Field(default="")
    clientid: str = Field(default="")
    topic: str = Field(default="")
    action: str = Field(default="")
    qos: int | None = None


class MqttAclResponse(BaseModel):
    result: MqttAuthResult


class MqttTelemetryIngestRequest(BaseModel):
    topic: str
    username: str = ""
    clientid: str = ""
    payload: str = ""

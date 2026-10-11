"""Firmware Studio request/response schemas."""

from __future__ import annotations

import uuid
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class McuTarget(StrEnum):
    ESP32_S3 = "esp32-s3"
    ESP32_C3 = "esp32-c3"
    ESP32_WROOM = "esp32-wroom"


class FrameworkTarget(StrEnum):
    PLATFORMIO = "platformio"
    ARDUINO = "arduino"


class SensorBinding(BaseModel):
    metric: str = Field(min_length=1, max_length=64)
    driver: str = Field(min_length=1, max_length=32)
    pin: int = Field(ge=0, le=48)


class FirmwareStudioConfig(BaseModel):
    mcu: McuTarget = McuTarget.ESP32_S3
    framework: FrameworkTarget = FrameworkTarget.PLATFORMIO
    wifi_ssid: str = Field(min_length=1, max_length=64)
    wifi_password: str = Field(min_length=1, max_length=128)
    broker_host: str = Field(min_length=1, max_length=255)
    broker_port: int = Field(default=1883, ge=1, le=65535)
    use_tls: bool = False
    publish_interval_s: int = Field(default=10, ge=1, le=3600)
    enable_ota: bool = False
    include_credentials: bool = False
    tenant_id: uuid.UUID | None = None
    device_id: uuid.UUID | None = None
    access_token: str | None = Field(default=None, max_length=128)
    sensors: list[SensorBinding] = Field(default_factory=list)

    @field_validator("access_token")
    @classmethod
    def strip_token(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class FirmwareGenerateRequest(BaseModel):
    device_profile_id: uuid.UUID
    config: FirmwareStudioConfig


class FirmwarePreviewResponse(BaseModel):
    platformio_ini: str
    main_cpp: str
    readme_md: str


class FirmwareTemplateInfo(BaseModel):
    mcus: list[str]
    frameworks: list[str]

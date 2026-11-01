"""Alert triage types."""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class AlertSnapshot:
    id: uuid.UUID
    tenant_id: uuid.UUID
    alarm_type: str
    severity: str
    title: str
    device_id: uuid.UUID | None
    lat: float | None
    lng: float | None
    metric: str | None


@dataclass(frozen=True)
class AlertCluster:
    signature: str
    alerts: list[AlertSnapshot]
    risk_score: float


@dataclass(frozen=True)
class RiskScore:
    value: int
    factors: dict[str, float]


@dataclass(frozen=True)
class BatchActionPlan:
    cluster_signature: str
    summary: str
    workflow_hint: str
    parallel_device_ids: list[str]

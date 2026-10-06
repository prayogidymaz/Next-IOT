"""Prometheus counters for thing-model ingest validation."""

from __future__ import annotations

import uuid

from prometheus_client import Counter

telemetry_rejected_total = Counter(
    "telemetry_rejected_total",
    "Telemetry metric keys rejected by thing-model validation",
    ["reason", "tenant_id"],
)
telemetry_unknown_keys_total = Counter(
    "telemetry_unknown_keys_total",
    "Telemetry metric keys not declared in thing model (still ingested)",
    ["tenant_id"],
)
telemetry_accepted_total = Counter(
    "telemetry_accepted_total",
    "Telemetry metric keys accepted by thing-model validation",
    ["tenant_id"],
)
command_rejected_total = Counter(
    "command_rejected_total",
    "Device commands rejected by thing-model validation",
    ["reason", "tenant_id"],
)


def _tenant_label(tenant_id: uuid.UUID) -> str:
    return str(tenant_id)


def record_telemetry_rejected(tenant_id: uuid.UUID, reason: str) -> None:
    telemetry_rejected_total.labels(reason=reason, tenant_id=_tenant_label(tenant_id)).inc()


def record_telemetry_unknown_key(tenant_id: uuid.UUID) -> None:
    telemetry_unknown_keys_total.labels(tenant_id=_tenant_label(tenant_id)).inc()


def record_telemetry_accepted_keys(tenant_id: uuid.UUID, count: int) -> None:
    if count <= 0:
        return
    telemetry_accepted_total.labels(tenant_id=_tenant_label(tenant_id)).inc(count)


def record_command_rejected(tenant_id: uuid.UUID, reason: str) -> None:
    command_rejected_total.labels(reason=reason, tenant_id=_tenant_label(tenant_id)).inc()

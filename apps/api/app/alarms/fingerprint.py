"""Stable alarm deduplication fingerprints."""

from __future__ import annotations

import hashlib
import uuid


def alarm_fingerprint(
    *,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID | None,
    alarm_type: str,
    dedup_key: str,
) -> str:
    device_part = str(device_id) if device_id is not None else ""
    payload = f"{tenant_id}|{device_part}|{alarm_type}|{dedup_key}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def dedup_key_from_details(details: dict[str, object]) -> str:
    metric = details.get("metric_key")
    if isinstance(metric, str) and metric:
        return metric
    return "default"

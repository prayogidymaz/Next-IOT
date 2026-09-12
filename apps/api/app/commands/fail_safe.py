"""Emergency fail-safe protocol — auto-dispatch RETURN_TO_HOME / EMERGENCY_LAND on critical anomalies."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.events import publish_device_command
from app.models.device_command import CommandStatus, CommandType, DeviceCommand

FAIL_SAFE_PRIORITY = "critical"

# Anomaly types that trigger automatic fail-safe when severity is critical.
_LAND_ANOMALY_TYPES = frozenset({"altitude_deviation", "speed_deviation"})
_RTH_ANOMALY_TYPES = frozenset({"voltage_drop", "battery_overheat", "signal_loss"})
_GEOFENCE_LAND_ACTION = "LAND"
_GEOFENCE_RTL_ACTION = "RTL"


class FailSafeProtocol:
    """Evaluate critical telemetry anomalies and dispatch high-priority emergency commands."""

    def resolve_action(
        self,
        anomaly_type: str,
        severity: str,
        metadata: dict[str, Any] | None = None,
    ) -> str | None:
        if severity != "critical":
            return None
        if anomaly_type == "geofence_breach":
            action = (metadata or {}).get("action_on_breach")
            if action == _GEOFENCE_LAND_ACTION:
                return CommandType.EMERGENCY_LAND
            if action == _GEOFENCE_RTL_ACTION:
                return CommandType.RETURN_TO_HOME
            return None
        if anomaly_type in _LAND_ANOMALY_TYPES:
            return CommandType.EMERGENCY_LAND
        if anomaly_type in _RTH_ANOMALY_TYPES:
            return CommandType.RETURN_TO_HOME
        return None

    def build_params(
        self,
        *,
        action: str,
        reason: str,
        anomaly_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "priority": FAIL_SAFE_PRIORITY,
            "fail_safe": True,
            "reason": reason,
            "action": action,
        }
        if anomaly_type:
            params["anomaly_type"] = anomaly_type
        if metadata:
            params["anomaly_metadata"] = metadata
        return params

    async def dispatch_fail_safe(
        self,
        db: AsyncSession,
        redis: aioredis.Redis,
        *,
        device_id: uuid.UUID,
        tenant_id: uuid.UUID,
        action: str,
        reason: str,
        anomaly_type: str | None = None,
        metadata: dict[str, Any] | None = None,
        issued_by_user_id: uuid.UUID | None = None,
    ) -> DeviceCommand:
        if action not in {CommandType.RETURN_TO_HOME, CommandType.EMERGENCY_LAND}:
            raise ValueError(f"Unsupported fail-safe action: {action}")

        params = self.build_params(
            action=action,
            reason=reason,
            anomaly_type=anomaly_type,
            metadata=metadata,
        )
        now = datetime.now(UTC)
        command = DeviceCommand(
            device_id=device_id,
            tenant_id=tenant_id,
            issued_by_user_id=issued_by_user_id,
            command_type=action,
            params=params,
            status=CommandStatus.DISPATCHED,
            dispatched_at=now,
        )
        db.add(command)
        await db.flush()

        await publish_device_command(
            redis,
            command_id=str(command.id),
            device_id=str(device_id),
            tenant_id=str(tenant_id),
            command_type=action,
            params=params,
            issued_by_user_id=str(issued_by_user_id) if issued_by_user_id else None,
        )
        return command

    async def handle_critical_anomalies(
        self,
        db: AsyncSession,
        redis: aioredis.Redis,
        *,
        device_id: uuid.UUID,
        tenant_id: uuid.UUID,
        anomalies: list[Any],
    ) -> list[DeviceCommand]:
        """Auto-dispatch fail-safe for each qualifying critical anomaly."""
        dispatched: list[DeviceCommand] = []
        seen_actions: set[str] = set()

        for anomaly in anomalies:
            severity = getattr(anomaly, "severity", None) or anomaly.get("severity")
            anomaly_type = getattr(anomaly, "anomaly_type", None) or anomaly.get("anomaly_type")
            message = getattr(anomaly, "message", None) or anomaly.get("message", "Critical anomaly")
            metadata = getattr(anomaly, "metadata_", None) or anomaly.get("metadata") or {}

            action = self.resolve_action(
                str(anomaly_type),
                str(severity),
                metadata if isinstance(metadata, dict) else {},
            )
            if action is None or action in seen_actions:
                continue

            command = await self.dispatch_fail_safe(
                db,
                redis,
                device_id=device_id,
                tenant_id=tenant_id,
                action=action,
                reason=str(message),
                anomaly_type=str(anomaly_type),
                metadata=metadata if isinstance(metadata, dict) else {},
            )
            dispatched.append(command)
            seen_actions.add(action)

        return dispatched


fail_safe_protocol = FailSafeProtocol()

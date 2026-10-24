"""Mesh event bus topic hierarchy and domain/event-type validation."""

from __future__ import annotations

from enum import StrEnum


class MeshDomain(StrEnum):
    SENSOR = "sensor"
    VISION = "vision"
    MOTION = "motion"
    ACTUATOR = "actuator"
    SECURITY = "security"
    UI = "ui"


DOMAIN_EVENT_TYPES: dict[MeshDomain, frozenset[str]] = {
    MeshDomain.SENSOR: frozenset(
        {
            "reading_update",
            "threshold_exceeded",
            "calibration_needed",
            "battery_low",
        }
    ),
    MeshDomain.VISION: frozenset(
        {
            "image_captured",
            "motion_detected",
            "object_detected",
            "anomaly_detected",
        }
    ),
    MeshDomain.MOTION: frozenset(
        {
            "dispatch_requested",
            "flight_started",
            "waypoint_reached",
            "flight_completed",
            "rth_triggered",
        }
    ),
    MeshDomain.ACTUATOR: frozenset(
        {
            "command_sent",
            "state_changed",
            "tank_level_low",
        }
    ),
    MeshDomain.SECURITY: frozenset(
        {
            "intrusion_detected",
            "lock_engaged",
            "access_granted",
            "access_denied",
        }
    ),
    MeshDomain.UI: frozenset(
        {
            "alert_shown",
            "user_acknowledged",
            "user_action_triggered",
        }
    ),
}


def mesh_event_topic(tenant_id: str, domain: MeshDomain, event_type: str) -> str:
    return f"tenants/{tenant_id}/mesh/events/{domain.value}/{event_type}"


def mesh_tenant_fanout_channel(tenant_id: str) -> str:
    return f"mesh:tenant:{tenant_id}"


def validate_domain_event_type(domain: MeshDomain, event_type: str) -> bool:
    allowed = DOMAIN_EVENT_TYPES.get(domain)
    if allowed is None:
        return False
    return event_type in allowed

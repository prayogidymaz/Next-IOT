"""Route detection confidence to mesh actions."""

from __future__ import annotations

import uuid

from app.vision.schemas import DetectionResult, RoutingAction, RoutingDecision


class ConfidenceRouter:
    def route(self, result: DetectionResult, device_id: uuid.UUID, tenant_id: uuid.UUID) -> RoutingDecision:
        _ = device_id, tenant_id
        confidence = result.max_confidence
        if confidence >= 0.85 and result.species_guess != "none":
            return RoutingDecision(
                action=RoutingAction.AUTO_TRIGGER,
                severity="high",
                workflow_name="pest_response",
                message="Auto-trigger pest_response workflow (drone dispatch + farmer notification).",
            )
        if confidence >= 0.6:
            return RoutingDecision(
                action=RoutingAction.HUMAN_REVIEW,
                severity="medium",
                workflow_name=None,
                message="Verify pest detection — human review requested.",
            )
        return RoutingDecision(
            action=RoutingAction.LOG_ONLY,
            severity="low",
            workflow_name=None,
            message="Logged vision detection below review threshold.",
        )

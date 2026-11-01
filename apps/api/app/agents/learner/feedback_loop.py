"""Collect feedback and train lightweight alert prioritization model."""

from __future__ import annotations

import uuid
from enum import StrEnum

import numpy as np
from sklearn.linear_model import LogisticRegression
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.models import AgentActionFeedback
from app.types.json_types import JsonObject


class FeedbackType(StrEnum):
    ACKNOWLEDGED = "acknowledged"
    DISMISSED = "dismissed"
    ACTION_TAKEN = "action_taken"


class FeedbackLoop:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._model: LogisticRegression | None = None
        self._feature_rows: list[list[float]] = []
        self._labels: list[int] = []

    async def record_feedback(
        self,
        user_id: uuid.UUID,
        alert_id: uuid.UUID,
        feedback: FeedbackType,
        notes: str = "",
        features: JsonObject | None = None,
    ) -> AgentActionFeedback:
        row = AgentActionFeedback(
            user_id=user_id,
            alert_id=alert_id,
            feedback=feedback.value,
            notes=notes,
        )
        self._db.add(row)
        await self._db.flush()

        feat = features or {}
        vector = [
            float(feat.get("severity_score", 0)),
            float(feat.get("risk_score", 0)),
            float(feat.get("repeat_count", 0)),
        ]
        self._feature_rows.append(vector)
        self._labels.append(1 if feedback == FeedbackType.ACTION_TAKEN else 0)
        return row

    def retrain_weekly(self) -> bool:
        if len(self._feature_rows) < 8:
            return False
        x = np.array(self._feature_rows, dtype=float)
        y = np.array(self._labels, dtype=int)
        model = LogisticRegression(max_iter=200)
        model.fit(x, y)
        self._model = model
        return True

    def prioritize_alert(self, features: JsonObject) -> float:
        if self._model is None:
            severity = features.get("severity_score")
            return float(severity) if isinstance(severity, (int, float)) else 0.5
        vector = np.array(
            [
                [
                    float(features.get("severity_score", 0)),
                    float(features.get("risk_score", 0)),
                    float(features.get("repeat_count", 0)),
                ]
            ],
            dtype=float,
        )
        proba = self._model.predict_proba(vector)[0][1]
        return float(proba)

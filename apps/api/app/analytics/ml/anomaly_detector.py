"""Isolation Forest + z-score anomaly detection on sensor series."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from app.analytics.ml.schemas import Anomaly, AnomalySeverity

logger = logging.getLogger(__name__)


class AnomalyDetector:
    def __init__(self, z_sigma: float = 2.5) -> None:
        self._z_sigma = min(max(z_sigma, 2.5), 3.5)

    def detect(self, sensor_series: pd.DataFrame, device_id: uuid.UUID) -> list[Anomaly]:
        if sensor_series.empty or "value" not in sensor_series.columns:
            return []
        values = sensor_series["value"].astype(float).to_numpy()
        if len(values) < 8:
            return []
        metric = str(sensor_series["metric"].iloc[0]) if "metric" in sensor_series.columns else "value"
        mean = float(np.mean(values))
        std = float(np.std(values))
        if std < 1e-6:
            std = 1e-6
        from sklearn.ensemble import IsolationForest

        forest = IsolationForest(contamination=0.03, random_state=42)
        preds = forest.fit_predict(values.reshape(-1, 1))
        scores = -forest.score_samples(values.reshape(-1, 1))
        anomalies: list[Anomaly] = []
        now = datetime.now(tz=UTC)
        for idx, (val, pred, score) in enumerate(zip(values, preds, scores, strict=True)):
            z = abs(val - mean) / std
            if pred == -1 and z >= self._z_sigma:
                severity = _severity_from_z(z)
                low = mean - self._z_sigma * std
                high = mean + self._z_sigma * std
                ts = now
                if "recorded_at" in sensor_series.columns:
                    raw_ts = sensor_series["recorded_at"].iloc[idx]
                    if isinstance(raw_ts, datetime):
                        ts = raw_ts if raw_ts.tzinfo else raw_ts.replace(tzinfo=UTC)
                anomalies.append(
                    Anomaly(
                        device_id=device_id,
                        detected_at=ts,
                        metric=metric,
                        value=float(val),
                        expected_range=(low, high),
                        severity=severity.value,
                        score=float(score),
                    )
                )
        return anomalies


def _severity_from_z(z: float) -> AnomalySeverity:
    if z >= 4.0:
        return AnomalySeverity.HIGH
    if z >= 3.0:
        return AnomalySeverity.MEDIUM
    return AnomalySeverity.LOW

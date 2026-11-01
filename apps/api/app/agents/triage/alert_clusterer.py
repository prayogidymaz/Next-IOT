"""Cluster alerts to reduce fatigue."""

from __future__ import annotations

import math
from collections import defaultdict

from app.agents.triage.types import AlertCluster, AlertSnapshot


class AlertClusterer:
    def cluster(self, alerts: list[AlertSnapshot], time_window_minutes: int = 15) -> list[AlertCluster]:
        if not alerts:
            return []

        buckets: dict[str, list[AlertSnapshot]] = defaultdict(list)
        for alert in alerts:
            geo = self._geo_bucket(alert.lat, alert.lng)
            key = f"{alert.alarm_type}|{alert.metric or 'any'}|{geo}"
            buckets[key].append(alert)

        clusters: list[AlertCluster] = []
        for signature, group in buckets.items():
            clusters.append(
                AlertCluster(
                    signature=signature,
                    alerts=group,
                    risk_score=0.0,
                )
            )
        _ = time_window_minutes  # reserved for temporal splitting
        return clusters

    @staticmethod
    def _geo_bucket(lat: float | None, lng: float | None) -> str:
        if lat is None or lng is None:
            return "unknown"
        radius_m = 50.0
        lat_bucket = math.floor(lat * 111_000 / radius_m)
        lng_bucket = math.floor(lng * 111_000 * max(math.cos(math.radians(lat)), 0.1) / radius_m)
        return f"{lat_bucket}:{lng_bucket}"

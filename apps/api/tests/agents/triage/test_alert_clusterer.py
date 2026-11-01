"""Alert clusterer tests."""

from __future__ import annotations

import uuid

from app.agents.triage.alert_clusterer import AlertClusterer
from app.agents.triage.types import AlertSnapshot


def _alert(metric: str = "soil_moisture") -> AlertSnapshot:
    return AlertSnapshot(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        alarm_type="threshold",
        severity="warning",
        title="Soil low",
        device_id=uuid.uuid4(),
        lat=-6.2,
        lng=106.8,
        metric=metric,
    )


def test_cluster_empty() -> None:
    assert AlertClusterer().cluster([]) == []


def test_cluster_groups_same_metric() -> None:
    alerts = [_alert(), _alert(), _alert("temp")]
    clusters = AlertClusterer().cluster(alerts)
    assert len(clusters) >= 2


def test_cluster_signature_stable() -> None:
    alerts = [_alert(), _alert()]
    clusters = AlertClusterer().cluster(alerts)
    assert clusters[0].signature == clusters[0].signature


def test_geo_bucket_unknown_without_coords() -> None:
    alert = AlertSnapshot(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        alarm_type="x",
        severity="info",
        title="t",
        device_id=None,
        lat=None,
        lng=None,
        metric=None,
    )
    clusters = AlertClusterer().cluster([alert])
    assert "unknown" in clusters[0].signature


def test_cluster_alert_count_preserved() -> None:
    alerts = [_alert() for _ in range(5)]
    total = sum(len(c.alerts) for c in AlertClusterer().cluster(alerts))
    assert total == 5


def test_time_window_param_accepted() -> None:
    clusters = AlertClusterer().cluster([_alert()], time_window_minutes=30)
    assert len(clusters) == 1

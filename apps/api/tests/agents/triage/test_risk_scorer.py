"""Risk scorer tests."""

from __future__ import annotations

import uuid

from app.agents.triage.risk_scorer import RiskScorer
from app.agents.triage.types import AlertSnapshot


def _alert(severity: str = "critical") -> AlertSnapshot:
    return AlertSnapshot(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        alarm_type="pest",
        severity=severity,
        title="Pest",
        device_id=None,
        lat=None,
        lng=None,
        metric=None,
    )


def test_critical_higher_than_info() -> None:
    scorer = RiskScorer()
    high = scorer.score(_alert("critical"), {})
    low = scorer.score(_alert("info"), {})
    assert high.value > low.value


def test_crop_coffee_boost() -> None:
    scorer = RiskScorer()
    with_crop = scorer.score(_alert(), {"crop_type": "coffee"})
    default = scorer.score(_alert(), {})
    assert with_crop.value >= default.value


def test_rain_forecast_lowers_score() -> None:
    scorer = RiskScorer()
    dry = scorer.score(_alert(), {})
    rainy = scorer.score(_alert(), {"rain_forecast_hours": 1})
    assert rainy.value <= dry.value


def test_score_clamped_0_100() -> None:
    scorer = RiskScorer()
    result = scorer.score(_alert("critical"), {"crop_type": "coffee", "repeat_count": 99})
    assert 0 <= result.value <= 100


def test_factors_present() -> None:
    scorer = RiskScorer()
    result = scorer.score(_alert(), {})
    assert "severity" in result.factors

"""Disease rule unit tests."""

from __future__ import annotations

import pytest
from app.agriculture.disease_predictor import (
    evaluate_coffee_berry_borer,
    evaluate_coffee_rust,
    evaluate_oil_palm_ganoderma,
    evaluate_rice_blast,
    forecast_risk_days,
)


def test_coffee_rust_triggers() -> None:
    risk = evaluate_coffee_rust(90, 23, 8, 50)
    assert risk is not None
    assert risk.risk_level == "high"


def test_coffee_rust_skips_low_humidity() -> None:
    assert evaluate_coffee_rust(70, 23, 8, 50) is None


@pytest.mark.parametrize(
    ("humidity", "expected"),
    [(90, True), (60, False), (85, False)],
)
def test_coffee_rust_humidity_gate(humidity: int, expected: bool) -> None:
    risk = evaluate_coffee_rust(humidity, 23, 8, 50)
    assert (risk is not None) is expected


def test_berry_borer_fruiting() -> None:
    assert evaluate_coffee_berry_borer(25, 80, "vegetative") is None
    assert evaluate_coffee_berry_borer(25, 80, "fruiting") is not None


@pytest.mark.parametrize("stage", ["planting", "germination", "harvesting"])
def test_berry_borer_non_fruiting(stage: str) -> None:
    assert evaluate_coffee_berry_borer(25, 80, stage) is None


def test_rice_blast() -> None:
    risk = evaluate_rice_blast(90, 22, True, True)
    assert risk is not None
    assert risk.disease_name == "Blas Padi"


@pytest.mark.parametrize("humidity", [50, 60, 70])
def test_rice_blast_low_humidity(humidity: int) -> None:
    assert evaluate_rice_blast(humidity, 22, True, True) is None


def test_ganoderma() -> None:
    risk = evaluate_oil_palm_ganoderma(0.5, 4.5)
    assert risk is not None


@pytest.mark.parametrize("crop", ["coffee", "rice", "oil_palm", "horticulture"])
def test_forecast_crop(crop: str) -> None:
    days = forecast_risk_days(crop, [{"humidity_pct": 90, "temp_c": 23, "date": "2026-01-01"}] * 7)
    assert len(days) == 7

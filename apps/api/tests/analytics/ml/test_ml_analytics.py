"""ML analytics unit and API tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import numpy as np
import pandas as pd
import pytest
from httpx import AsyncClient

from app.analytics.ml.anomaly_detector import AnomalyDetector
from app.analytics.ml.cost_optimizer import CostOptimizer
from app.analytics.ml.yield_predictor import YieldPredictor, _synthetic_coffee_frame

PASSWORD = "SecurePass123!"


def test_yield_predictor_fits_and_predicts() -> None:
    frame = _synthetic_coffee_frame(120)
    predictor = YieldPredictor()
    model = predictor.fit(frame)
    assert model is not None
    forecast = predictor.predict(uuid.uuid4(), horizon_days=30)
    assert forecast.estimated_kg > 0
    assert forecast.confidence_interval[0] <= forecast.estimated_kg


def test_yield_predictor_mock_fallback() -> None:
    predictor = YieldPredictor()
    forecast = predictor.predict(uuid.uuid4(), horizon_days=14)
    assert forecast.model_version == "lr-v1"
    assert forecast.horizon_days == 14


def test_anomaly_detector_detects_spike() -> None:
    values = [10.0] * 20 + [100.0]
    frame = pd.DataFrame({"value": values, "metric": ["temp"] * len(values)})
    detector = AnomalyDetector(z_sigma=2.5)
    found = detector.detect(frame, uuid.uuid4())
    assert len(found) >= 1
    assert found[-1].value == 100.0


def test_anomaly_detector_ignores_normal() -> None:
    rng = np.random.default_rng(1)
    values = 20 + rng.normal(0, 0.5, 40)
    frame = pd.DataFrame({"value": values, "metric": ["temp"] * len(values)})
    detector = AnomalyDetector(z_sigma=3.5)
    found = detector.detect(frame, uuid.uuid4())
    assert len(found) == 0


def test_cost_optimizer_computes_savings() -> None:
    report = CostOptimizer().recommend(uuid.uuid4(), period_days=30)
    assert report.total_potential_saving_idr > 0
    assert report.water_liter_saved_idr > 0
    assert report.fertilizer_rec_kg >= 0


@pytest.mark.parametrize("period", [7, 14, 30, 60])
def test_cost_optimizer_periods(period: int) -> None:
    report = CostOptimizer().recommend(uuid.uuid4(), period_days=period)
    assert report.period_days == max(period, 7)


@pytest.mark.parametrize("horizon", [7, 30, 90])
def test_yield_horizons(horizon: int) -> None:
    forecast = YieldPredictor().predict(uuid.uuid4(), horizon_days=horizon)
    assert forecast.horizon_days == horizon


def test_anomaly_empty_series() -> None:
    frame = pd.DataFrame({"value": []})
    assert AnomalyDetector().detect(frame, uuid.uuid4()) == []


def test_anomaly_short_series() -> None:
    frame = pd.DataFrame({"value": [1.0, 2.0], "metric": ["x", "x"]})
    assert AnomalyDetector().detect(frame, uuid.uuid4()) == []


@pytest.mark.asyncio
async def test_endpoints_require_auth(client: AsyncClient) -> None:
    plot_id = str(uuid.uuid4())
    assert (await client.get(f"/api/v1/analytics/yield/forecast?plot_id={plot_id}")).status_code == 401
    assert (await client.get("/api/v1/analytics/anomalies")).status_code == 401
    assert (await client.get("/api/v1/analytics/optimization/report")).status_code == 401


async def _register(client: AsyncClient, slug: str, email: str) -> str:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "ML",
            "tenant_slug": slug,
            "email": email,
            "password": PASSWORD,
        },
    )
    return reg.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_yield_forecast_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _register(client, unique_slug, unique_email)
    plot_id = uuid.uuid4()
    resp = await client.get(
        f"/api/v1/analytics/yield/forecast?plot_id={plot_id}&horizon_days=30",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["estimated_kg"] > 0


@pytest.mark.asyncio
async def test_optimization_report_endpoint(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _register(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/analytics/optimization/report?period_days=30",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert float(resp.json()["total_potential_saving_idr"]) > 0


@pytest.mark.asyncio
async def test_anomalies_list_empty(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _register(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/analytics/anomalies",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_acknowledge_anomaly_404(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _register(client, unique_slug, unique_email)
    resp = await client.post(
        f"/api/v1/analytics/anomalies/{uuid.uuid4()}/acknowledge",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_anomaly_severity_levels() -> None:
    values = [10.0] * 30 + [50.0]
    frame = pd.DataFrame({"value": values, "metric": ["m"] * len(values)})
    found = AnomalyDetector(z_sigma=2.5).detect(frame, uuid.uuid4())
    assert found[0].severity in {"low", "medium", "high", "critical"}


def test_yield_training_frame_columns() -> None:
    frame = _synthetic_coffee_frame(10)
    assert "yield_kg" in frame.columns
    assert len(frame) == 10


@pytest.mark.parametrize("sigma", [2.5, 3.0, 3.5])
def test_anomaly_sigma_config(sigma: float) -> None:
    detector = AnomalyDetector(z_sigma=sigma)
    assert detector._z_sigma == sigma  # noqa: SLF001


def test_optimizer_recommendations_shape() -> None:
    report = CostOptimizer().recommend(uuid.uuid4(), 30)
    assert "irrigation" in report.recommendations
    assert "lighting" in report.recommendations


def test_anomaly_with_timestamps() -> None:
    now = datetime.now(tz=UTC)
    values = [1.0] * 15 + [99.0]
    frame = pd.DataFrame(
        {
            "value": values,
            "metric": ["v"] * len(values),
            "recorded_at": [now] * len(values),
        }
    )
    found = AnomalyDetector().detect(frame, uuid.uuid4())
    assert found[0].detected_at.tzinfo is not None

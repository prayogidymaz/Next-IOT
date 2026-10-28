"""Coffee yield forecasting with scikit-learn LinearRegression."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import numpy as np
import pandas as pd

from app.analytics.ml.schemas import YieldForecast

_MODEL_VERSION = "lr-v1"


class YieldPredictor:
    def __init__(self) -> None:
        self._model: object | None = None
        self._residual_std: float = 1.0

    def fit(self, historical_data: pd.DataFrame) -> object:
        from sklearn.linear_model import LinearRegression

        frame = _ensure_feature_columns(historical_data)
        features = frame[
            ["avg_soil_moisture", "avg_temp", "rainfall_mm", "ndvi", "days_since_planting"]
        ].to_numpy()
        target = frame["yield_kg"].to_numpy()
        model = LinearRegression()
        model.fit(features, target)
        preds = model.predict(features)
        residuals = target - preds
        self._residual_std = float(np.std(residuals)) if len(residuals) > 1 else 1.0
        self._model = model
        return model

    def predict(self, plot_id: uuid.UUID, horizon_days: int = 30) -> YieldForecast:
        if self._model is None:
            synthetic = _synthetic_coffee_frame(rows=max(horizon_days, 60))
            self.fit(synthetic)
        assert self._model is not None
        latest = _synthetic_coffee_frame(rows=1).iloc[0]
        horizon_factor = 1.0 + (horizon_days / 365.0) * 0.05
        features = np.array(
            [
                [
                    latest["avg_soil_moisture"],
                    latest["avg_temp"],
                    latest["rainfall_mm"],
                    latest["ndvi"],
                    latest["days_since_planting"] + horizon_days,
                ]
            ]
        )
        predict = self._model.predict
        estimated = float(predict(features)[0] * horizon_factor)
        margin = 1.96 * self._residual_std
        ci = (max(0.0, estimated - margin), estimated + margin)
        risks: list[str] = []
        if latest["avg_soil_moisture"] < 35:
            risks.append("low_soil_moisture")
        if latest["ndvi"] < 0.45:
            risks.append("vegetation_stress")
        if latest["rainfall_mm"] < 10:
            risks.append("drought_risk")
        return YieldForecast(
            plot_id=plot_id,
            horizon_days=horizon_days,
            estimated_kg=round(estimated, 2),
            confidence_interval=(round(ci[0], 2), round(ci[1], 2)),
            risk_factors=risks,
            model_version=_MODEL_VERSION,
            forecast_date=date.today() + timedelta(days=horizon_days),
        )


def _ensure_feature_columns(frame: pd.DataFrame) -> pd.DataFrame:
    required = ["avg_soil_moisture", "avg_temp", "rainfall_mm", "ndvi", "days_since_planting", "yield_kg"]
    if all(col in frame.columns for col in required):
        return frame
    return _synthetic_coffee_frame(rows=len(frame) if len(frame) > 0 else 90)


def _synthetic_coffee_frame(rows: int) -> pd.DataFrame:
    days = np.arange(rows)
    moisture = 55 + 10 * np.sin(days / 14.0) + np.random.default_rng(42).normal(0, 2, rows)
    temp = 24 + 3 * np.sin(days / 30.0)
    rain = 12 + 8 * np.abs(np.sin(days / 21.0))
    ndvi = 0.55 + 0.08 * np.sin(days / 45.0)
    dsp = days + 120
    yield_kg = 80 + moisture * 0.4 + ndvi * 120 - np.maximum(0, temp - 28) * 2 + rain * 0.2
    yield_kg += np.random.default_rng(7).normal(0, 3, rows)
    return pd.DataFrame(
        {
            "avg_soil_moisture": moisture,
            "avg_temp": temp,
            "rainfall_mm": rain,
            "ndvi": ndvi,
            "days_since_planting": dsp,
            "yield_kg": np.maximum(yield_kg, 10),
        }
    )

"""Score alert risk 0-100."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.agents.triage.types import AlertSnapshot, RiskScore
from app.types.json_types import JsonObject


class RiskScorer:
    _SEVERITY_WEIGHT = {
        "critical": 40.0,
        "major": 32.0,
        "minor": 20.0,
        "warning": 12.0,
        "info": 5.0,
    }

    _CROP_VALUE = {
        "coffee": 15.0,
        "vegetable": 8.0,
        "default": 10.0,
    }

    def score(self, alert: AlertSnapshot, context: JsonObject) -> RiskScore:
        severity_base = self._SEVERITY_WEIGHT.get(alert.severity.lower(), 10.0)
        crop_raw = context.get("crop_type")
        crop_key = str(crop_raw).lower() if isinstance(crop_raw, str) else "default"
        crop_factor = self._CROP_VALUE.get(crop_key, self._CROP_VALUE["default"])

        wib = datetime.now(tz=ZoneInfo("Asia/Jakarta"))
        time_factor = 12.0 if 6 <= wib.hour <= 9 else 4.0

        history_raw = context.get("repeat_count")
        history_factor = min(float(history_raw), 10.0) if isinstance(history_raw, (int, float)) else 0.0

        weather_raw = context.get("rain_forecast_hours")
        weather_factor = -8.0 if isinstance(weather_raw, (int, float)) and weather_raw <= 2 else 0.0

        total = severity_base + crop_factor + time_factor + history_factor + weather_factor
        clamped = max(0, min(100, int(round(total))))
        return RiskScore(
            value=clamped,
            factors={
                "severity": severity_base,
                "crop": crop_factor,
                "time_of_day": time_factor,
                "history": history_factor,
                "weather": weather_factor,
            },
        )

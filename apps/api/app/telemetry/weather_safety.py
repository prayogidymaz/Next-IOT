"""Flight safety evaluation from wind and precipitation thresholds."""

from __future__ import annotations

from enum import StrEnum

WIND_CAUTION_MIN_M_S = 10.0
WIND_NO_FLY_M_S = 15.0
RAIN_NO_FLY_MM_H = 10.0


class FlightSafetyStatus(StrEnum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    NO_FLY = "NO_FLY"


def evaluate_flight_safety(*, wind_speed_m_s: float, rain_rate_mm_h: float) -> FlightSafetyStatus:
    """Apply mission weather go/no-go rules."""
    if wind_speed_m_s > WIND_NO_FLY_M_S or rain_rate_mm_h > RAIN_NO_FLY_MM_H:
        return FlightSafetyStatus.NO_FLY
    if wind_speed_m_s >= WIND_CAUTION_MIN_M_S:
        return FlightSafetyStatus.CAUTION
    return FlightSafetyStatus.SAFE

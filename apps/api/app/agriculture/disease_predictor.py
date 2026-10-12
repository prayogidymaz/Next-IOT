"""Rule-based crop disease risk engine (ML-ready hooks later)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RiskLevel = Literal["low", "medium", "high", "critical"]


@dataclass(frozen=True)
class DiseaseRisk:
    disease_name: str
    risk_level: RiskLevel
    factors: dict[str, object]
    action_recommended: str


def evaluate_coffee_rust(
    humidity_pct: float,
    temp_c: float,
    leaf_wetness_hours: float,
    humid_hours_above_85: float,
) -> DiseaseRisk | None:
    if humid_hours_above_85 < 48 or humidity_pct <= 85:
        return None
    if not (21 <= temp_c <= 25):
        return None
    if leaf_wetness_hours < 6:
        return None
    return DiseaseRisk(
        disease_name="Karat Daun Kopi",
        risk_level="high",
        factors={
            "humidity_pct": humidity_pct,
            "temp_c": temp_c,
            "leaf_wetness_hours": leaf_wetness_hours,
            "humid_hours_above_85": humid_hours_above_85,
        },
        action_recommended="Semprot fungisida tembaga; kurangi kelembaban daun dengan pruning.",
    )


def evaluate_coffee_berry_borer(
    temp_c: float,
    humidity_pct: float,
    crop_stage: str,
) -> DiseaseRisk | None:
    if crop_stage != "fruiting":
        return None
    if not (20 <= temp_c <= 30):
        return None
    if not (70 <= humidity_pct <= 90):
        return None
    return DiseaseRisk(
        disease_name="Hama Penggerek Buah Kopi",
        risk_level="medium",
        factors={"temp_c": temp_c, "humidity_pct": humidity_pct, "stage": crop_stage},
        action_recommended="Panen rutin buah matang; perangkap feromon di blok berisiko.",
    )


def evaluate_rice_blast(
    humidity_pct: float,
    night_temp_c: float,
    light_rain: bool,
    nitrogen_high: bool,
) -> DiseaseRisk | None:
    if humidity_pct < 80 or not light_rain:
        return None
    if not (18 <= night_temp_c <= 25):
        return None
    level: RiskLevel = "high" if nitrogen_high else "medium"
    return DiseaseRisk(
        disease_name="Blas Padi",
        risk_level=level,
        factors={
            "humidity_pct": humidity_pct,
            "night_temp_c": night_temp_c,
            "light_rain": light_rain,
            "nitrogen_high": nitrogen_high,
        },
        action_recommended="Kurangi pupuk N; drainase sawah; fungicide sesuai rekomendasi penyuluh.",
    )


def evaluate_oil_palm_ganoderma(
    soil_moisture_variance: float,
    soil_ph: float,
) -> DiseaseRisk | None:
    if soil_moisture_variance < 0.15 and 5.5 <= soil_ph <= 6.5:
        return None
    return DiseaseRisk(
        disease_name="Ganoderma (Sawit)",
        risk_level="medium",
        factors={"soil_moisture_variance": soil_moisture_variance, "soil_ph": soil_ph},
        action_recommended="Monitor pangkal batang; sanitasi tunggul; jaga drainase konsisten.",
    )


def forecast_risk_days(
    crop_type: str,
    daily_conditions: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Seven-day outlook from simplified daily weather rows."""
    out: list[dict[str, object]] = []
    for idx, day in enumerate(daily_conditions[:7]):
        humidity = float(str(day.get("humidity_pct", 70)))
        temp = float(str(day.get("temp_c", 26)))
        level = "low"
        if crop_type == "coffee" and humidity > 88 and 21 <= temp <= 25:
            level = "high"
        elif crop_type == "rice" and humidity > 85:
            level = "medium"
        out.append({"day_index": idx, "risk_level": level, "date": day.get("date")})
    return out

"""CO2 coefficients and auto-calculation helpers."""

from __future__ import annotations

from decimal import Decimal

from app.types.json_types import JsonObject

KG_CO2_PER_KWH = Decimal("0.82")
KG_CO2_PER_LITER_DIESEL = Decimal("2.68")
KG_CO2_PER_KG_FERTILIZER = Decimal("5.2")
KG_CO2_PER_KM_TRANSPORT = Decimal("0.12")

COEFFICIENTS: dict[str, Decimal] = {
    "electricity": KG_CO2_PER_KWH,
    "fuel": KG_CO2_PER_LITER_DIESEL,
    "fertilizer": KG_CO2_PER_KG_FERTILIZER,
    "transport": KG_CO2_PER_KM_TRANSPORT,
}


def co2_from_source(source_type: str, amount: Decimal) -> Decimal:
    coeff = COEFFICIENTS.get(source_type, Decimal("1"))
    return (amount * coeff).quantize(Decimal("0.001"))


def co2_from_actuator_telemetry(payload: JsonObject) -> Decimal | None:
    """Estimate kWh from actuator runtime minutes in telemetry payload."""
    runtime = payload.get("runtime_minutes")
    power_kw = payload.get("power_kw")
    if not isinstance(runtime, (int, float)) or not isinstance(power_kw, (int, float)):
        return None
    kwh = Decimal(str(runtime)) / Decimal("60") * Decimal(str(power_kw))
    return co2_from_source("electricity", kwh)

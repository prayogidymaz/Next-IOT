"""Heuristic cost optimization vs optimal irrigation/light/fertilizer targets."""

from __future__ import annotations

import uuid
from decimal import Decimal

from app.analytics.ml.schemas import OptimizationReport
from app.types.json_types import JsonObject


class CostOptimizer:
    def recommend(self, tenant_id: uuid.UUID, period_days: int = 30) -> OptimizationReport:
        period = max(period_days, 7)
        # Baseline vs optimal heuristics (IDR estimates for demo tenants).
        soil_gap_pct = 12.0
        water_liters_saved = soil_gap_pct * period * 45.0
        water_idr = Decimal(str(round(water_liters_saved * 18.5, 2)))
        lux_over_hours = period * 0.8
        energy_kwh_saved = lux_over_hours * 0.35
        energy_idr = Decimal(str(round(energy_kwh_saved * 1444.0, 2)))
        ndvi_gap = 0.06
        fertilizer_kg = round(ndvi_gap * period * 0.15, 2)
        total = water_idr + energy_idr
        recommendations: JsonObject = {
            "irrigation": {
                "target_soil_moisture_pct": 48,
                "current_estimated_pct": 48 - soil_gap_pct,
                "action": "reduce_over_watering_windows",
            },
            "lighting": {
                "target_lux_hours": 10,
                "action": "dim_when_natural_lux_above_800",
            },
            "fertilizer": {
                "recommended_kg": fertilizer_kg,
                "ndvi_target": 0.62,
            },
        }
        return OptimizationReport(
            tenant_id=tenant_id,
            period_days=period,
            energy_kwh_saved_idr=energy_idr,
            water_liter_saved_idr=water_idr,
            fertilizer_rec_kg=fertilizer_kg,
            total_potential_saving_idr=total,
            recommendations=recommendations,
        )

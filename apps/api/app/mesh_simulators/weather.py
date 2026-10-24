"""Weather station sensor simulator."""

from __future__ import annotations

import random

from app.mesh.event_bus import MeshDomain
from app.mesh_simulators.base import MeshPublisher
from pydantic import JsonValue


class WeatherSimulator:
    def sample_metrics(self) -> dict[str, JsonValue]:
        return {
            "temperature": round(random.uniform(22.0, 32.0), 1),
            "humidity": round(random.uniform(60.0, 85.0), 1),
            "pressure_hpa": round(random.uniform(1005.0, 1018.0), 1),
        }

    async def publish_reading(self, publisher: MeshPublisher) -> None:
        await publisher.publish_mesh(
            MeshDomain.SENSOR,
            "reading_update",
            {"metrics": self.sample_metrics()},
        )

    async def publish_forecast(self, publisher: MeshPublisher, rain_probability: float) -> None:
        await publisher.publish_mesh(
            MeshDomain.SENSOR,
            "weather_forecast",
            {
                "forecast": "rain_likely",
                "rain_probability": rain_probability,
                "no_rain_forecast_24h": rain_probability < 0.7,
            },
        )

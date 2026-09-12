"""Ray-casting geofence breach detection for forbidden zones."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class GeofenceZoneSnapshot:
    id: str
    name: str
    polygon_coords: list[dict[str, float]]
    min_altitude: float
    max_altitude: float
    action_on_breach: str


@dataclass(frozen=True)
class GeofenceBreach:
    zone_id: str
    zone_name: str
    breach_type: str
    action_on_breach: str
    message: str
    metadata: dict[str, Any]


class GeofenceChecker:
    """Point-in-polygon (ray-casting) checker for forbidden geofence volumes."""

    def point_in_polygon(self, lat: float, lon: float, polygon: Sequence[dict[str, float]]) -> bool:
        if len(polygon) < 3:
            return False

        inside = False
        j = len(polygon) - 1
        for i in range(len(polygon)):
            yi = polygon[i]["lat"]
            xi = polygon[i]["lon"]
            yj = polygon[j]["lat"]
            xj = polygon[j]["lon"]

            intersects = ((yi > lat) != (yj > lat)) and (
                lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi
            )
            if intersects:
                inside = not inside
            j = i
        return inside

    def check_altitude_violation(
        self,
        altitude_m: float,
        *,
        min_altitude: float,
        max_altitude: float,
    ) -> bool:
        return altitude_m < min_altitude or altitude_m > max_altitude

    def check_position(
        self,
        lat: float,
        lon: float,
        altitude_m: float | None,
        zones: Sequence[GeofenceZoneSnapshot],
    ) -> list[GeofenceBreach]:
        breaches: list[GeofenceBreach] = []

        for zone in zones:
            inside = self.point_in_polygon(lat, lon, zone.polygon_coords)
            if not inside:
                continue

            altitude_violation = False
            if altitude_m is not None:
                altitude_violation = self.check_altitude_violation(
                    altitude_m,
                    min_altitude=zone.min_altitude,
                    max_altitude=zone.max_altitude,
                )

            if altitude_m is None or (zone.min_altitude <= altitude_m <= zone.max_altitude):
                breach_type = "geofence_breach"
                message = f"Drone entered forbidden zone '{zone.name}'"
            elif altitude_violation:
                breach_type = "altitude_violation"
                message = (
                    f"Altitude {altitude_m:.1f} m violates zone '{zone.name}' "
                    f"limits ({zone.min_altitude:.0f}-{zone.max_altitude:.0f} m)"
                )
            else:
                continue

            breaches.append(
                GeofenceBreach(
                    zone_id=zone.id,
                    zone_name=zone.name,
                    breach_type=breach_type,
                    action_on_breach=zone.action_on_breach,
                    message=message,
                    metadata={
                        "zone_id": zone.id,
                        "zone_name": zone.name,
                        "breach_type": breach_type,
                        "action_on_breach": zone.action_on_breach,
                        "lat": lat,
                        "lon": lon,
                        "altitude_m": altitude_m,
                        "min_altitude": zone.min_altitude,
                        "max_altitude": zone.max_altitude,
                    },
                )
            )

        return breaches

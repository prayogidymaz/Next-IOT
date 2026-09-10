"""GPS path interpolation for simulated drone flight."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, degrees, radians, sin, sqrt


@dataclass(frozen=True)
class GeoPoint:
    latitude: float
    longitude: float
    altitude_m: float


def _haversine_m(a: GeoPoint, b: GeoPoint) -> float:
    r = 6_371_000.0
    lat1, lon1 = radians(a.latitude), radians(a.longitude)
    lat2, lon2 = radians(b.latitude), radians(b.longitude)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(h), sqrt(1 - h))


def _bearing_deg(a: GeoPoint, b: GeoPoint) -> float:
    lat1, lon1 = radians(a.latitude), radians(a.longitude)
    lat2, lon2 = radians(b.latitude), radians(b.longitude)
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    return (degrees(atan2(x, y)) + 360) % 360


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def steps_for_segment(start: GeoPoint, end: GeoPoint, *, min_steps: int = 5, max_steps: int = 20) -> int:
    distance = _haversine_m(start, end)
    # ~10 m/s simulated speed → one step per second
    steps = max(min_steps, int(distance / 10))
    return min(max_steps, steps)


def interpolate_segment(start: GeoPoint, end: GeoPoint, steps: int) -> list[GeoPoint]:
    if steps <= 0:
        return [end]
    points: list[GeoPoint] = []
    for i in range(1, steps + 1):
        t = i / steps
        points.append(
            GeoPoint(
                latitude=_lerp(start.latitude, end.latitude, t),
                longitude=_lerp(start.longitude, end.longitude, t),
                altitude_m=_lerp(start.altitude_m, end.altitude_m, t),
            )
        )
    return points


def build_mission_path(
    origin: GeoPoint,
    waypoints: list[tuple[float, float]],
    *,
    cruise_altitude_m: float,
    min_steps: int = 5,
    max_steps: int = 20,
) -> list[GeoPoint]:
    """Build a full flight path from origin through each waypoint at cruise altitude."""
    if not waypoints:
        return [origin]

    path: list[GeoPoint] = []
    current = origin

    for lat, lon in waypoints:
        target = GeoPoint(latitude=lat, longitude=lon, altitude_m=cruise_altitude_m)
        steps = steps_for_segment(current, target, min_steps=min_steps, max_steps=max_steps)
        segment = interpolate_segment(current, target, steps)
        path.extend(segment)
        current = target

    return path


def segment_speed_mps(start: GeoPoint, end: GeoPoint, duration_s: float = 1.0) -> float:
    if duration_s <= 0:
        return 0.0
    return _haversine_m(start, end) / duration_s


def heading_to(end: GeoPoint, start: GeoPoint) -> float:
    return _bearing_deg(start, end)

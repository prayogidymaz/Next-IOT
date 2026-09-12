"""Dynamic SAR search grid generator — Expanding Square & Parallel Track patterns."""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Any

METERS_PER_DEG_LAT = 111_320.0


class SarGridPattern(StrEnum):
    EXPANDING_SQUARE = "expanding_square"
    PARALLEL_TRACK = "parallel_track"


class SarGridService:
    """Compute SAR search grids from LKP (Last Known Position) and search radius."""

    def generate(
        self,
        *,
        lkp_lat: float,
        lkp_lon: float,
        radius_m: float,
        pattern: SarGridPattern | str = SarGridPattern.EXPANDING_SQUARE,
        leg_spacing_m: float = 100.0,
    ) -> dict[str, Any]:
        if radius_m <= 0:
            raise ValueError("radius_m must be positive")
        if leg_spacing_m <= 0:
            raise ValueError("leg_spacing_m must be positive")

        pattern_value = SarGridPattern(pattern)

        if pattern_value == SarGridPattern.EXPANDING_SQUARE:
            waypoints, tracks = self._expanding_square(lkp_lat, lkp_lon, radius_m, leg_spacing_m)
        else:
            waypoints, tracks = self._parallel_track(lkp_lat, lkp_lon, radius_m, leg_spacing_m)

        search_areas = [
            {
                "label": "search_boundary",
                "points": self._square_polygon(lkp_lat, lkp_lon, radius_m),
            }
        ]

        return {
            "pattern": pattern_value.value,
            "lkp": {"lat": round(lkp_lat, 7), "lon": round(lkp_lon, 7)},
            "radius_m": radius_m,
            "leg_spacing_m": leg_spacing_m,
            "waypoint_count": len(waypoints),
            "waypoints": waypoints,
            "tracks": tracks,
            "search_areas": search_areas,
        }

    def _offset(self, lat: float, lon: float, north_m: float, east_m: float) -> tuple[float, float]:
        dlat = north_m / METERS_PER_DEG_LAT
        cos_lat = math.cos(math.radians(lat))
        dlon = east_m / (METERS_PER_DEG_LAT * cos_lat) if cos_lat else 0.0
        return lat + dlat, lon + dlon

    def _distance_m(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        north_m = (lat2 - lat1) * METERS_PER_DEG_LAT
        east_m = (lon2 - lon1) * METERS_PER_DEG_LAT * math.cos(math.radians((lat1 + lat2) / 2))
        return math.hypot(north_m, east_m)

    def _square_polygon(self, center_lat: float, center_lon: float, radius_m: float) -> list[dict[str, float]]:
        corners = [
            self._offset(center_lat, center_lon, -radius_m, -radius_m),
            self._offset(center_lat, center_lon, -radius_m, radius_m),
            self._offset(center_lat, center_lon, radius_m, radius_m),
            self._offset(center_lat, center_lon, radius_m, -radius_m),
        ]
        return [{"lat": round(lat, 7), "lon": round(lon, 7)} for lat, lon in corners]

    def _expanding_square(
        self,
        center_lat: float,
        center_lon: float,
        radius_m: float,
        leg_spacing_m: float,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        lat, lon = center_lat, center_lon
        waypoints: list[dict[str, Any]] = [
            {"sequence": 1, "lat": round(lat, 7), "lon": round(lon, 7), "label": "LKP"},
        ]
        track_points: list[dict[str, float]] = [{"lat": round(lat, 7), "lon": round(lon, 7)}]

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        leg_index = 0
        max_legs = 200

        while leg_index < max_legs:
            leg_number = (leg_index // 2) + 1
            leg_length = leg_number * leg_spacing_m
            d_n, d_e = directions[leg_index % 4]

            next_lat, next_lon = self._offset(lat, lon, d_n * leg_length, d_e * leg_length)
            dist = self._distance_m(center_lat, center_lon, next_lat, next_lon)

            if dist > radius_m and leg_index >= 4:
                break

            lat, lon = next_lat, next_lon
            track_points.append({"lat": round(lat, 7), "lon": round(lon, 7)})
            waypoints.append(
                {
                    "sequence": len(waypoints) + 1,
                    "lat": round(lat, 7),
                    "lon": round(lon, 7),
                }
            )
            leg_index += 1

            if dist >= radius_m:
                break

        tracks = [{"track_index": 1, "points": track_points}]
        return waypoints, tracks

    def _parallel_track(
        self,
        center_lat: float,
        center_lon: float,
        radius_m: float,
        track_spacing_m: float,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        waypoints: list[dict[str, Any]] = [
            {"sequence": 1, "lat": round(center_lat, 7), "lon": round(center_lon, 7), "label": "LKP"},
        ]
        tracks: list[dict[str, Any]] = []
        seq = 2
        track_index = 0
        north = -radius_m

        while north <= radius_m:
            if track_index % 2 == 0:
                start_east, end_east = -radius_m, radius_m
            else:
                start_east, end_east = radius_m, -radius_m

            start_lat, start_lon = self._offset(center_lat, center_lon, north, start_east)
            end_lat, end_lon = self._offset(center_lat, center_lon, north, end_east)

            track_points = [
                {"lat": round(start_lat, 7), "lon": round(start_lon, 7)},
                {"lat": round(end_lat, 7), "lon": round(end_lon, 7)},
            ]
            tracks.append({"track_index": track_index + 1, "points": track_points})

            for point in track_points:
                waypoints.append({"sequence": seq, "lat": point["lat"], "lon": point["lon"]})
                seq += 1

            north += track_spacing_m
            track_index += 1

        return waypoints, tracks

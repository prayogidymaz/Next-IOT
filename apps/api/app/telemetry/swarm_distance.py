"""Swarm distance matrix and collision-risk detection for multi-drone coordination."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

COLLISION_RISK_THRESHOLD_M = 20.0
COLLISION_RISK_WARNING = "COLLISION_RISK_WARNING"
METERS_PER_DEG_LAT = 111_320.0


@dataclass(frozen=True)
class SwarmNode:
    device_id: str
    lat: float
    lon: float
    alt: float | None = None


@dataclass(frozen=True)
class SwarmLink:
    device_a_id: str
    device_b_id: str
    distance_m: float
    collision_risk: bool
    warning: str | None = None


class SwarmDistanceCalculator:
    """Compute pairwise distances between concurrently active drone nodes."""

    def __init__(self, collision_threshold_m: float = COLLISION_RISK_THRESHOLD_M) -> None:
        self.collision_threshold_m = collision_threshold_m

    @staticmethod
    def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        north_m = (lat2 - lat1) * METERS_PER_DEG_LAT
        cos_lat = math.cos(math.radians((lat1 + lat2) / 2))
        east_m = (lon2 - lon1) * METERS_PER_DEG_LAT * cos_lat if cos_lat else 0.0
        return math.hypot(north_m, east_m)

    def compute_links(self, nodes: list[SwarmNode]) -> list[SwarmLink]:
        links: list[SwarmLink] = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                a, b = nodes[i], nodes[j]
                distance = self.haversine_m(a.lat, a.lon, b.lat, b.lon)
                collision_risk = distance < self.collision_threshold_m
                links.append(
                    SwarmLink(
                        device_a_id=a.device_id,
                        device_b_id=b.device_id,
                        distance_m=round(distance, 2),
                        collision_risk=collision_risk,
                        warning=COLLISION_RISK_WARNING if collision_risk else None,
                    )
                )
        return links

    def compute_matrix(self, nodes: list[SwarmNode]) -> dict[str, Any]:
        links = self.compute_links(nodes)
        return {
            "node_count": len(nodes),
            "link_count": len(links),
            "collision_threshold_m": self.collision_threshold_m,
            "has_collision_risk": any(link.collision_risk for link in links),
            "links": [
                {
                    "device_a_id": link.device_a_id,
                    "device_b_id": link.device_b_id,
                    "distance_m": link.distance_m,
                    "collision_risk": link.collision_risk,
                    "warning": link.warning,
                }
                for link in links
            ],
        }

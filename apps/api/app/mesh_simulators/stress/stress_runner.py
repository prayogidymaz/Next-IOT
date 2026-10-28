"""Spawn simulated mesh devices under load."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field


@dataclass(slots=True)
class StressMetrics:
    messages_sent: int = 0
    messages_dropped: int = 0
    latencies_ms: list[float] = field(default_factory=list)

    @property
    def msg_per_sec(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return self.messages_sent / max(1.0, sum(self.latencies_ms) / 1000.0)

    def percentile(self, pct: float) -> float:
        if not self.latencies_ms:
            return 0.0
        ordered = sorted(self.latencies_ms)
        idx = int(min(len(ordered) - 1, max(0, round((pct / 100.0) * (len(ordered) - 1)))))
        return ordered[idx]


@dataclass(slots=True)
class SimDevice:
    device_id: uuid.UUID
    device_type: str
    interval_ms: int


class StressRunner:
    def __init__(self) -> None:
        self.metrics = StressMetrics()
        self.devices: list[SimDevice] = []

    def spawn_devices(self, count: int, device_type: str, interval_ms: int) -> list[SimDevice]:
        spawned: list[SimDevice] = []
        for _ in range(count):
            jitter = interval_ms + random.randint(-500, 500)
            device = SimDevice(device_id=uuid.uuid4(), device_type=device_type, interval_ms=max(100, jitter))
            spawned.append(device)
        self.devices.extend(spawned)
        return spawned

    def bootstrap_default_mesh(self) -> dict[str, int]:
        counts = {
            "soil_sensor": self.spawn_devices(100, "soil_sensor", 10_000),
            "camera": self.spawn_devices(50, "camera", 90_000),
            "drone": self.spawn_devices(20, "drone", 30_000),
            "actuator": self.spawn_devices(10, "actuator", 15_000),
        }
        return {key: len(value) for key, value in counts.items()}

    def record_message(self, latency_ms: float, dropped: bool = False) -> None:
        if dropped:
            self.metrics.messages_dropped += 1
            return
        self.metrics.messages_sent += 1
        self.metrics.latencies_ms.append(latency_ms)

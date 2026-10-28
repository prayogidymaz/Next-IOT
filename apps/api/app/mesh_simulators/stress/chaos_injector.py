"""Chaos injection helpers for mesh stress tests."""

from __future__ import annotations

import random
import time


class ChaosInjector:
    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self.broker_disconnected = False

    def packet_loss(self, rate: float = 0.05) -> bool:
        return self._rng.random() < rate

    def network_latency(self, min_ms: int, max_ms: int) -> float:
        delay = self._rng.randint(min_ms, max_ms)
        time.sleep(delay / 1000.0)
        return float(delay)

    def broker_disconnect(self, duration_s: int) -> None:
        self.broker_disconnected = True
        time.sleep(duration_s)
        self.broker_disconnected = False

    def device_crash(self, devices: list[object], count: int) -> list[object]:
        if count <= 0 or not devices:
            return devices
        victims = self._rng.sample(devices, k=min(count, len(devices)))
        remaining = [device for device in devices if device not in victims]
        return remaining + victims

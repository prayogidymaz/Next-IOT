"""Pre-built auto-response chain templates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Awaitable

from app.types.json_types import JsonObject


@dataclass(frozen=True)
class ChainStep:
    step_id: str
    description: str
    handler_key: str


@dataclass(frozen=True)
class ChainTemplate:
    chain_id: str
    description: str
    steps: tuple[ChainStep, ...]


PEST_RESPONSE_CHAIN = ChainTemplate(
    chain_id="pest_response",
    description="Pest detected → spray → notify → follow-up vision",
    steps=(
        ChainStep("detect", "Vision detection severity > 0.8", "vision.detect"),
        ChainStep("spray", "Actuator sprayer 15s", "actuator.spray"),
        ChainStep("notify_farmer", "WA + push + watch haptic", "notify.multi"),
        ChainStep("wait_24h", "Wait 24h", "flow.wait"),
        ChainStep("verify_vision_followup", "Drone re-check", "vision.followup"),
        ChainStep("report_outcome", "Log success/failure", "report.outcome"),
    ),
)

IRRIGATION_SMART_CHAIN = ChainTemplate(
    chain_id="irrigation_smart",
    description="Soil low → weather check → valve → monitor → savings",
    steps=(
        ChainStep("trigger", "Soil moisture < 40%", "sensor.threshold"),
        ChainStep("check_weather", "Skip if rain in 2h", "weather.check"),
        ChainStep("open_valve", "Open valve by deficit", "actuator.valve"),
        ChainStep("monitor_live", "Poll soil every 2min", "sensor.poll"),
        ChainStep("close_when_optimal", "Close at 65% or 30min", "actuator.close"),
        ChainStep("log_savings", "Log liters + cost", "analytics.savings"),
    ),
)

DEVICE_HEALTH_CHAIN = ChainTemplate(
    chain_id="device_health",
    description="Offline device recovery chain",
    steps=(
        ChainStep("detect_offline", "No telemetry 60min", "health.detect"),
        ChainStep("ping_device", "MQTT ping", "mqtt.ping"),
        ChainStep("try_restart", "OTA restart command", "ota.restart"),
        ChainStep("escalate_if_fail", "Notify admin + ticket", "escalate.ticket"),
    ),
)

CHAIN_REGISTRY: dict[str, ChainTemplate] = {
    PEST_RESPONSE_CHAIN.chain_id: PEST_RESPONSE_CHAIN,
    IRRIGATION_SMART_CHAIN.chain_id: IRRIGATION_SMART_CHAIN,
    DEVICE_HEALTH_CHAIN.chain_id: DEVICE_HEALTH_CHAIN,
}

StepHandler = Callable[[JsonObject], Awaitable[JsonObject]]

"""CLI entrypoint for mesh device simulators."""

from __future__ import annotations

import asyncio
import os
import sys

from app.mesh.event_bus import MeshDomain
from app.mesh_simulators.base import MeshPublisher, SimulatorEnv
from app.mesh_simulators.cctv import CctvSimulator, run_tick
from app.mesh_simulators.cyberdeck import CyberdeckSimulator
from app.mesh_simulators.gate import GateSimulator
from app.mesh_simulators.runtime import run_mqtt_loop
from app.mesh_simulators.smartwatch import SmartwatchSimulator
from app.mesh_simulators.sprayer import SprayerSimulator
from app.mesh_simulators.weather import WeatherSimulator
from pydantic import JsonValue

CommandResult = dict[str, JsonValue]


async def _noop(_publisher: MeshPublisher) -> None:
    return None


async def _sprayer_tick(publisher: MeshPublisher) -> None:
    sim = SprayerSimulator()
    await publisher.publish_mesh(
        MeshDomain.ACTUATOR,
        "state_changed",
        {"tank_level_percent": sim.tank_percent, "valve_open": sim.valve_open},
    )


async def run_cctv(env: SimulatorEnv) -> None:
    sim = CctvSimulator(env)
    publisher_ref: list[MeshPublisher] = []
    http_port = int(os.environ.get("SIMULATOR_HTTP_PORT", "0"))

    async def on_command(
        _publisher: MeshPublisher,
        command_type: str,
        params: CommandResult,
    ) -> CommandResult:
        return await sim.handle_command(command_type, params)

    async def on_publisher_ready(publisher: MeshPublisher) -> None:
        publisher_ref.clear()
        publisher_ref.append(publisher)
        if http_port <= 0:
            return
        from app.mesh_simulators.http_sidecar import build_cctv_http_app, run_http_sidecar

        app = build_cctv_http_app(env, sim, publisher_ref)
        env_with_port = SimulatorEnv(
            tenant_id=env.tenant_id,
            device_id=env.device_id,
            mqtt_broker=env.mqtt_broker,
            mqtt_port=env.mqtt_port,
            mqtt_username=env.mqtt_username,
            mqtt_password=env.mqtt_password,
            emit_interval_seconds=env.emit_interval_seconds,
            http_port=http_port,
        )
        asyncio.create_task(run_http_sidecar(env_with_port, app))

    await run_mqtt_loop(
        env,
        on_tick=lambda publisher: run_tick(publisher, sim),
        on_command=on_command,
        on_publisher_ready=on_publisher_ready,
    )


async def run_sprayer(env: SimulatorEnv) -> None:
    sim = SprayerSimulator()

    async def on_command(
        publisher: MeshPublisher,
        command_type: str,
        params: CommandResult,
    ) -> CommandResult:
        return await sim.handle_command(publisher, command_type, params)

    await run_mqtt_loop(env, on_tick=_sprayer_tick, on_command=on_command)


async def run_gate(env: SimulatorEnv) -> None:
    sim = GateSimulator()

    async def on_command(
        publisher: MeshPublisher,
        command_type: str,
        params: CommandResult,
    ) -> CommandResult:
        return await sim.handle_command(publisher, command_type, params)

    await run_mqtt_loop(env, on_tick=_noop, on_command=on_command)


async def run_cyberdeck(env: SimulatorEnv) -> None:
    sim = CyberdeckSimulator()

    async def on_command(
        publisher: MeshPublisher,
        command_type: str,
        params: CommandResult,
    ) -> CommandResult:
        return await sim.handle_command(publisher, command_type, params)

    await run_mqtt_loop(
        env,
        on_tick=lambda publisher: sim.publish_alert_shown(publisher, "heartbeat"),
        on_command=on_command,
    )


async def run_weather(env: SimulatorEnv) -> None:
    weather = WeatherSimulator()

    async def on_command(
        _publisher: MeshPublisher,
        _command_type: str,
        _params: CommandResult,
    ) -> CommandResult:
        return {"ok": True}

    await run_mqtt_loop(
        env,
        on_tick=lambda publisher: weather.publish_reading(publisher),
        on_command=on_command,
    )


async def run_smartwatch(env: SimulatorEnv) -> None:
    watch = SmartwatchSimulator()

    async def on_command(
        _publisher: MeshPublisher,
        command_type: str,
        params: CommandResult,
    ) -> CommandResult:
        return await watch.handle_command(command_type, params)

    await run_mqtt_loop(env, on_tick=_noop, on_command=on_command)


async def _run(name: str, env: SimulatorEnv) -> None:
    runners = {
        "cctv": run_cctv,
        "sprayer": run_sprayer,
        "gate": run_gate,
        "cyberdeck": run_cyberdeck,
        "weather": run_weather,
        "smartwatch": run_smartwatch,
    }
    runner = runners.get(name)
    if runner is None:
        raise SystemExit(f"Unknown simulator: {name}")
    await runner(env)


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    env = SimulatorEnv.from_os()
    asyncio.run(_run(name, env))


if __name__ == "__main__":
    main()

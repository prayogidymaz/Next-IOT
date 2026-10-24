"""Async MQTT runtime for mesh simulators."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import Awaitable, Callable

import aiomqtt
from app.mesh_simulators.base import MqttMeshPublisher, SimulatorEnv, command_topic
from pydantic import JsonValue

logger = logging.getLogger(__name__)

TickHandler = Callable[[MqttMeshPublisher], Awaitable[None]]
CommandHandler = Callable[[MqttMeshPublisher, str, dict[str, JsonValue]], Awaitable[dict[str, JsonValue]]]


async def run_mqtt_loop(
    env: SimulatorEnv,
    *,
    on_tick: TickHandler,
    on_command: CommandHandler,
) -> None:
    async with aiomqtt.Client(
        hostname=env.mqtt_broker,
        port=env.mqtt_port,
        username=env.mqtt_username or None,
        password=env.mqtt_password or None,
    ) as client:
        publisher = MqttMeshPublisher(env, client)
        cmd_topic = command_topic(env.tenant_id, env.device_id)
        await client.subscribe(cmd_topic)

        async def _command_loop() -> None:
            async for message in client.messages:
                if str(message.topic) != cmd_topic:
                    continue
                raw = message.payload
                text = raw.decode() if isinstance(raw, bytes) else str(raw)
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload, dict):
                    continue
                command_type = str(payload.get("command_type", ""))
                params_raw = payload.get("params")
                inner_raw = payload.get("payload")
                params: dict[str, JsonValue] = {}
                if isinstance(params_raw, dict):
                    params = dict(params_raw)
                elif isinstance(inner_raw, dict):
                    params = dict(inner_raw)
                await on_command(publisher, command_type, params)

        command_task = asyncio.create_task(_command_loop())
        try:
            while True:
                await on_tick(publisher)
                await asyncio.sleep(env.emit_interval_seconds)
        finally:
            command_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await command_task

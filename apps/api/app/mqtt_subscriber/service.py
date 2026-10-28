"""aiomqtt 2.x subscriber — telemetry, client attributes, and RPC responses."""

from __future__ import annotations

import asyncio
import logging
import os
import socket

import aiomqtt
from pydantic import JsonValue

from app.attributes.client_ingest import persist_client_attributes_from_mqtt
from app.attributes.mqtt_topics import parse_client_attributes_topic
from app.config import settings
from app.database import async_session
from app.mesh.mqtt_ingest import ingest_mesh_event_from_mqtt
from app.mqtt_auth.subscriber_auth import (
    SUBSCRIBER_ATTRIBUTES_SHARE_FILTER,
    SUBSCRIBER_RPC_RESPONSE_SHARE_FILTER,
    SUBSCRIBER_TELEMETRY_SHARE_FILTER,
)
from app.mqtt_subscriber.schemas import TelemetryMqttTopic
from app.mqtt_subscriber.telemetry_ingest import persist_telemetry_from_mqtt
from app.rpc.mqtt_topics import parse_rpc_response_topic
from app.rpc.response_ingest import handle_rpc_response_from_mqtt
from app.rules.attribute_event import AttributeChangeEvent
from app.rules.executor import RuleExecutor
from app.rules.hooks import apply_attribute_change_rules, apply_telemetry_rules
from app.rules.telemetry_event import TelemetryRuleEvent
from app.telemetry.mqtt_payload import parse_telemetry_payload_bytes
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)

TELEMETRY_SUBSCRIBE_FILTER = "tenants/+/devices/+/telemetry"
ATTRIBUTES_SUBSCRIBE_FILTER = "tenants/+/devices/+/attributes"
RPC_RESPONSE_SUBSCRIBE_FILTER = "tenants/+/devices/+/commands/+/response"
MESH_EVENTS_SUBSCRIBE_FILTER = "tenants/+/mesh/events/#"


def _mqtt_client_identifier() -> str:
    return f"next-iot-subscriber-{socket.gethostname()}-{os.getpid()}"


def _message_payload_bytes(payload: object) -> bytes | None:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, bytearray):
        return bytes(payload)
    if isinstance(payload, str):
        return payload.encode("utf-8")
    return None


class MqttSubscriberService:
    def __init__(self, redis: RedisClient, rule_executor: RuleExecutor | None = None) -> None:
        self._redis = redis
        self._rule_executor = rule_executor
        self._stopping = False

    async def _run_telemetry_rules_after_commit(self, event: TelemetryRuleEvent) -> None:
        if self._rule_executor is None:
            logger.warning("Rule executor missing; skipping telemetry rules for device=%s", event.device_id)
            return
        async with async_session() as db:
            try:
                await apply_telemetry_rules(
                    self._rule_executor,
                    db,
                    tenant_id=event.tenant_id,
                    device_id=event.device_id,
                    metrics=event.metrics,
                    recorded_at=event.recorded_at,
                    reading_id=event.reading_id,
                )
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("Rule executor batch failed after telemetry persist device=%s", event.device_id)

    def request_stop(self) -> None:
        self._stopping = True

    async def _handle_telemetry(self, message: aiomqtt.Message, topic_str: str) -> None:
        try:
            parsed_topic = TelemetryMqttTopic.from_mqtt_topic(topic_str)
        except ValueError:
            logger.warning("MQTT Subscriber ignored telemetry topic: %s", topic_str)
            return

        payload_bytes = _message_payload_bytes(message.payload)
        if payload_bytes is None:
            logger.warning("MQTT Subscriber non-bytes payload on %s", topic_str)
            return

        try:
            payload_obj: dict[str, JsonValue] = parse_telemetry_payload_bytes(payload_bytes)
        except Exception as exc:
            logger.warning("MQTT Subscriber invalid payload on %s: %s", topic_str, exc)
            return

        if not payload_obj:
            logger.warning("MQTT Subscriber empty payload on %s", topic_str)
            return

        values = payload_obj.get("values")
        temp_log = values.get("temperature") if isinstance(values, dict) else None
        logger.warning(
            "Telemetry received: tenant=%s device=%s temp=%s",
            parsed_topic.tenant_id,
            parsed_topic.device_id,
            temp_log,
        )

        async with async_session() as db:
            try:
                result = await persist_telemetry_from_mqtt(
                    db,
                    self._redis,
                    topic=parsed_topic,
                    payload_obj=payload_obj,
                    client_id=_mqtt_client_identifier(),
                )
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("MQTT Subscriber persist failed on %s", topic_str)
                return

        rule_event_raw = result.get("rule_event")
        if isinstance(rule_event_raw, TelemetryRuleEvent):
            await self._run_telemetry_rules_after_commit(rule_event_raw)

        logger.warning(
            "MQTT Subscriber persisted: device=%s accepted=%s rejected=%s",
            parsed_topic.device_id,
            result.get("accepted_count", 0),
            result.get("rejected", []),
        )

    async def _handle_client_attributes(self, message: aiomqtt.Message, topic_str: str) -> None:
        parsed = parse_client_attributes_topic(topic_str)
        if parsed is None:
            logger.warning("MQTT Subscriber ignored attributes topic: %s", topic_str)
            return
        tenant_id, device_id = parsed
        payload_bytes = _message_payload_bytes(message.payload)
        if payload_bytes is None:
            return
        try:
            payload_obj: dict[str, JsonValue] = parse_telemetry_payload_bytes(payload_bytes)
        except Exception as exc:
            logger.warning("MQTT Subscriber invalid attributes payload on %s: %s", topic_str, exc)
            return

        attr_changes: list[AttributeChangeEvent] = []
        async with async_session() as db:
            try:
                count, attr_changes = await persist_client_attributes_from_mqtt(
                    db,
                    tenant_id=tenant_id,
                    device_id=device_id,
                    payload=payload_obj,
                )
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("MQTT Subscriber client attributes failed on %s", topic_str)
                return
        if self._rule_executor is not None and attr_changes:
            async with async_session() as rule_db:
                try:
                    for change in attr_changes:
                        await apply_attribute_change_rules(
                            self._rule_executor,
                            rule_db,
                            tenant_id=tenant_id,
                            device_id=device_id,
                            scope=change.scope,
                            key=change.key,
                            old_value=change.old_value,
                            new_value=change.new_value,
                        )
                    await rule_db.commit()
                except Exception:
                    await rule_db.rollback()
                    logger.exception("Rule executor failed after client attributes device=%s", device_id)
        logger.warning(
            "MQTT Subscriber client attributes: device=%s keys=%s",
            device_id,
            count,
        )

    async def _handle_rpc_response(self, message: aiomqtt.Message, topic_str: str) -> None:
        parsed = parse_rpc_response_topic(topic_str)
        if parsed is None:
            logger.warning("MQTT Subscriber ignored RPC topic: %s", topic_str)
            return
        payload_bytes = _message_payload_bytes(message.payload)
        if payload_bytes is None:
            return
        try:
            payload_obj: dict[str, JsonValue] = parse_telemetry_payload_bytes(payload_bytes)
        except Exception as exc:
            logger.warning("MQTT Subscriber invalid RPC payload on %s: %s", topic_str, exc)
            return

        async with async_session() as db:
            try:
                handled = await handle_rpc_response_from_mqtt(db, parsed, payload_obj)
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("MQTT Subscriber RPC response failed on %s", topic_str)
                return
        if handled:
            logger.warning("MQTT Subscriber RPC completed: request=%s", parsed.request_id)

    async def _handle_mesh_event(self, message: aiomqtt.Message, topic_str: str) -> None:
        payload_bytes = _message_payload_bytes(message.payload)
        if payload_bytes is None:
            return
        try:
            payload_obj: dict[str, JsonValue] = parse_telemetry_payload_bytes(payload_bytes)
        except Exception as exc:
            logger.warning("MQTT Subscriber invalid mesh payload on %s: %s", topic_str, exc)
            return
        async with async_session() as db:
            try:
                handled = await ingest_mesh_event_from_mqtt(
                    db,
                    self._redis,
                    topic=topic_str,
                    payload_obj=payload_obj,
                )
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("MQTT Subscriber mesh ingest failed on %s", topic_str)
                return
        if handled:
            logger.warning("MQTT Subscriber mesh event ingested: %s", topic_str)

    async def _handle(self, message: aiomqtt.Message) -> None:
        topic_str = str(message.topic)
        if "/mesh/events/" in topic_str:
            await self._handle_mesh_event(message, topic_str)
            return
        if topic_str.endswith("/telemetry"):
            await self._handle_telemetry(message, topic_str)
            return
        if topic_str.endswith("/attributes"):
            await self._handle_client_attributes(message, topic_str)
            return
        if "/commands/" in topic_str and topic_str.endswith("/response"):
            await self._handle_rpc_response(message, topic_str)
            return
        logger.warning("MQTT Subscriber unhandled topic: %s", topic_str)

    async def run(self) -> None:
        await asyncio.sleep(1.0)
        backoff = 1.0
        max_backoff = min(settings.mqtt_subscriber_reconnect_max_seconds, 30.0)
        while not self._stopping:
            try:
                async with aiomqtt.Client(
                    hostname=settings.mqtt_broker_host,
                    port=settings.mqtt_broker_port,
                    username=settings.mqtt_subscriber_internal_user,
                    password=settings.mqtt_subscriber_internal_password,
                    identifier=_mqtt_client_identifier(),
                    keepalive=30,
                ) as client:
                    await client.subscribe(SUBSCRIBER_TELEMETRY_SHARE_FILTER, qos=1)
                    await client.subscribe(SUBSCRIBER_ATTRIBUTES_SHARE_FILTER, qos=1)
                    await client.subscribe(SUBSCRIBER_RPC_RESPONSE_SHARE_FILTER, qos=1)
                    await client.subscribe(MESH_EVENTS_SUBSCRIBE_FILTER, qos=1)
                    logger.warning(
                        "MQTT Subscriber connected; subscribed telemetry, attributes, rpc, mesh"
                    )
                    backoff = 1.0
                    async for message in client.messages:
                        if self._stopping:
                            break
                        try:
                            await self._handle(message)
                        except Exception:
                            logger.exception("MQTT Subscriber message handler error")
            except aiomqtt.MqttError as exc:
                logger.warning(
                    "MQTT Subscriber disconnected: %s (retry in %.1fs)",
                    exc,
                    backoff,
                )
            except Exception:
                logger.exception("MQTT Subscriber unexpected error (retry in %.1fs)", backoff)

            if self._stopping:
                break
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2.0, max_backoff)

        logger.warning("MQTT Subscriber stopped")

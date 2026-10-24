"""Execute mesh workflows triggered by mesh events."""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.alarms.service import upsert_alarm
from app.attributes.broadcast import broadcast_shared_attribute_update
from app.commands.events import publish_device_command
from app.config import settings
from app.mesh.device_resolver import resolve_device, resolve_device_id_template
from app.mesh.event_bus import MeshDomain, mesh_tenant_fanout_channel
from app.mesh.publisher import MeshEventPublisher
from app.mesh.schemas import MeshEvent
from app.mesh.workflow_schema import (
    MeshWorkflowDefinition,
    WorkflowAction,
    WorkflowActionType,
    WorkflowCondition,
    WorkflowExecutionStatus,
)
from app.mesh.workflow_templates import render_json_object, render_json_value, render_template_string
from app.models.device_attribute import DeviceAttribute, DeviceAttributeScope
from app.models.device_command import CommandStatus, CommandType, DeviceCommand
from app.models.mesh_event import MeshEventRecord
from app.models.mesh_workflow import MeshWorkflowExecution
from app.mqtt_publisher.protocol import MqttPublisherProtocol
from app.types.json_types import JsonObject, JsonValue
from app.types.redis_client import RedisClient, close_pubsub

logger = logging.getLogger(__name__)


def _store_action_results(action_results: JsonObject) -> dict[str, object]:
    return {key: value for key, value in action_results.items()}


class MeshWorkflowExecutor:
    def __init__(
        self,
        redis: RedisClient,
        publisher: MeshEventPublisher | None,
        mqtt: MqttPublisherProtocol | None,
    ) -> None:
        self._redis = redis
        self._publisher = publisher
        self._mqtt = mqtt

    async def evaluate_conditions(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        definition: MeshWorkflowDefinition,
        template_context: JsonObject,
    ) -> bool:
        for condition in definition.conditions:
            if not await self._evaluate_condition(db, tenant_id, condition, template_context):
                return False
        return True

    async def _evaluate_condition(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        condition: WorkflowCondition,
        template_context: JsonObject,
    ) -> bool:
        if condition.type == "device_state":
            if condition.device_resolver is None:
                return False
            device = await resolve_device(db, self._redis, tenant_id, condition.device_resolver, template_context)
            if device is None:
                return False
            if condition.state_match is None:
                return True
            from app.mesh.device_resolver import device_matches_state

            return await device_matches_state(db, device, condition.state_match)
        if condition.type == "attribute_true":
            if condition.device_resolver is None or condition.attribute is None:
                return False
            device = await resolve_device(db, self._redis, tenant_id, condition.device_resolver, template_context)
            if device is None:
                return False
            from sqlalchemy import select

            row = await db.scalar(
                select(DeviceAttribute).where(
                    DeviceAttribute.device_id == device.id,
                    DeviceAttribute.key == condition.attribute,
                )
            )
            if row is None:
                return False
            value = row.value_json
            return bool(value)
        return True

    def build_template_context(self, event: MeshEvent | None, action_results: JsonObject) -> JsonObject:
        trigger_ctx: JsonObject = {}
        if event is not None:
            trigger_ctx = {
                "event_id": str(event.event_id),
                "domain": event.domain.value,
                "event_type": event.event_type,
                "payload": event.payload,
                "context": event.context.model_dump(mode="json"),
            }
        ctx: JsonObject = {"trigger": trigger_ctx, "actions": action_results}
        for action_id, result in action_results.items():
            if isinstance(result, dict):
                ctx[action_id] = result
        return ctx

    async def plan_actions(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        definition: MeshWorkflowDefinition,
        template_context: JsonObject,
    ) -> list[JsonObject]:
        planned: list[JsonObject] = []
        rolling_results: JsonObject = {}
        for action in definition.actions:
            ctx = {**template_context, "actions": rolling_results}
            entry = await self._plan_action(db, tenant_id, action, ctx)
            planned.append(entry)
            rolling_results[action.id] = entry
        return planned

    async def _plan_action(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        action: WorkflowAction,
        template_context: JsonObject,
    ) -> JsonObject:
        base: JsonObject = {"action_id": action.id, "type": action.type.value}
        if action.device_resolver is not None:
            device = await resolve_device(db, self._redis, tenant_id, action.device_resolver, template_context)
            base["resolved_device_id"] = str(device.id) if device is not None else None
        if action.type == WorkflowActionType.NOTIFICATION and action.template is not None:
            base["message"] = render_template_string(action.template, template_context)
        if action.command is not None:
            base["command"] = action.command
            base["params"] = render_json_object(action.params, template_context)
        return base

    async def execute(
        self,
        db: AsyncSession,
        *,
        workflow_id: uuid.UUID,
        tenant_id: uuid.UUID,
        definition: MeshWorkflowDefinition,
        trigger_event: MeshEvent | None,
        dry_run: bool = False,
    ) -> MeshWorkflowExecution:
        started = datetime.now(tz=UTC)
        correlation_id = trigger_event.correlation_id if trigger_event is not None else uuid.uuid4()
        trigger_event_id: uuid.UUID | None = None
        if trigger_event is not None:
            persisted = await db.scalar(
                select(MeshEventRecord.id).where(MeshEventRecord.id == trigger_event.event_id)
            )
            if persisted is not None:
                trigger_event_id = trigger_event.event_id
        execution = MeshWorkflowExecution(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            trigger_event_id=trigger_event_id,
            status=WorkflowExecutionStatus.RUNNING.value,
            started_at=started,
            action_results={},
            correlation_id=correlation_id,
        )
        db.add(execution)
        await db.flush()

        action_results: JsonObject = {}
        template_context = self.build_template_context(trigger_event, action_results)

        if not await self.evaluate_conditions(db, tenant_id, definition, template_context):
            execution.status = WorkflowExecutionStatus.SKIPPED_CONDITION.value
            execution.completed_at = datetime.now(tz=UTC)
            execution.duration_ms = int((execution.completed_at - started).total_seconds() * 1000)
            execution.action_results = _store_action_results(action_results)
            await db.flush()
            return execution

        if dry_run:
            planned = await self.plan_actions(db, tenant_id, definition, template_context)
            action_results["planned"] = cast(JsonValue, planned)
            execution.status = WorkflowExecutionStatus.SUCCESS.value
            execution.completed_at = datetime.now(tz=UTC)
            execution.duration_ms = 0
            execution.action_results = _store_action_results(action_results)
            await db.flush()
            return execution

        try:
            for action in definition.actions:
                template_context = self.build_template_context(trigger_event, action_results)
                result = await self._run_action(db, tenant_id, action, template_context, trigger_event)
                action_results[action.id] = result
            execution.status = WorkflowExecutionStatus.SUCCESS.value
        except TimeoutError as exc:
            execution.status = WorkflowExecutionStatus.TIMEOUT.value
            execution.error_message = str(exc)
        except Exception as exc:
            logger.exception("Workflow execution failed workflow_id=%s", workflow_id)
            execution.status = WorkflowExecutionStatus.FAILED.value
            execution.error_message = str(exc)
        finally:
            execution.completed_at = datetime.now(tz=UTC)
            execution.duration_ms = int((execution.completed_at - started).total_seconds() * 1000)
            execution.action_results = _store_action_results(action_results)
            await db.flush()
            if execution.status == WorkflowExecutionStatus.SUCCESS.value and self._publisher is not None:
                await self._publish_workflow_completed(db, tenant_id, workflow_id, execution.id, trigger_event)

        return execution

    async def _publish_workflow_completed(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        workflow_id: uuid.UUID,
        execution_id: uuid.UUID,
        trigger_event: MeshEvent | None,
    ) -> None:
        if self._publisher is None or trigger_event is None:
            return
        parent_id: uuid.UUID | None = None
        persisted = await db.scalar(
            select(MeshEventRecord.id).where(MeshEventRecord.id == trigger_event.event_id)
        )
        if persisted is not None:
            parent_id = trigger_event.event_id
        try:
            await self._publisher.publish_event(
                db,
                tenant_id=tenant_id,
                domain=MeshDomain.UI,
                event_type="user_action_triggered",
                device_id=trigger_event.device_id,
                payload={
                    "workflow_id": str(workflow_id),
                    "execution_id": str(execution_id),
                    "message": "workflow_completed",
                },
                correlation_id=trigger_event.correlation_id,
                parent_event_id=parent_id,
            )
        except Exception:
            logger.exception("Failed to publish workflow_completed mesh event")

    async def _run_action(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        action: WorkflowAction,
        template_context: JsonObject,
        trigger_event: MeshEvent | None,
    ) -> JsonObject:
        if action.type in {WorkflowActionType.DISPATCH_DEVICE, WorkflowActionType.TRIGGER_DEVICE}:
            return await self._run_device_command(db, tenant_id, action, template_context)
        if action.type == WorkflowActionType.WAIT_FOR_EVENT:
            return await self._run_wait_for_event(db, tenant_id, action, template_context)
        if action.type == WorkflowActionType.NOTIFICATION:
            return await self._run_notification(db, tenant_id, action, template_context, trigger_event)
        if action.type == WorkflowActionType.SET_ATTRIBUTE:
            return await self._run_set_attribute(db, tenant_id, action, template_context)
        if action.type == WorkflowActionType.CREATE_ALARM:
            return await self._run_create_alarm(db, tenant_id, action, template_context, trigger_event)
        if action.type == WorkflowActionType.LOG_EVENT:
            return await self._run_log_event(db, tenant_id, action, template_context, trigger_event)
        return {"skipped": True, "reason": "unknown_action"}

    async def _run_device_command(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        action: WorkflowAction,
        template_context: JsonObject,
    ) -> JsonObject:
        if action.device_resolver is None or action.command is None:
            raise ValueError("device command action misconfigured")
        device = await resolve_device(db, self._redis, tenant_id, action.device_resolver, template_context)
        if device is None:
            raise ValueError(f"No device for action {action.id}")
        params = render_json_object(action.params, template_context)
        command_type, command_params = _map_workflow_command(action.command, params)
        command = DeviceCommand(
            device_id=device.id,
            tenant_id=device.tenant_id,
            issued_by_user_id=None,
            command_type=command_type,
            params=command_params,
            status=CommandStatus.DISPATCHED,
            dispatched_at=datetime.now(tz=UTC),
        )
        db.add(command)
        await db.flush()
        await publish_device_command(
            self._redis,
            command_id=str(command.id),
            device_id=str(device.id),
            tenant_id=str(device.tenant_id),
            command_type=command_type,
            params=command_params,
            issued_by_user_id=None,
        )
        return {"resolved_device_id": str(device.id), "command_id": str(command.id), "command_type": command_type}

    async def _run_wait_for_event(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        action: WorkflowAction,
        template_context: JsonObject,
    ) -> JsonObject:
        if action.wait_for is None:
            raise ValueError("wait_for missing")
        timeout = float(action.timeout_seconds or 60)
        expected_device: uuid.UUID | None = None
        if action.wait_for.from_device is not None:
            expected_device = await resolve_device_id_template(
                db,
                tenant_id,
                action.wait_for.from_device,
                template_context,
            )
        pubsub = self._redis.pubsub()
        channel = mesh_tenant_fanout_channel(str(tenant_id))
        await pubsub.subscribe(channel)
        deadline = time.monotonic() + timeout
        matched_event_id: str | None = None
        try:
            while time.monotonic() < deadline:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message is None:
                    continue
                data_raw = message.get("data")
                text = data_raw.decode() if isinstance(data_raw, bytes) else str(data_raw)
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    continue
                domain = str(payload.get("domain", ""))
                event_type = str(payload.get("event_type", ""))
                if domain != action.wait_for.domain or event_type != action.wait_for.event_type:
                    continue
                device_raw = payload.get("device_id")
                if expected_device is not None and str(device_raw) != str(expected_device):
                    continue
                matched_event_id = str(payload.get("event_id", ""))
                break
        finally:
            await close_pubsub(pubsub)
        if matched_event_id is None:
            raise TimeoutError(f"wait_for_event timed out after {timeout}s")
        return {"matched_event_id": matched_event_id}

    async def _run_notification(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        action: WorkflowAction,
        template_context: JsonObject,
        trigger_event: MeshEvent | None,
    ) -> JsonObject:
        if action.template is None:
            raise ValueError("notification template missing")
        message = render_template_string(action.template, template_context)
        farm_id: uuid.UUID | None = None
        if trigger_event is not None and trigger_event.context.farm_id is not None:
            farm_id = trigger_event.context.farm_id
        sent = False
        if farm_id is not None and "whatsapp" in action.channels:
            from app.agriculture.notification_dispatcher import AgriNotificationDispatcher

            dispatcher = AgriNotificationDispatcher(db, self._redis)
            sent = await dispatcher.send_custom_message(farm_id, "Mesh workflow", message)
        channel_list: list[JsonValue] = [str(channel) for channel in action.channels]
        return {"message": message, "whatsapp_sent": sent, "channels": channel_list}

    async def _run_set_attribute(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        action: WorkflowAction,
        template_context: JsonObject,
    ) -> JsonObject:
        if action.device_resolver is None or action.scope is None or action.key is None:
            raise ValueError("set_attribute misconfigured")
        device = await resolve_device(db, self._redis, tenant_id, action.device_resolver, template_context)
        if device is None:
            raise ValueError("device not found for set_attribute")
        from sqlalchemy import select

        scope_enum = DeviceAttributeScope(action.scope)
        value = render_json_value(action.value, template_context) if action.value is not None else None
        row = await db.scalar(
            select(DeviceAttribute).where(
                DeviceAttribute.device_id == device.id,
                DeviceAttribute.scope == scope_enum,
                DeviceAttribute.key == action.key,
            )
        )
        if row is None:
            row = DeviceAttribute(
                device_id=device.id,
                tenant_id=device.tenant_id,
                scope=scope_enum,
                key=action.key,
                value_json=value,
                updated_by_user_id=None,
                updated_source="mesh_workflow",
            )
            db.add(row)
        else:
            row.value_json = value
            row.updated_source = "mesh_workflow"
        await db.flush()
        if action.scope == DeviceAttributeScope.SHARED.value and self._mqtt is not None:
            await broadcast_shared_attribute_update(
                self._mqtt,
                tenant_id=device.tenant_id,
                device_id=device.id,
                key=action.key,
                value=value,
                qos=settings.attribute_shared_broadcast_qos,
            )
        return {"resolved_device_id": str(device.id), "key": action.key, "value": value}

    async def _run_create_alarm(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        action: WorkflowAction,
        template_context: JsonObject,
        trigger_event: MeshEvent | None,
    ) -> JsonObject:
        device_id = trigger_event.device_id if trigger_event is not None else None
        if action.device_resolver is not None:
            device = await resolve_device(db, self._redis, tenant_id, action.device_resolver, template_context)
            if device is not None:
                device_id = device.id
        title = render_template_string(action.title or "Workflow alarm", template_context)
        message = render_template_string(action.message or "", template_context) if action.message else None
        row = await upsert_alarm(
            db,
            tenant_id=tenant_id,
            device_id=device_id,
            alarm_type=action.alarm_type or "mesh_workflow",
            severity=action.severity or "warning",
            title=title,
            message=message,
            details={"workflow": True},
            source="mesh_workflow",
            notify=False,
        )
        return {"alarm_id": str(row.id)}

    async def _run_log_event(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        action: WorkflowAction,
        template_context: JsonObject,
        trigger_event: MeshEvent | None,
    ) -> JsonObject:
        if self._publisher is None or trigger_event is None or action.log_message is None:
            return {"logged": False}
        message = render_template_string(action.log_message, template_context)
        parent_id: uuid.UUID | None = None
        persisted = await db.scalar(
            select(MeshEventRecord.id).where(MeshEventRecord.id == trigger_event.event_id)
        )
        if persisted is not None:
            parent_id = trigger_event.event_id
        event_id = await self._publisher.publish_event(
            db,
            tenant_id=tenant_id,
            domain=MeshDomain.UI,
            event_type="user_action_triggered",
            device_id=trigger_event.device_id,
            payload={"message": message, "level": "log"},
            correlation_id=trigger_event.correlation_id,
            parent_event_id=parent_id,
        )
        return {"logged": True, "mesh_event_id": str(event_id)}


def _map_workflow_command(command: str, params: JsonObject) -> tuple[str, dict[str, JsonValue]]:
    normalized = command.strip().lower()
    if normalized in {"fly_to", "go_to"}:
        target = params.get("target")
        if isinstance(target, dict):
            lat = target.get("lat")
            lng = target.get("lng")
            if isinstance(lat, int | float) and isinstance(lng, int | float):
                return CommandType.GO_TO_WAYPOINT.value, {"lat": float(lat), "lon": float(lng)}
        lat = params.get("lat")
        lon = params.get("lon") if "lon" in params else params.get("lng")
        if isinstance(lat, int | float) and isinstance(lon, int | float):
            return CommandType.GO_TO_WAYPOINT.value, {"lat": float(lat), "lon": float(lon)}
    if normalized in {"open_valve", "spray", "capture_ndvi", "capture_image", "lock", "record"}:
        return CommandType.SET_ACTUATOR.value, {"value": command, **params}
    return CommandType.SET_ACTUATOR.value, {"value": command, **params}


_executor: MeshWorkflowExecutor | None = None


def init_mesh_workflow_executor(
    redis: RedisClient,
    publisher: MeshEventPublisher | None,
    mqtt: MqttPublisherProtocol | None,
) -> MeshWorkflowExecutor:
    global _executor
    _executor = MeshWorkflowExecutor(redis, publisher, mqtt)
    return _executor


def get_mesh_workflow_executor() -> MeshWorkflowExecutor | None:
    return _executor

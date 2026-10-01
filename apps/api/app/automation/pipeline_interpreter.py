"""No-code automation pipeline rule interpreter — Trigger → Condition → Action."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import redis.asyncio as aioredis
from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.events import publish_automation_event
from app.automation.schemas import PipelineExecutionStep
from app.mission.sar_emergency_events import publish_sar_emergency_alert
from app.mission.sar_grid_service import SarGridService
from app.models.automation_pipeline import AutomationPipeline


def _metric_float(context: dict[str, JsonValue], *keys: str) -> float | None:
    metrics = context.get("metrics") or {}
    for key in keys:
        if key in context and context[key] is not None:
            try:
                return float(context[key])
            except (TypeError, ValueError):
                continue
        if key in metrics and metrics[key] is not None:
            try:
                return float(metrics[key])
            except (TypeError, ValueError):
                continue
    return None


class PipelineInterpreterService:
    """Evaluate and execute automation pipeline graphs."""

    def __init__(self) -> None:
        self._grid_service = SarGridService()

    def evaluate_trigger(
        self,
        subtype: str,
        event_type: str,
        context: dict[str, JsonValue],
        config: dict[str, JsonValue] | None = None,
    ) -> bool:
        mapping = {
            "AI_DETECTION": "AI_DETECTION",
            "TELEMETRY_ANOMALY": "TELEMETRY_ANOMALY",
            "GEOFENCE_BREACH": "GEOFENCE_BREACH",
            "WEATHER_HAZARD": "WEATHER_HAZARD",
            "TELEMETRY_THRESHOLD": "TELEMETRY_THRESHOLD",
        }
        expected = mapping.get(subtype)
        if expected is None or event_type != expected:
            return False

        node_config = config or {}
        if subtype == "TELEMETRY_THRESHOLD":
            return self._metric_threshold(node_config, context)
        if subtype == "AI_DETECTION":
            return context.get("detection_class") is not None
        if subtype == "TELEMETRY_ANOMALY":
            allowed = node_config.get("anomaly_types")
            anomaly = context.get("anomaly_type")
            if allowed and isinstance(allowed, list):
                return anomaly in allowed
            return anomaly is not None
        if subtype == "GEOFENCE_BREACH":
            return context.get("anomaly_type") == "geofence_breach" or context.get("breach_type") is not None
        if subtype == "WEATHER_HAZARD":
            status = context.get("flight_safety_status") or context.get("weather_status")
            return status in {"CAUTION", "NO_FLY"}
        return True

    def _metric_threshold(self, config: dict[str, JsonValue], context: dict[str, JsonValue]) -> bool:
        metric = str(config.get("metric") or "temperature")
        operator = str(config.get("operator") or ">")
        threshold = float(config.get("threshold", 0))
        value = _metric_float(context, metric, metric.replace(".", "_"))
        if value is None:
            return False
        ops = {
            ">": value > threshold,
            "<": value < threshold,
            ">=": value >= threshold,
            "<=": value <= threshold,
            "==": value == threshold,
        }
        return ops.get(operator, False)

    def _evaluate_metric_clause(self, clause: dict[str, JsonValue], context: dict[str, JsonValue]) -> bool:
        metric = str(clause.get("metric") or "temperature")
        operator = str(clause.get("operator") or ">")
        threshold = float(clause.get("threshold", 0))
        return self._metric_threshold(
            {"metric": metric, "operator": operator, "threshold": threshold},
            context,
        )

    def evaluate_condition(self, subtype: str, config: dict[str, JsonValue], context: dict[str, JsonValue]) -> bool:
        if subtype == "LOGIC_AND":
            clauses = config.get("conditions") or []
            if not isinstance(clauses, list) or not clauses:
                return False
            return all(self._evaluate_metric_clause(c, context) for c in clauses)

        if subtype == "LOGIC_OR":
            clauses = config.get("conditions") or []
            if not isinstance(clauses, list) or not clauses:
                return False
            return any(self._evaluate_metric_clause(c, context) for c in clauses)

        if subtype == "WIND_SPEED_LESS_THAN":
            threshold = float(config.get("threshold", 15))
            wind = _metric_float(context, "wind_speed_m_s", "wind_speed")
            return wind is not None and wind < threshold

        if subtype == "BATTERY_ABOVE":
            threshold = float(config.get("threshold", 11.0))
            voltage = _metric_float(context, "voltage", "battery_voltage", "batt_voltage")
            return voltage is not None and voltage > threshold

        if subtype == "TIME_WINDOW":
            start_hour = int(config.get("start_hour", 0))
            end_hour = int(config.get("end_hour", 23))
            now_hour = datetime.now(UTC).hour
            if start_hour <= end_hour:
                return start_hour <= now_hour <= end_hour
            return now_hour >= start_hour or now_hour <= end_hour

        return True

    async def execute_action(
        self,
        subtype: str,
        config: dict[str, JsonValue],
        context: dict[str, JsonValue],
        *,
        redis: aioredis.Redis | None = None,
        tenant_id: uuid.UUID | None = None,
        dry_run: bool = False,
    ) -> dict[str, JsonValue]:
        device_id = context.get("device_id")
        message = config.get("message") or context.get("message") or f"Automation action {subtype}"

        if subtype in {"MAVLINK_ARM", "MAVLINK_RTL", "MAVLINK_LAND"}:
            command_map = {
                "MAVLINK_ARM": "ARM",
                "MAVLINK_RTL": "RTL",
                "MAVLINK_LAND": "LAND",
            }
            return {
                "action": subtype,
                "command": command_map[subtype],
                "device_id": device_id,
                "dry_run": dry_run,
                "dispatched": not dry_run,
            }

        if subtype == "DISPATCH_SAR_GRID":
            lat = context.get("lat") or _metric_float(context, "latitude", "lat")
            lon = context.get("lon") or _metric_float(context, "longitude", "lon")
            if lat is None or lon is None:
                return {"action": subtype, "success": False, "reason": "missing coordinates"}
            if dry_run:
                return {"action": subtype, "success": True, "dry_run": True, "lat": lat, "lon": lon}
            grid = self._grid_service.generate(lkp_lat=float(lat), lkp_lon=float(lon), radius_m=500)
            return {"action": subtype, "success": True, "waypoint_count": grid.get("waypoint_count", 0)}

        if subtype in {"TRIGGER_ALARM", "TRIGGER_ALERT"}:
            if dry_run or redis is None or tenant_id is None:
                return {"action": subtype, "success": True, "dry_run": dry_run, "message": message}
            await publish_automation_event(
                redis,
                tenant_id=str(tenant_id),
                event_type="TRIGGER_ALARM",
                context={"message": message, "device_id": device_id},
            )
            return {"action": subtype, "success": True, "message": message}

        if subtype == "DEVICE_COMMAND":
            command = str(config.get("command") or "relay_on").lower()
            target_device = config.get("device_id") or device_id
            return {
                "action": subtype,
                "success": True,
                "dry_run": dry_run,
                "device_id": target_device,
                "command": command,
                "dispatched": not dry_run,
            }

        if subtype == "SEND_WEBHOOK":
            url = config.get("url")
            if not url:
                return {"action": subtype, "success": False, "reason": "missing url"}
            return {
                "action": subtype,
                "success": True,
                "dry_run": dry_run,
                "url": url,
                "method": config.get("method") or "POST",
            }

        if subtype == "WEBSOCKET_ALERT":
            if dry_run or redis is None or tenant_id is None:
                return {"action": subtype, "success": True, "dry_run": dry_run, "message": message}
            await publish_sar_emergency_alert(
                redis,
                tenant_id=str(tenant_id),
                event_type="automation.websocket_alert",
                incident={"message": message, "device_id": device_id, "source": "automation_pipeline"},
            )
            return {"action": subtype, "success": True, "message": message}

        return {"action": subtype, "success": False, "reason": "unknown action"}

    def _build_adjacency(self, edges: list[dict[str, JsonValue]]) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = {}
        for edge in edges:
            source = edge.get("from") or edge.get("from_node")
            target = edge.get("to") or edge.get("to_node")
            if source and target:
                adjacency.setdefault(str(source), []).append(str(target))
        return adjacency

    def _node_map(self, nodes: list[dict[str, JsonValue]]) -> dict[str, dict[str, JsonValue]]:
        return {str(node["id"]): node for node in nodes if node.get("id")}

    async def run_pipeline(
        self,
        pipeline: AutomationPipeline | dict[str, JsonValue],
        *,
        event_type: str,
        context: dict[str, JsonValue],
        redis: aioredis.Redis | None = None,
        tenant_id: uuid.UUID | None = None,
        dry_run: bool = False,
    ) -> tuple[bool, list[PipelineExecutionStep]]:
        if isinstance(pipeline, AutomationPipeline):
            nodes = pipeline.nodes_json or []
            edges = pipeline.edges_json or []
            tid = pipeline.tenant_id
        else:
            nodes = pipeline.get("nodes_json") or []
            edges = pipeline.get("edges_json") or []
            tid = tenant_id

        node_by_id = self._node_map(nodes)
        adjacency = self._build_adjacency(edges)
        steps: list[PipelineExecutionStep] = []
        executed = False

        trigger_nodes = [n for n in nodes if n.get("type") == "TRIGGER"]
        for trigger in trigger_nodes:
            subtype = str(trigger.get("subtype", ""))
            trigger_config = trigger.get("config") or {}
            matched = self.evaluate_trigger(subtype, event_type, context, trigger_config)
            steps.append(
                PipelineExecutionStep(
                    node_id=str(trigger["id"]),
                    node_type="TRIGGER",
                    subtype=subtype,
                    matched=matched,
                    result={"event_type": event_type},
                )
            )
            if not matched:
                continue

            queue = adjacency.get(str(trigger["id"]), [])
            while queue:
                node_id = queue.pop(0)
                node = node_by_id.get(node_id)
                if node is None:
                    continue

                node_type = str(node.get("type", ""))
                subtype = str(node.get("subtype", ""))
                config = node.get("config") or {}

                if node_type == "CONDITION":
                    passed = self.evaluate_condition(subtype, config, context)
                    steps.append(
                        PipelineExecutionStep(
                            node_id=node_id,
                            node_type=node_type,
                            subtype=subtype,
                            matched=passed,
                            result={"passed": passed},
                        )
                    )
                    if not passed:
                        continue
                    queue.extend(adjacency.get(node_id, []))

                elif node_type == "ACTION":
                    result = await self.execute_action(
                        subtype,
                        config,
                        context,
                        redis=redis,
                        tenant_id=tid,
                        dry_run=dry_run,
                    )
                    steps.append(
                        PipelineExecutionStep(
                            node_id=node_id,
                            node_type=node_type,
                            subtype=subtype,
                            matched=True,
                            result=result,
                        )
                    )
                    executed = True
                    queue.extend(adjacency.get(node_id, []))

        return executed, steps

    async def process_event(
        self,
        db: AsyncSession,
        redis: aioredis.Redis,
        *,
        tenant_id: uuid.UUID,
        event_type: str,
        context: dict[str, JsonValue],
    ) -> list[dict[str, JsonValue]]:
        query = select(AutomationPipeline).where(
            AutomationPipeline.tenant_id == tenant_id,
            AutomationPipeline.is_active.is_(True),
        )
        pipelines = (await db.scalars(query)).all()
        results: list[dict[str, JsonValue]] = []

        for pipeline in pipelines:
            executed, steps = await self.run_pipeline(
                pipeline,
                event_type=event_type,
                context=context,
                redis=redis,
                tenant_id=tenant_id,
                dry_run=False,
            )
            if executed or any(s.matched for s in steps):
                results.append(
                    {
                        "pipeline_id": str(pipeline.id),
                        "pipeline_name": pipeline.name,
                        "executed": executed,
                        "steps": [s.model_dump() for s in steps],
                    }
                )
        return results


pipeline_interpreter_service = PipelineInterpreterService()

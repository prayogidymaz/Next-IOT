"""Detect and suggest fixes for failing mesh workflows."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.healer.error_classifier import ErrorClassifier
from app.agents.healer.types import BrokenWorkflow, Diagnosis, ErrorCategory, FixSuggestion
from app.agents.models import AgentHealingSuggestion, HealingSuggestionStatus
from app.auth.dependencies import CurrentUser
from app.models.mesh_workflow import MeshWorkflow, MeshWorkflowExecution
from app.types.json_types import JsonObject
from app.workflows.versioning.service import VersioningService


class WorkflowHealer:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._classifier = ErrorClassifier()

    async def detect_broken_workflows(self, tenant_id: uuid.UUID) -> list[BrokenWorkflow]:
        since = datetime.now(tz=UTC) - timedelta(hours=24)
        rows = await self._db.execute(
            select(
                MeshWorkflowExecution.workflow_id,
                MeshWorkflow.name,
                func.count().label("total"),
                func.sum(case((MeshWorkflowExecution.status == "failed", 1), else_=0)).label("failed"),
            )
            .join(MeshWorkflow, MeshWorkflow.id == MeshWorkflowExecution.workflow_id)
            .where(
                MeshWorkflowExecution.tenant_id == tenant_id,
                MeshWorkflowExecution.started_at >= since,
            )
            .group_by(MeshWorkflowExecution.workflow_id, MeshWorkflow.name)
        )
        broken: list[BrokenWorkflow] = []
        for workflow_id, name, total, failed in rows.all():
            total_i = int(total or 0)
            failed_i = int(failed or 0)
            if total_i < 3:
                continue
            rate = failed_i / total_i
            if rate > 0.5:
                broken.append(
                    BrokenWorkflow(
                        workflow_id=cast(uuid.UUID, workflow_id),
                        workflow_name=str(name),
                        failure_rate=rate,
                        sample_size=total_i,
                    )
                )
        return broken

    async def diagnose(self, workflow_id: uuid.UUID) -> Diagnosis:
        rows = await self._db.scalars(
            select(MeshWorkflowExecution)
            .where(
                MeshWorkflowExecution.workflow_id == workflow_id,
                MeshWorkflowExecution.status == "failed",
            )
            .order_by(MeshWorkflowExecution.started_at.desc())
            .limit(10)
        )
        samples: list[str] = []
        categories: list[ErrorCategory] = []
        for row in rows.all():
            msg = row.error_message or "unknown error"
            samples.append(msg)
            ctx = row.action_results if isinstance(row.action_results, dict) else {}
            categories.append(self._classifier.classify(msg, cast(JsonObject, ctx)))

        primary = categories[0] if categories else ErrorCategory.UNKNOWN
        recommendation = self._recommendation_for(primary)
        return Diagnosis(
            workflow_id=workflow_id,
            primary_category=primary,
            error_samples=samples,
            recommendation=recommendation,
        )

    async def suggest_fix(self, workflow_id: uuid.UUID, diagnosis: Diagnosis) -> FixSuggestion:
        mesh = await self._db.get(MeshWorkflow, workflow_id)
        definition = mesh.definition if mesh and isinstance(mesh.definition, dict) else {}
        patch: JsonObject = {"definition": dict(definition)}
        confidence = 0.55
        summary = diagnosis.recommendation

        if diagnosis.primary_category == ErrorCategory.DEVICE_OFFLINE:
            patch["fallback"] = {"disable_on_offline": True}
            confidence = 0.72
            summary = "Add offline fallback or disable rule when device unreachable"
        elif diagnosis.primary_category == ErrorCategory.SCHEMA_INVALID:
            patch["definition"] = {**dict(definition), "schema_version": 2}
            confidence = 0.65
        elif diagnosis.primary_category == ErrorCategory.TIMEOUT:
            patch["timeouts"] = {"action_ms": 30_000}
            confidence = 0.7
        elif diagnosis.primary_category == ErrorCategory.PERMISSION:
            patch["rbac"] = {"require_role": "operator"}
            confidence = 0.6

        return FixSuggestion(
            workflow_id=workflow_id,
            patch=patch,
            confidence=confidence,
            summary=summary,
        )

    async def persist_suggestion(
        self,
        tenant_id: uuid.UUID,
        diagnosis: Diagnosis,
        fix: FixSuggestion,
    ) -> AgentHealingSuggestion:
        row = AgentHealingSuggestion(
            workflow_id=fix.workflow_id,
            tenant_id=tenant_id,
            diagnosis_json={
                "category": diagnosis.primary_category.value,
                "samples": diagnosis.error_samples,
                "recommendation": diagnosis.recommendation,
            },
            fix_json={"patch": fix.patch, "summary": fix.summary},
            confidence=fix.confidence,
            status=HealingSuggestionStatus.PENDING,
        )
        self._db.add(row)
        await self._db.flush()
        return row

    async def apply_fix(
        self,
        fix_id: uuid.UUID,
        approved_by: CurrentUser,
    ) -> MeshWorkflow:
        suggestion = await self._db.get(AgentHealingSuggestion, fix_id)
        if suggestion is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
        if suggestion.status not in {HealingSuggestionStatus.PENDING, HealingSuggestionStatus.APPROVED}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suggestion not applicable")

        mesh = await self._db.get(MeshWorkflow, suggestion.workflow_id)
        if mesh is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

        fix_body = suggestion.fix_json if isinstance(suggestion.fix_json, dict) else {}
        patch_raw = fix_body.get("patch")
        patch = patch_raw if isinstance(patch_raw, dict) else {}
        def_raw = patch.get("definition")
        if isinstance(def_raw, dict):
            mesh.definition = def_raw

        versioning = VersioningService(self._db)
        await versioning.create_version_from_mesh_row(mesh, approved_by.user_id)

        suggestion.status = HealingSuggestionStatus.APPLIED
        suggestion.approved_by = approved_by.user_id
        suggestion.applied_at = datetime.now(tz=UTC)
        await self._db.flush()
        return mesh

    @staticmethod
    def _recommendation_for(category: ErrorCategory) -> str:
        mapping = {
            ErrorCategory.DEVICE_OFFLINE: "Suggest fallback device or disable rule when offline",
            ErrorCategory.SCHEMA_INVALID: "Suggest schema fix on action payload",
            ErrorCategory.TIMEOUT: "Suggest increase timeout threshold",
            ErrorCategory.PERMISSION: "Suggest role check before action",
            ErrorCategory.DEPENDENCY_MISSING: "Verify dependent resource exists",
            ErrorCategory.RATE_LIMITED: "Backoff or reduce trigger frequency",
            ErrorCategory.UNKNOWN: "Review failed execution logs manually",
        }
        return mapping[category]

"""Workflow healer unit tests."""

from __future__ import annotations

import uuid

import pytest

from app.agents.healer.error_classifier import ErrorClassifier
from app.agents.healer.types import ErrorCategory


def test_classifier_device_offline() -> None:
    cat = ErrorClassifier().classify("Device offline during action", {})
    assert cat == ErrorCategory.DEVICE_OFFLINE


def test_classifier_schema_invalid() -> None:
    cat = ErrorClassifier().classify("Invalid payload for sensor", {})
    assert cat == ErrorCategory.SCHEMA_INVALID


def test_classifier_timeout() -> None:
    cat = ErrorClassifier().classify("Action timed out", {})
    assert cat == ErrorCategory.TIMEOUT


def test_classifier_permission() -> None:
    cat = ErrorClassifier().classify("403 forbidden", {})
    assert cat == ErrorCategory.PERMISSION


def test_classifier_unknown() -> None:
    cat = ErrorClassifier().classify("something else", {})
    assert cat == ErrorCategory.UNKNOWN


def test_recommendation_mapping() -> None:
    from app.agents.healer.workflow_healer import WorkflowHealer

    text = WorkflowHealer._recommendation_for(ErrorCategory.TIMEOUT)
    assert "timeout" in text.lower()


@pytest.mark.asyncio
async def test_detect_broken_empty_db() -> None:
    from app.database import async_session
    from app.agents.healer.workflow_healer import WorkflowHealer

    async with async_session() as db:
        rows = await WorkflowHealer(db).detect_broken_workflows(uuid.uuid4())
        assert isinstance(rows, list)


@pytest.mark.asyncio
async def test_suggest_fix_returns_patch() -> None:
    from app.database import async_session
    from app.agents.healer.types import Diagnosis
    from app.agents.healer.workflow_healer import WorkflowHealer

    diagnosis = Diagnosis(
        workflow_id=uuid.uuid4(),
        primary_category=ErrorCategory.SCHEMA_INVALID,
        error_samples=["invalid payload"],
        recommendation="fix schema",
    )
    async with async_session() as db:
        fix = await WorkflowHealer(db).suggest_fix(diagnosis.workflow_id, diagnosis)
        assert fix.confidence > 0
        assert "definition" in fix.patch or "schema" in str(fix.patch).lower()

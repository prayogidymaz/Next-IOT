"""Threshold adjuster tests."""

from __future__ import annotations

import uuid

import pytest

from app.agents.learner.threshold_adjuster import ThresholdAdjuster


@pytest.mark.asyncio
async def test_analyze_returns_none_without_data() -> None:
    from app.database import async_session

    async with async_session() as db:
        result = await ThresholdAdjuster(db).analyze_and_adjust(uuid.uuid4(), period_days=30)
        assert result is None


def test_adjustment_dataclass_fields() -> None:
    from app.agents.learner.threshold_adjuster import ThresholdAdjustment

    row = ThresholdAdjustment(
        workflow_id=uuid.uuid4(),
        metric="soil_moisture_percent",
        old_value=40.0,
        suggested_value=35.0,
        reason="test",
    )
    assert row.suggested_value < row.old_value


@pytest.mark.asyncio
async def test_persist_suggestion() -> None:
    from app.database import async_session
    from app.agents.learner.threshold_adjuster import ThresholdAdjustment, ThresholdAdjuster

    adj = ThresholdAdjustment(
        workflow_id=uuid.uuid4(),
        metric="soil_moisture_percent",
        old_value=40.0,
        suggested_value=35.0,
        reason="too many fires",
    )
    async with async_session() as db:
        row = await ThresholdAdjuster(db).persist_suggestion(uuid.uuid4(), adj)
        assert row.status == "pending"


def test_feedback_loop_retrain_requires_samples() -> None:
    from app.agents.learner.feedback_loop import FeedbackLoop

    class DummyDb:
        pass

    loop = FeedbackLoop(DummyDb())  # type: ignore[arg-type]
    assert loop.retrain_weekly() is False


def test_feedback_prioritize_without_model() -> None:
    from app.agents.learner.feedback_loop import FeedbackLoop

    class DummyDb:
        pass

    loop = FeedbackLoop(DummyDb())  # type: ignore[arg-type]
    score = loop.prioritize_alert({"severity_score": 0.8})
    assert score == 0.8

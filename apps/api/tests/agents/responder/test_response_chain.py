"""Response chain tests."""

from __future__ import annotations

import uuid

import pytest

from app.agents.responder.chain_definitions import CHAIN_REGISTRY, DEVICE_HEALTH_CHAIN


def test_registry_contains_pest_chain() -> None:
    assert "pest_response" in CHAIN_REGISTRY


def test_irrigation_chain_step_count() -> None:
    assert len(CHAIN_REGISTRY["irrigation_smart"].steps) == 6


def test_device_health_chain_first_step() -> None:
    assert DEVICE_HEALTH_CHAIN.steps[0].step_id == "detect_offline"


def test_chain_template_ids_unique() -> None:
    ids = [tpl.chain_id for tpl in CHAIN_REGISTRY.values()]
    assert len(ids) == len(set(ids))


@pytest.mark.asyncio
async def test_executor_start_unknown_chain() -> None:
    from app.database import async_session
    from app.agents.responder.chain_executor import ChainExecutor

    class FakeRedis:
        async def set(self, *_a: object, **_k: object) -> None:
            return None

        async def publish(self, *_a: object, **_k: object) -> None:
            return None

    async with async_session() as db:
        executor = ChainExecutor(db, FakeRedis())  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            await executor.start("missing", uuid.uuid4(), None, {})


def test_response_chain_picks_pest_for_vision() -> None:
    from datetime import UTC, datetime

    from app.agents.responder.response_chain import ResponseChain
    from app.mesh.event_bus import MeshDomain
    from app.mesh.schemas import MeshContext, MeshEvent

    event = MeshEvent(
        event_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        domain=MeshDomain.VISION,
        event_type="detection",
        timestamp=datetime.now(tz=UTC),
        payload={},
        context=MeshContext(),
    )
    assert ResponseChain._chain_for_event(event) == "pest_response"


def test_response_chain_irrigation_threshold() -> None:
    from datetime import UTC, datetime

    from app.agents.responder.response_chain import ResponseChain
    from app.mesh.event_bus import MeshDomain
    from app.mesh.schemas import MeshContext, MeshEvent

    event = MeshEvent(
        event_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        domain=MeshDomain.SENSOR,
        event_type="threshold_exceeded",
        timestamp=datetime.now(tz=UTC),
        payload={},
        context=MeshContext(),
    )
    assert ResponseChain._chain_for_event(event) == "irrigation_smart"


def test_list_registered_chains() -> None:
    from app.agents.responder.response_chain import ResponseChain

    class Dummy:
        def __init__(self) -> None:
            pass

    # static helper without db
    assert len(CHAIN_REGISTRY) >= 3

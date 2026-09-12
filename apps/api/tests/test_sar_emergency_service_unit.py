import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.mission.sar_emergency_service import SarEmergencyResponseService
from app.mission.schemas import SarIncidentCreateRequest, SarIncidentTypeEnum


@pytest.fixture
def service() -> SarEmergencyResponseService:
    return SarEmergencyResponseService()


def test_generate_sar_grid_on_create_payload(service: SarEmergencyResponseService):
    grid = service._generate_sar_grid(-6.2088, 106.8456)
    assert grid["pattern"] == "expanding_square"
    assert grid["waypoint_count"] >= 2
    assert grid["lkp"]["lat"] == -6.2088


@pytest.mark.asyncio
async def test_create_incident_generates_grid_and_broadcasts(service: SarEmergencyResponseService):
    db = AsyncMock()
    redis = AsyncMock()
    user = MagicMock()
    user.tenant_id = uuid.uuid4()

    async def _refresh(obj):
        return None

    db.flush = AsyncMock()
    db.refresh = AsyncMock(side_effect=_refresh)
    db.add = MagicMock()

    payload = SarIncidentCreateRequest(
        incident_type=SarIncidentTypeEnum.PERSON_LOST,
        target_lat=-6.2088,
        target_lon=106.8456,
        severity="critical",
        message="Missing hiker reported",
    )

    result = await service.create_incident(db, redis, user, payload)

    assert result["incident_type"] == "PERSON_LOST"
    assert result["status"] == "ACTIVE"
    assert result["sar_grid"]["waypoint_count"] >= 2
    redis.publish.assert_called()
    db.add.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_from_anomaly_skips_non_critical(service: SarEmergencyResponseService):
    db = AsyncMock()
    redis = AsyncMock()
    result = await service.trigger_from_anomaly(
        db,
        redis,
        tenant_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        anomaly_type="speed_deviation",
        severity="warning",
        message="Speed warning",
        metadata={"lat": -6.2, "lon": 106.8},
    )
    assert result is None
    db.add.assert_not_called()

import pytest

from app.mission.sar_grid_service import SarGridPattern, SarGridService


@pytest.fixture
def service() -> SarGridService:
    return SarGridService()


def test_expanding_square_starts_at_lkp(service: SarGridService):
    result = service.generate(
        lkp_lat=-6.2088,
        lkp_lon=106.8456,
        radius_m=500,
        pattern=SarGridPattern.EXPANDING_SQUARE,
        leg_spacing_m=100,
    )
    assert result["pattern"] == "expanding_square"
    assert result["waypoint_count"] >= 2
    assert result["waypoints"][0]["label"] == "LKP"
    assert result["waypoints"][0]["lat"] == pytest.approx(-6.2088, abs=0.001)
    assert len(result["tracks"]) == 1
    assert len(result["tracks"][0]["points"]) >= 2
    assert len(result["search_areas"]) == 1
    assert len(result["search_areas"][0]["points"]) == 4


def test_parallel_track_generates_multiple_tracks(service: SarGridService):
    result = service.generate(
        lkp_lat=-6.2088,
        lkp_lon=106.8456,
        radius_m=300,
        pattern=SarGridPattern.PARALLEL_TRACK,
        leg_spacing_m=100,
    )
    assert result["pattern"] == "parallel_track"
    assert len(result["tracks"]) >= 3
    for track in result["tracks"]:
        assert len(track["points"]) == 2


def test_invalid_radius_raises(service: SarGridService):
    with pytest.raises(ValueError, match="radius_m"):
        service.generate(lkp_lat=0, lkp_lon=0, radius_m=0, pattern=SarGridPattern.EXPANDING_SQUARE)

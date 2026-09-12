import pytest

from app.mission.geofence_checker import GeofenceChecker, GeofenceZoneSnapshot


@pytest.fixture
def checker() -> GeofenceChecker:
    return GeofenceChecker()


@pytest.fixture
def square_zone() -> GeofenceZoneSnapshot:
    return GeofenceZoneSnapshot(
        id="zone-1",
        name="No-Fly Alpha",
        polygon_coords=[
            {"lat": -6.2100, "lon": 106.8440},
            {"lat": -6.2100, "lon": 106.8460},
            {"lat": -6.2080, "lon": 106.8460},
            {"lat": -6.2080, "lon": 106.8440},
        ],
        min_altitude=0.0,
        max_altitude=120.0,
        action_on_breach="WARN",
    )


def test_point_in_polygon_inside(checker: GeofenceChecker, square_zone: GeofenceZoneSnapshot):
    assert checker.point_in_polygon(-6.2090, 106.8450, square_zone.polygon_coords) is True


def test_point_in_polygon_outside(checker: GeofenceChecker, square_zone: GeofenceZoneSnapshot):
    assert checker.point_in_polygon(-6.2070, 106.8450, square_zone.polygon_coords) is False


def test_geofence_breach_inside_forbidden_zone(checker: GeofenceChecker, square_zone: GeofenceZoneSnapshot):
    breaches = checker.check_position(-6.2090, 106.8450, 50.0, [square_zone])
    assert len(breaches) == 1
    assert breaches[0].breach_type == "geofence_breach"
    assert breaches[0].zone_name == "No-Fly Alpha"


def test_no_breach_outside_zone(checker: GeofenceChecker, square_zone: GeofenceZoneSnapshot):
    assert checker.check_position(-6.2070, 106.8450, 50.0, [square_zone]) == []


def test_altitude_violation_inside_zone(checker: GeofenceChecker, square_zone: GeofenceZoneSnapshot):
    breaches = checker.check_position(-6.2090, 106.8450, 150.0, [square_zone])
    assert len(breaches) == 1
    assert breaches[0].breach_type == "altitude_violation"


def test_check_altitude_violation_helper(checker: GeofenceChecker):
    assert checker.check_altitude_violation(150.0, min_altitude=0.0, max_altitude=120.0) is True
    assert checker.check_altitude_violation(50.0, min_altitude=0.0, max_altitude=120.0) is False

from app.telemetry.swarm_distance import (
    COLLISION_RISK_THRESHOLD_M,
    COLLISION_RISK_WARNING,
    SwarmDistanceCalculator,
    SwarmNode,
)


def test_haversine_distance_same_point_is_zero():
    calc = SwarmDistanceCalculator()
    assert calc.haversine_m(-6.2088, 106.8456, -6.2088, 106.8456) == 0.0


def test_compute_links_detects_collision_risk():
    calc = SwarmDistanceCalculator(collision_threshold_m=20.0)
    nodes = [
        SwarmNode(device_id="d1", lat=-6.2088, lon=106.8456),
        SwarmNode(device_id="d2", lat=-6.20881, lon=106.84561),
    ]
    links = calc.compute_links(nodes)
    assert len(links) == 1
    assert links[0].collision_risk is True
    assert links[0].warning == COLLISION_RISK_WARNING
    assert links[0].distance_m < COLLISION_RISK_THRESHOLD_M


def test_compute_links_safe_distance():
    calc = SwarmDistanceCalculator(collision_threshold_m=20.0)
    nodes = [
        SwarmNode(device_id="d1", lat=-6.2088, lon=106.8456),
        SwarmNode(device_id="d2", lat=-6.2188, lon=106.8556),
    ]
    links = calc.compute_links(nodes)
    assert len(links) == 1
    assert links[0].collision_risk is False
    assert links[0].warning is None
    assert links[0].distance_m > COLLISION_RISK_THRESHOLD_M


def test_compute_matrix_three_nodes():
    calc = SwarmDistanceCalculator()
    nodes = [
        SwarmNode(device_id="a", lat=0.0, lon=0.0),
        SwarmNode(device_id="b", lat=0.0, lon=0.001),
        SwarmNode(device_id="c", lat=0.001, lon=0.0),
    ]
    matrix = calc.compute_matrix(nodes)
    assert matrix["node_count"] == 3
    assert matrix["link_count"] == 3

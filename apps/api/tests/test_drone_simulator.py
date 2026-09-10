from app.drone_simulator.interpolation import GeoPoint, build_mission_path, interpolate_segment, steps_for_segment


def test_interpolate_segment_endpoints():
    start = GeoPoint(-6.2088, 106.8456, 30.0)
    end = GeoPoint(-6.2100, 106.8500, 60.0)
    path = interpolate_segment(start, end, steps=4)
    assert len(path) == 4
    assert path[-1].latitude == end.latitude
    assert path[-1].longitude == end.longitude
    assert path[-1].altitude_m == end.altitude_m


def test_build_mission_path_follows_waypoints():
    origin = GeoPoint(-6.2088, 106.8456, 28.0)
    waypoints = [(-6.2095, 106.8470), (-6.2105, 106.8485)]
    path = build_mission_path(origin, waypoints, cruise_altitude_m=60.0, min_steps=3, max_steps=5)
    assert len(path) >= 6
    assert path[-1].latitude == waypoints[-1][0]
    assert path[-1].altitude_m == 60.0


def test_steps_for_segment_scales_with_distance():
    near = GeoPoint(0.0, 0.0, 10.0)
    far = GeoPoint(0.0, 0.1, 10.0)
    assert steps_for_segment(near, near, min_steps=5, max_steps=20) == 5
    assert steps_for_segment(near, far, min_steps=5, max_steps=20) > 5

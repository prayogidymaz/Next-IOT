import math

import pytest
from pymavlink.dialects.v20 import common as mavlink

from app.mavlink.bridge_service import MavlinkBridgeService
from app.mavlink.constants import MavlinkCommandType


def _pack_message(mav: mavlink.MAVLink, msg: mavlink.MAVLink_message) -> bytes:
    return msg.pack(mav)


def _heartbeat_packet() -> bytes:
    mav = mavlink.MAVLink(None, srcSystem=1, srcComponent=1)
    msg = mav.heartbeat_encode(
        mavlink.MAV_TYPE_QUADROTOR,
        mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
        mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        0,
        mavlink.MAV_STATE_ACTIVE,
    )
    return _pack_message(mav, msg)


def _global_position_packet() -> bytes:
    mav = mavlink.MAVLink(None, srcSystem=1, srcComponent=1)
    msg = mav.global_position_int_encode(
        0,
        int(-6.2088 * 1e7),
        int(106.8456 * 1e7),
        int(120 * 1000),
        int(100 * 1000),
        100,
        200,
        300,
        int(90 * 100),
    )
    return _pack_message(mav, msg)


def _attitude_packet() -> bytes:
    mav = mavlink.MAVLink(None, srcSystem=1, srcComponent=1)
    msg = mav.attitude_encode(
        0,
        math.radians(5.0),
        math.radians(-3.0),
        math.radians(120.0),
        0.01,
        0.02,
        0.03,
    )
    return _pack_message(mav, msg)


def _sys_status_packet() -> bytes:
    mav = mavlink.MAVLink(None, srcSystem=1, srcComponent=1)
    msg = mav.sys_status_encode(
        0,
        0,
        0,
        0,
        12600,
        500,
        88,
        0,
        0,
        0,
        0,
        0,
        0,
    )
    return _pack_message(mav, msg)


def test_decode_heartbeat_sets_connected():
    bridge = MavlinkBridgeService()
    types, snapshot = bridge.decode_packet(_heartbeat_packet())
    assert "HEARTBEAT" in types
    assert snapshot.mavlink_connected is True
    assert snapshot.autopilot == "ArduPilot"


def test_decode_global_position_and_attitude_metrics():
    bridge = MavlinkBridgeService()
    bridge.feed_bytes(_global_position_packet())
    types, snapshot = bridge.feed_bytes(_attitude_packet())
    assert "ATTITUDE" in types
    metrics = snapshot.metrics
    assert metrics["latitude"] == pytest.approx(-6.2088, abs=0.0001)
    assert metrics["longitude"] == pytest.approx(106.8456, abs=0.0001)
    assert metrics["roll"] == pytest.approx(5.0, abs=0.1)
    assert metrics["pitch"] == pytest.approx(-3.0, abs=0.1)
    assert metrics["yaw"] == pytest.approx(120.0, abs=0.1)


def test_decode_sys_status_battery():
    bridge = MavlinkBridgeService()
    _, snapshot = bridge.decode_packet(_sys_status_packet())
    assert snapshot.metrics["battery"] == pytest.approx(88.0)
    assert snapshot.metrics["voltage"] == pytest.approx(12.6, abs=0.01)


def test_encode_arm_and_disarm_packets():
    bridge = MavlinkBridgeService()
    arm = bridge.encode_command(MavlinkCommandType.ARM)
    disarm = bridge.encode_command(MavlinkCommandType.DISARM)
    assert arm[0] == 0xFD
    assert disarm[0] == 0xFD
    assert arm != disarm


def test_encode_rtl_land_waypoint():
    bridge = MavlinkBridgeService()
    rtl = bridge.encode_command(MavlinkCommandType.RTL)
    land = bridge.encode_command(MavlinkCommandType.LAND)
    waypoint = bridge.encode_command(
        MavlinkCommandType.WAYPOINT,
        params={"lat": -6.2, "lon": 106.8, "altitude_m": 50},
    )
    assert rtl[0] == 0xFD
    assert land[0] == 0xFD
    assert waypoint[0] == 0xFD
    assert len(waypoint) > 10


def test_feed_bytes_stream_concatenation():
    bridge = MavlinkBridgeService()
    packet = _heartbeat_packet() + _attitude_packet()
    types, snapshot = bridge.feed_bytes(packet)
    assert "HEARTBEAT" in types
    assert "ATTITUDE" in types
    assert snapshot.mavlink_connected is True

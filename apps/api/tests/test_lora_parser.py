from app.hardware.parser import parse_json_packet, parse_nmea_gpgga, parse_serial_line, packet_to_metrics


def test_parse_json_lora_packet():
    line = '{"node_id":"DRONE-01","lat":3.595,"lon":98.665,"alt":60,"rssi":-85,"snr":9.5}'
    packet = parse_json_packet(line)
    assert packet is not None
    assert packet.node_id == "DRONE-01"
    assert packet.latitude == 3.595
    assert packet.longitude == 98.665
    assert packet.altitude_m == 60.0
    assert packet.rssi == -85.0
    assert packet.snr == 9.5


def test_parse_nmea_gpgga_with_node_prefix():
    line = "DRONE-01,$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    packet = parse_nmea_gpgga(line, default_node_id="DRONE-01")
    assert packet is not None
    assert packet.node_id == "DRONE-01"
    assert round(packet.latitude, 4) == 48.1173
    assert round(packet.longitude, 4) == 11.5167
    assert packet.altitude_m == 545.4


def test_parse_serial_line_prefers_json():
    line = '{"node_id":"NODE-2","lat":-6.2,"lon":106.8,"alt":55}'
    packet = parse_serial_line(line)
    assert packet is not None
    assert packet.node_id == "NODE-2"


def test_packet_to_metrics_numeric_only():
    line = '{"node_id":"DRONE-01","lat":3.595,"lon":98.665,"alt":60,"rssi":-85,"snr":9.5}'
    packet = parse_json_packet(line)
    metrics = packet_to_metrics(packet)
    assert metrics["latitude"] == 3.595
    assert metrics["rssi"] == -85.0
    assert all(isinstance(v, (int, float)) for v in metrics.values())

class MavlinkStatus {
  const MavlinkStatus({
    required this.deviceId,
    required this.connected,
    required this.protocolVersion,
    this.autopilot,
    this.lastHeartbeatAt,
    this.metrics = const {},
  });

  final String? deviceId;
  final bool connected;
  final String protocolVersion;
  final String? autopilot;
  final DateTime? lastHeartbeatAt;
  final Map<String, double> metrics;

  bool get isMavlink2 => protocolVersion.startsWith('2');

  factory MavlinkStatus.fromJson(Map<String, dynamic> json) {
    final rawMetrics = json['metrics'] as Map<String, dynamic>? ?? {};
    return MavlinkStatus(
      deviceId: json['device_id'] as String?,
      connected: json['connected'] as bool? ?? false,
      protocolVersion: json['protocol_version'] as String? ?? '2.0',
      autopilot: json['autopilot'] as String?,
      lastHeartbeatAt: json['last_heartbeat_at'] != null
          ? DateTime.tryParse(json['last_heartbeat_at'] as String)
          : null,
      metrics: rawMetrics.map(
        (key, value) => MapEntry(key, (value as num).toDouble()),
      ),
    );
  }

  static MavlinkStatus fromMarkerMetrics(Map<String, double> metrics) {
    final connected = (metrics['mavlink_connected'] ?? 0) >= 1;
    final protocol = metrics['mavlink_protocol']?.toString() ?? '2.0';
    return MavlinkStatus(
      deviceId: null,
      connected: connected,
      protocolVersion: protocol,
      metrics: metrics,
    );
  }
}

class MavlinkAttitude {
  const MavlinkAttitude({
    required this.roll,
    required this.pitch,
    required this.yaw,
  });

  final double roll;
  final double pitch;
  final double yaw;

  factory MavlinkAttitude.fromMetrics(Map<String, double> metrics) {
    return MavlinkAttitude(
      roll: metrics['roll'] ?? 0,
      pitch: metrics['pitch'] ?? 0,
      yaw: metrics['yaw'] ?? 0,
    );
  }
}

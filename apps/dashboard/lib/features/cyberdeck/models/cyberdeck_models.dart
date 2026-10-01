class CyberdeckMeshNode {
  const CyberdeckMeshNode({
    required this.nodeId,
    required this.label,
    required this.deviceType,
    this.latitude,
    this.longitude,
    this.rssi,
    this.snr,
    this.batteryPct,
    this.channel = 1,
    this.online = true,
  });

  final String nodeId;
  final String label;
  final String deviceType;
  final double? latitude;
  final double? longitude;
  final double? rssi;
  final double? snr;
  final double? batteryPct;
  final int channel;
  final bool online;

  factory CyberdeckMeshNode.fromJson(Map<String, dynamic> json) {
    return CyberdeckMeshNode(
      nodeId: json['node_id'] as String,
      label: json['label'] as String,
      deviceType: json['device_type'] as String,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      rssi: (json['rssi'] as num?)?.toDouble(),
      snr: (json['snr'] as num?)?.toDouble(),
      batteryPct: (json['battery_pct'] as num?)?.toDouble(),
      channel: json['channel'] as int? ?? 1,
      online: json['online'] as bool? ?? true,
    );
  }
}

class CyberdeckHealth {
  const CyberdeckHealth({
    required this.cpuTempC,
    required this.ramUsedPct,
    required this.batteryPct,
    required this.powerSource,
    required this.uptimeSec,
    this.loraChannel = 1,
    this.encryption = 'AES-128-GCM',
  });

  final double cpuTempC;
  final double ramUsedPct;
  final double batteryPct;
  final String powerSource;
  final int uptimeSec;
  final int loraChannel;
  final String encryption;

  factory CyberdeckHealth.fromJson(Map<String, dynamic> json) {
    return CyberdeckHealth(
      cpuTempC: (json['cpu_temp_c'] as num).toDouble(),
      ramUsedPct: (json['ram_used_pct'] as num).toDouble(),
      batteryPct: (json['battery_pct'] as num).toDouble(),
      powerSource: json['power_source'] as String,
      uptimeSec: json['uptime_sec'] as int,
      loraChannel: json['lora_channel'] as int? ?? 1,
      encryption: json['encryption'] as String? ?? 'AES-128-GCM',
    );
  }
}

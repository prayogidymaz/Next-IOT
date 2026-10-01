class FleetDeviceDto {
  FleetDeviceDto({required this.id, required this.name, required this.metadata});

  final String id;
  final String name;
  final List<FleetMetadataItem> metadata;

  factory FleetDeviceDto.fromJson(Map<String, Object?> json) {
    final rawMeta = json['metadata'];
    final items = <FleetMetadataItem>[];
    if (rawMeta is List<Object?>) {
      for (final entry in rawMeta) {
        if (entry is Map<Object?, Object?>) {
          items.add(FleetMetadataItem.fromJson(entry));
        }
      }
    }
    return FleetDeviceDto(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      metadata: items,
    );
  }
}

class FleetMetadataItem {
  FleetMetadataItem({required this.key, required this.value});

  final String key;
  final String value;

  factory FleetMetadataItem.fromJson(Map<Object?, Object?> json) {
    return FleetMetadataItem(
      key: json['key']?.toString() ?? '',
      value: json['value']?.toString() ?? '',
    );
  }
}

class TelemetryBulkResponse {
  TelemetryBulkResponse({required this.accepted, required this.failed});

  final int accepted;
  final int failed;

  factory TelemetryBulkResponse.fromJson(Map<String, Object?> json) {
    return TelemetryBulkResponse(
      accepted: _asInt(json['accepted']),
      failed: _asInt(json['failed']),
    );
  }
}

int _asInt(Object? value) {
  if (value is int) return value;
  if (value is num) return value.toInt();
  return 0;
}

enum GeofenceAction {
  warn('WARN'),
  rtl('RTL'),
  land('LAND');

  const GeofenceAction(this.apiValue);
  final String apiValue;

  static GeofenceAction fromApi(String value) {
    return GeofenceAction.values.firstWhere(
      (a) => a.apiValue == value,
      orElse: () => GeofenceAction.warn,
    );
  }
}

class GeofencePoint {
  const GeofencePoint({required this.lat, required this.lon});

  final double lat;
  final double lon;

  factory GeofencePoint.fromJson(Map<String, dynamic> json) {
    return GeofencePoint(
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {'lat': lat, 'lon': lon};
}

class GeofenceZone {
  const GeofenceZone({
    required this.id,
    required this.tenantId,
    required this.name,
    required this.polygonCoords,
    required this.maxAltitude,
    required this.minAltitude,
    required this.actionOnBreach,
  });

  final String id;
  final String tenantId;
  final String name;
  final List<GeofencePoint> polygonCoords;
  final double maxAltitude;
  final double minAltitude;
  final GeofenceAction actionOnBreach;

  factory GeofenceZone.fromJson(Map<String, dynamic> json) {
    final coords = (json['polygon_coords'] as List<dynamic>? ?? [])
        .map((e) => GeofencePoint.fromJson(e as Map<String, dynamic>))
        .toList();
    return GeofenceZone(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      name: json['name'] as String,
      polygonCoords: coords,
      maxAltitude: (json['max_altitude'] as num).toDouble(),
      minAltitude: (json['min_altitude'] as num).toDouble(),
      actionOnBreach: GeofenceAction.fromApi(json['action_on_breach'] as String),
    );
  }
}

class GeofenceListData {
  const GeofenceListData({required this.count, required this.zones});

  final int count;
  final List<GeofenceZone> zones;

  factory GeofenceListData.fromJson(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>? ?? [])
        .map((e) => GeofenceZone.fromJson(e as Map<String, dynamic>))
        .toList();
    return GeofenceListData(count: json['count'] as int? ?? items.length, zones: items);
  }
}

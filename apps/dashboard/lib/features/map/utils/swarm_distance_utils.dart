import 'dart:math' as math;

import '../../devices/models/device_models.dart';
import '../models/device_map_models.dart';

const double collisionRiskThresholdM = 20.0;
const String collisionRiskWarning = 'COLLISION_RISK_WARNING';
const double metersPerDegLat = 111320.0;

class SwarmNodePosition {
  const SwarmNodePosition({
    required this.deviceId,
    required this.deviceName,
    required this.lat,
    required this.lon,
  });

  final String deviceId;
  final String deviceName;
  final double lat;
  final double lon;
}

class SwarmDistanceLink {
  const SwarmDistanceLink({
    required this.deviceAId,
    required this.deviceBId,
    required this.deviceAName,
    required this.deviceBName,
    required this.distanceM,
    required this.collisionRisk,
    this.warning,
  });

  final String deviceAId;
  final String deviceBId;
  final String deviceAName;
  final String deviceBName;
  final double distanceM;
  final bool collisionRisk;
  final String? warning;
}

double haversineDistanceM(double lat1, double lon1, double lat2, double lon2) {
  final northM = (lat2 - lat1) * metersPerDegLat;
  final cosLat = math.cos((lat1 + lat2) * math.pi / 360);
  final eastM = (lon2 - lon1) * metersPerDegLat * cosLat;
  return math.sqrt(northM * northM + eastM * eastM);
}

List<SwarmNodePosition> swarmNodesFromMarkers(List<DeviceMapMarker> markers) {
  return markers
      .map(
        (m) => SwarmNodePosition(
          deviceId: m.device.id,
          deviceName: m.device.name,
          lat: m.fix.latitude,
          lon: m.fix.longitude,
        ),
      )
      .toList();
}

List<SwarmDistanceLink> computeSwarmLinks(
  List<SwarmNodePosition> nodes, {
  double thresholdM = collisionRiskThresholdM,
}) {
  final links = <SwarmDistanceLink>[];
  for (var i = 0; i < nodes.length; i++) {
    for (var j = i + 1; j < nodes.length; j++) {
      final a = nodes[i];
      final b = nodes[j];
      final distance = haversineDistanceM(a.lat, a.lon, b.lat, b.lon);
      final risk = distance < thresholdM;
      links.add(
        SwarmDistanceLink(
          deviceAId: a.deviceId,
          deviceBId: b.deviceId,
          deviceAName: a.deviceName,
          deviceBName: b.deviceName,
          distanceM: distance,
          collisionRisk: risk,
          warning: risk ? collisionRiskWarning : null,
        ),
      );
    }
  }
  return links;
}

bool markersHaveCollisionRisk(List<DeviceMapMarker> markers) {
  final links = computeSwarmLinks(swarmNodesFromMarkers(markers));
  return links.any((l) => l.collisionRisk);
}

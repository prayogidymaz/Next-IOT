import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/theme/tactical_theme.dart';
import '../utils/swarm_distance_utils.dart';

class SwarmDistanceOverlay extends StatelessWidget {
  const SwarmDistanceOverlay({
    super.key,
    required this.nodes,
    required this.links,
  });

  final List<SwarmNodePosition> nodes;
  final List<SwarmDistanceLink> links;

  static List<Widget> buildMapLayers({
    required List<SwarmNodePosition> nodes,
    required List<SwarmDistanceLink> links,
  }) {
    if (nodes.length < 2 || links.isEmpty) return const [];

    final nodeById = {for (final n in nodes) n.deviceId: n};
    final polylines = <Polyline>[];
    final midMarkers = <Marker>[];

    for (final link in links) {
      final a = nodeById[link.deviceAId];
      final b = nodeById[link.deviceBId];
      if (a == null || b == null) continue;

      final color = link.collisionRisk ? TacticalColors.critical : TacticalColors.borderNeon;
      final pointA = LatLng(a.lat, a.lon);
      final pointB = LatLng(b.lat, b.lon);
      polylines.add(
        Polyline(
          points: [pointA, pointB],
          color: color.withOpacity(link.collisionRisk ? 0.95 : 0.55),
          strokeWidth: link.collisionRisk ? 3.5 : 2,
        ),
      );

      final midLat = (a.lat + b.lat) / 2;
      final midLon = (a.lon + b.lon) / 2;
      midMarkers.add(
        Marker(
          point: LatLng(midLat, midLon),
          width: 72,
          height: 28,
          alignment: Alignment.center,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: (link.collisionRisk ? TacticalColors.critical : TacticalColors.surface).withOpacity(0.92),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: link.collisionRisk ? TacticalColors.critical : TacticalColors.borderNeon,
              ),
            ),
            child: Text(
              link.collisionRisk ? '${link.distanceM.round()}m ⚠' : '${link.distanceM.round()}m',
              style: TextStyle(
                fontSize: 9,
                fontWeight: FontWeight.w800,
                color: link.collisionRisk ? Colors.white : TacticalColors.borderNeon,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
    }

    return [
      if (polylines.isNotEmpty) PolylineLayer(polylines: polylines),
      if (midMarkers.isNotEmpty) MarkerLayer(markers: midMarkers),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final layers = buildMapLayers(nodes: nodes, links: links);
    if (layers.isEmpty) return const SizedBox.shrink();
    return Stack(children: layers);
  }
}

import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/weather_vector_models.dart';

class WindVectorOverlay extends StatelessWidget {
  const WindVectorOverlay({super.key, required this.vectors});

  final List<WindVectorPoint> vectors;

  static List<Widget> buildMapLayers(List<WindVectorPoint> vectors) {
    if (vectors.isEmpty) return const [];

    final polylines = <Polyline>[];
    final markers = <Marker>[];

    for (final vector in vectors) {
      final start = LatLng(vector.lat, vector.lon);
      final end = _arrowEnd(start, vector.windDirectionDeg, vector.windSpeedMs);
      final color = _colorForSpeed(vector.windSpeedMs);

      polylines.add(
        Polyline(
          points: [start, end],
          color: color.withOpacity(0.85),
          strokeWidth: 2 + (vector.windSpeedMs / 8).clamp(0, 3),
        ),
      );

      markers.add(
        Marker(
          point: end,
          width: 18,
          height: 18,
          alignment: Alignment.center,
          child: Transform.rotate(
            angle: _blowRadians(vector.windDirectionDeg),
            child: Icon(Icons.arrow_upward, size: 14, color: color),
          ),
        ),
      );
    }

    return [
      if (polylines.isNotEmpty) PolylineLayer(polylines: polylines),
      if (markers.isNotEmpty) MarkerLayer(markers: markers),
    ];
  }

  static LatLng _arrowEnd(LatLng start, double directionDeg, double speedMs) {
    final blowDeg = (directionDeg + 180) % 360;
    final radians = blowDeg * math.pi / 180;
    const metersPerDegLat = 111320.0;
    final lengthM = (40 + speedMs * 8).clamp(40, 180);
    final dLat = (lengthM * math.cos(radians)) / metersPerDegLat;
    final dLon = (lengthM * math.sin(radians)) /
        (metersPerDegLat * math.cos(start.latitude * math.pi / 180));
    return LatLng(start.latitude + dLat, start.longitude + dLon);
  }

  static double _blowRadians(double directionDeg) {
    final blowDeg = (directionDeg + 180) % 360;
    return blowDeg * math.pi / 180;
  }

  static Color _colorForSpeed(double speedMs) {
    if (speedMs > 15) return TacticalColors.critical;
    if (speedMs >= 10) return TacticalColors.warning;
    return TacticalColors.success;
  }

  @override
  Widget build(BuildContext context) {
    final layers = buildMapLayers(vectors);
    if (layers.isEmpty) return const SizedBox.shrink();
    return Stack(children: layers);
  }
}

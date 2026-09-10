import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../models/signal_heatmap_models.dart';
import '../utils/signal_strength_utils.dart';

class SignalHeatmapLayer extends StatelessWidget {
  const SignalHeatmapLayer({super.key, required this.points});

  final List<SignalHeatmapPoint> points;

  static List<Widget> buildMapLayers(List<SignalHeatmapPoint> points) {
    if (points.isEmpty) return const [];

    final polylines = <Polyline>[];
    for (var i = 1; i < points.length; i++) {
      final prev = points[i - 1];
      final curr = points[i];
      final avgRssi = (prev.rssi + curr.rssi) / 2;
      polylines.add(
        Polyline(
          points: [
            LatLng(prev.lat, prev.lon),
            LatLng(curr.lat, curr.lon),
          ],
          color: colorForRssi(avgRssi),
          strokeWidth: 5,
        ),
      );
    }

    final circles = points.map((point) {
      final color = colorForRssi(point.rssi);
      return CircleMarker(
        point: LatLng(point.lat, point.lon),
        radius: 28,
        useRadiusInMeter: false,
        color: color.withOpacity(0.28),
        borderColor: color.withOpacity(0.85),
        borderStrokeWidth: 2,
      );
    }).toList();

    return [
      if (polylines.isNotEmpty) PolylineLayer(polylines: polylines),
      CircleLayer(circles: circles),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final layers = buildMapLayers(points);
    if (layers.isEmpty) return const SizedBox.shrink();
    return Stack(children: layers);
  }
}

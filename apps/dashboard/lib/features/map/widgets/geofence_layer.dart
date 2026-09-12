import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../mission/models/geofence_models.dart';

class GeofenceLayer extends StatelessWidget {
  const GeofenceLayer({super.key, required this.zones});

  final List<GeofenceZone> zones;

  static List<Widget> buildMapLayers(List<GeofenceZone> zones) {
    final layers = <Widget>[];

    for (final zone in zones) {
      if (zone.polygonCoords.length < 3) continue;
      layers.add(
        PolygonLayer(
          polygons: [
            Polygon(
              points: zone.polygonCoords.map((p) => LatLng(p.lat, p.lon)).toList(),
              color: TacticalColors.critical.withOpacity(0.12),
              borderColor: TacticalColors.critical.withOpacity(0.85),
              borderStrokeWidth: 2.5,
            ),
          ],
        ),
      );
    }

    return layers;
  }

  @override
  Widget build(BuildContext context) {
    final layers = buildMapLayers(zones);
    if (layers.isEmpty) return const SizedBox.shrink();
    return Stack(children: layers);
  }
}

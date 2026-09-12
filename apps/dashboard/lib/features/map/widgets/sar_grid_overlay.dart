import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../mission/models/sar_grid_models.dart';

class SarGridOverlay extends StatelessWidget {
  const SarGridOverlay({super.key, required this.result});

  final SarGridResult result;

  static List<Widget> buildMapLayers(SarGridResult result) {
    final layers = <Widget>[];

    for (final area in result.searchAreas) {
      if (area.points.length < 3) continue;
      layers.add(
        PolygonLayer(
          polygons: [
            Polygon(
              points: area.points.map((p) => LatLng(p.lat, p.lon)).toList(),
              color: TacticalColors.warning.withOpacity(0.08),
              borderColor: TacticalColors.warning.withOpacity(0.7),
              borderStrokeWidth: 2,
            ),
          ],
        ),
      );
    }

    final trackPolylines = result.tracks.map((track) {
      return Polyline(
        points: track.points.map((p) => LatLng(p.lat, p.lon)).toList(),
        color: TacticalColors.cyan.withOpacity(0.85),
        strokeWidth: 2.5,
      );
    }).toList();

    if (trackPolylines.isNotEmpty) {
      layers.add(PolylineLayer(polylines: trackPolylines));
    }

    final lkpMarker = MarkerLayer(
      markers: [
        Marker(
          point: LatLng(result.lkp.lat, result.lkp.lon),
          width: 48,
          height: 48,
          alignment: Alignment.center,
          child: Container(
            decoration: BoxDecoration(
              color: TacticalColors.critical.withOpacity(0.2),
              shape: BoxShape.circle,
              border: Border.all(color: TacticalColors.critical, width: 2),
            ),
            child: const Icon(Icons.location_searching, color: TacticalColors.critical, size: 22),
          ),
        ),
      ],
    );
    layers.add(lkpMarker);

    return layers;
  }

  @override
  Widget build(BuildContext context) {
    final layers = buildMapLayers(result);
    if (layers.isEmpty) return const SizedBox.shrink();
    return Stack(children: layers);
  }
}

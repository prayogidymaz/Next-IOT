import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../devices/models/device_models.dart';
import '../../telemetry/models/telemetry_models.dart';
import '../models/device_map_models.dart';
import '../utils/gps_utils.dart';
import 'device_map_marker_widget.dart';
import 'tactical_tile_layer.dart';
import 'telemetry_map_overlay.dart';

class DeviceMapView extends StatefulWidget {
  const DeviceMapView({
    super.key,
    required this.device,
    this.telemetry,
    this.hasActiveAlert = false,
    this.height = 320,
  });

  final Device device;
  final TelemetryLatest? telemetry;
  final bool hasActiveAlert;
  final double height;

  @override
  State<DeviceMapView> createState() => _DeviceMapViewState();
}

class _DeviceMapViewState extends State<DeviceMapView> {
  final MapController _mapController = MapController();

  DeviceMapMarker? get _marker => buildMapMarker(
        device: widget.device,
        telemetry: widget.telemetry,
        hasActiveAlert: widget.hasActiveAlert,
      );

  void _centerOnDevice() {
    final marker = _marker;
    if (marker == null) return;
    _mapController.move(
      LatLng(marker.fix.latitude, marker.fix.longitude),
      16,
    );
  }

  @override
  Widget build(BuildContext context) {
    final marker = _marker;

    if (marker == null) {
      return SizedBox(
        height: widget.height,
        child: Center(
          child: Text(
            'No GPS fix available for this device.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
      );
    }

    final center = LatLng(marker.fix.latitude, marker.fix.longitude);

    return SizedBox(
      height: widget.height,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Stack(
          children: [
            if (isFlutterTestEnvironment)
              const ColoredBox(color: TacticalColors.surface),
            FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: center,
                initialZoom: 15,
                minZoom: 3,
                maxZoom: 18,
              ),
              children: [
                const TacticalTileLayer(),
                MarkerLayer(
                  markers: [
                    Marker(
                      point: center,
                      width: 80,
                      height: 80,
                      alignment: Alignment.topCenter,
                      child: DeviceMapMarkerWidget(
                        marker: marker,
                        isSelected: true,
                        compact: true,
                        onTap: () {},
                      ),
                    ),
                  ],
                ),
              ],
            ),
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: TelemetryMapOverlay(
                marker: marker,
                onCenter: _centerOnDevice,
                compact: true,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../mission/providers/mission_provider.dart';
import '../../mission/widgets/mission_control_overlay.dart';
import '../../mission/widgets/waypoint_marker.dart';
import '../widgets/tactical_tile_layer.dart' show TacticalTileLayer, isFlutterTestEnvironment;
import '../../devices/providers/device_provider.dart';
import '../models/device_map_models.dart';
import '../config/tile_url_resolver.dart';
import '../providers/map_provider.dart';
import '../providers/map_tile_provider.dart';
import '../providers/signal_heatmap_provider.dart';
import '../widgets/signal_heatmap_layer.dart';
import '../widgets/signal_heatmap_legend.dart';
import '../utils/gps_utils.dart';
import '../widgets/device_map_marker_widget.dart';
import '../widgets/telemetry_map_overlay.dart';
import '../../telemetry/providers/telemetry_anomaly_provider.dart';
import '../../telemetry/widgets/anomaly_alert_badge.dart';
import '../../telemetry/widgets/anomaly_alert_panel.dart';

class TacticalMapScreen extends ConsumerStatefulWidget {
  const TacticalMapScreen({super.key});

  @override
  ConsumerState<TacticalMapScreen> createState() => _TacticalMapScreenState();
}

class _TacticalMapScreenState extends ConsumerState<TacticalMapScreen> {
  final MapController _mapController = MapController();
  Timer? _silentRefreshTimer;
  int _silentRefreshTick = 0;
  static const _liveRefreshInterval = Duration(seconds: 2);

  @override
  void initState() {
    super.initState();
    Future.microtask(_refreshMap);
    _silentRefreshTimer = Timer.periodic(_liveRefreshInterval, (_) => _silentRefreshMap());
  }

  @override
  void dispose() {
    _silentRefreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _refreshMap() async {
    final devices = ref.read(deviceProvider).devices;
    if (devices.isEmpty) {
      await ref.read(deviceProvider.notifier).loadDevices();
    }
    await ref.read(tacticalMapProvider.notifier).loadMarkers();
  }

  Future<void> _silentRefreshMap() async {
    _silentRefreshTick += 1;
    if (_silentRefreshTick % 5 == 0) {
      await ref.read(deviceProvider.notifier).loadDevices();
    }
    await ref.read(tacticalMapProvider.notifier).refreshMarkersSilent();
    final deviceId = ref.read(tacticalMapProvider).selectedDeviceId;
    if (deviceId != null) {
      await ref.read(telemetryAnomalyProvider.notifier).loadForDevice(deviceId);
    }
  }

  void _centerOnSelected() {
    final selected = ref.read(tacticalMapProvider).selected;
    if (selected == null) return;
    _mapController.move(
      LatLng(selected.fix.latitude, selected.fix.longitude),
      16,
    );
  }

  LatLng _initialCenter(List<DeviceMapMarker> markers) {
    if (markers.isEmpty) {
      return const LatLng(kDefaultMapLatitude, kDefaultMapLongitude);
    }
    final first = markers.first;
    return LatLng(first.fix.latitude, first.fix.longitude);
  }

  void _onMapTap(TapPosition tapPosition, LatLng point) {
    final mission = ref.read(missionPlannerProvider);
    if (mission.plannerMode) {
      ref.read(missionPlannerProvider.notifier).addWaypoint(point);
      return;
    }
    ref.read(tacticalMapProvider.notifier).selectDevice(null);
  }

  @override
  Widget build(BuildContext context) {
    final mapState = ref.watch(tacticalMapProvider);
    final mission = ref.watch(missionPlannerProvider);
    final tileMode = ref.watch(mapTileModeProvider);
    final heatmap = ref.watch(signalHeatmapProvider);
    final anomalies = ref.watch(telemetryAnomalyProvider);
    final selected = mapState.selected;

    ref.listen(tacticalMapProvider.select((s) => s.selectedDeviceId), (prev, next) {
      if (next != null) {
        ref.read(missionPlannerProvider.notifier).setTargetDevice(next);
        if (ref.read(signalHeatmapProvider).enabled) {
          ref.read(signalHeatmapProvider.notifier).loadForDevice(next);
        }
        ref.read(telemetryAnomalyProvider.notifier).loadForDevice(next);
      }
    });

    final showMap = mapState.markers.isNotEmpty || mission.plannerMode;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 8,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Text('TACTICAL MAP', style: Theme.of(context).textTheme.titleLarge),
            FilterChip(
              label: const Text('Mission Planner'),
              selected: mission.plannerMode,
              onSelected: (_) => ref.read(missionPlannerProvider.notifier).togglePlannerMode(),
              selectedColor: TacticalColors.cyan.withOpacity(0.2),
              checkmarkColor: TacticalColors.borderNeon,
            ),
            FilterChip(
              label: Text(tileMode == MapTileMode.offline ? 'Offline Map' : 'Online Map'),
              selected: tileMode == MapTileMode.offline,
              onSelected: (_) => ref.read(mapTileModeProvider.notifier).toggle(),
              selectedColor: TacticalColors.warning.withOpacity(0.2),
              checkmarkColor: TacticalColors.warning,
              avatar: Icon(
                tileMode == MapTileMode.offline ? Icons.offline_bolt : Icons.public,
                size: 16,
                color: tileMode == MapTileMode.offline ? TacticalColors.warning : TacticalColors.borderNeon,
              ),
            ),
            if (anomalies.hasAnomalies)
              AnomalyAlertBadge(
                count: anomalies.count,
                hasCritical: anomalies.hasCritical,
              ),
            FilterChip(
              label: const Text('Signal Heatmap'),
              selected: heatmap.enabled,
              onSelected: (_) async {
                await ref.read(signalHeatmapProvider.notifier).toggle();
                if (!ref.read(signalHeatmapProvider).enabled) return;
                final targetId = mapState.selectedDeviceId ??
                    (mapState.markers.isNotEmpty ? mapState.markers.first.device.id : null);
                if (targetId != null) {
                  await ref.read(signalHeatmapProvider.notifier).loadForDevice(targetId);
                }
              },
              selectedColor: TacticalColors.success.withOpacity(0.2),
              checkmarkColor: TacticalColors.success,
              avatar: Icon(
                Icons.cell_tower,
                size: 16,
                color: heatmap.enabled ? TacticalColors.success : TacticalColors.textSecondary,
              ),
            ),
            if (selected != null && !mission.plannerMode)
              OutlinedButton.icon(
                onPressed: _centerOnSelected,
                icon: const Icon(Icons.my_location, size: 18),
                label: const Text('Center on Device'),
              ),
            IconButton(
              tooltip: 'Refresh map',
              onPressed: mapState.isLoading ? null : _refreshMap,
              icon: mapState.isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.refresh),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: Stack(
              children: [
                if (isFlutterTestEnvironment)
                  const ColoredBox(color: TacticalColors.surface),
                if (mapState.isLoading && mapState.markers.isEmpty && !mission.plannerMode)
                  const Center(child: CircularProgressIndicator())
                else if (mapState.error != null && mapState.markers.isEmpty && !mission.plannerMode)
                  Center(child: Text(mapState.error!))
                else if (!showMap)
                  const Center(child: Text('No devices with GPS telemetry yet.'))
                else
                  FlutterMap(
                    mapController: _mapController,
                    options: MapOptions(
                      initialCenter: _initialCenter(mapState.markers),
                      initialZoom: 13,
                      minZoom: 3,
                      maxZoom: 18,
                      onTap: _onMapTap,
                    ),
                    children: [
                      const TacticalTileLayer(),
                      if (heatmap.enabled && heatmap.points.isNotEmpty)
                        ...SignalHeatmapLayer.buildMapLayers(heatmap.points),
                      if (mission.waypoints.length >= 2)
                        PolylineLayer(
                          polylines: [
                            Polyline(
                              points: mission.waypoints
                                  .map((w) => LatLng(w.latitude, w.longitude))
                                  .toList(),
                              color: TacticalColors.borderNeon,
                              strokeWidth: 3,
                            ),
                          ],
                        ),
                      if (mapState.markers.isNotEmpty)
                        MarkerLayer(
                          markers: mapState.markers.map((marker) {
                            final point = LatLng(marker.fix.latitude, marker.fix.longitude);
                            final isSelected = marker.device.id == mapState.selectedDeviceId;
                            return Marker(
                              point: point,
                              width: 90,
                              height: 90,
                              alignment: Alignment.topCenter,
                              child: DeviceMapMarkerWidget(
                                marker: marker,
                                isSelected: isSelected,
                                compact: true,
                                anomalyCount: isSelected ? anomalies.count : 0,
                                hasCriticalAnomaly: isSelected && anomalies.hasCritical,
                                onTap: () => ref
                                    .read(tacticalMapProvider.notifier)
                                    .selectDevice(marker.device.id),
                              ),
                            );
                          }).toList(),
                        ),
                      if (mission.waypoints.isNotEmpty)
                        MarkerLayer(
                          markers: mission.waypoints.map((wp) {
                            return Marker(
                              point: LatLng(wp.latitude, wp.longitude),
                              width: 48,
                              height: 48,
                              alignment: Alignment.center,
                              child: WaypointMarker(label: wp.label),
                            );
                          }).toList(),
                        ),
                    ],
                  ),
                const MissionControlOverlay(),
                if (selected != null && !mission.plannerMode)
                  Positioned(
                    left: 0,
                    right: 0,
                    bottom: 0,
                    child: TelemetryMapOverlay(
                      marker: selected,
                      onCenter: _centerOnSelected,
                    ),
                  ),
                if (anomalies.hasAnomalies)
                  Positioned(
                    top: 12,
                    left: 12,
                    child: AnomalyAlertPanel(
                      anomalies: anomalies.items,
                      isLoading: anomalies.isLoading,
                    ),
                  ),
                if (heatmap.enabled)
                  Positioned(
                    left: 12,
                    bottom: selected != null && !mission.plannerMode ? 120 : 12,
                    child: SignalHeatmapLegend(
                      pointCount: heatmap.points.length,
                      hours: heatmap.hours,
                    ),
                  ),
                Positioned(
                  top: 12,
                  right: 12,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: TacticalColors.surface.withOpacity(0.9),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: TacticalColors.border),
                    ),
                    child: Text(
                      '${mapState.markers.length} GPS FIX',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: TacticalColors.borderNeon,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

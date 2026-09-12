import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../mission/providers/mission_provider.dart';
import '../../mission/providers/sar_grid_provider.dart';
import '../../mission/widgets/emergency_fail_safe_dialog.dart';
import '../../mission/widgets/mission_control_overlay.dart';
import '../../mission/widgets/waypoint_marker.dart';
import '../widgets/sar_grid_overlay.dart';
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
import '../../telemetry/providers/flight_replay_provider.dart';
import '../../telemetry/providers/telemetry_anomaly_provider.dart';
import '../../telemetry/widgets/anomaly_alert_badge.dart';
import '../../telemetry/widgets/anomaly_alert_panel.dart';
import '../../telemetry/widgets/telemetry_export_dialog.dart';
import '../providers/swarm_overlay_provider.dart';
import '../utils/swarm_distance_utils.dart';
import '../widgets/flight_replay_control_bar.dart';
import '../widgets/swarm_distance_overlay.dart';
import '../../video/models/video_feed_models.dart';
import '../../video/providers/video_feed_provider.dart';
import '../../video/widgets/tactical_video_panel.dart';
import '../../mavlink/providers/mavlink_hud_provider.dart';
import '../../mavlink/providers/mavlink_provider.dart';
import '../providers/weather_vector_provider.dart';
import '../widgets/flight_safety_weather_card.dart';
import '../widgets/wind_vector_overlay.dart';
import '../../mission/providers/geofence_provider.dart';
import '../../mission/providers/sar_incident_provider.dart';
import '../../mission/widgets/sar_incident_response_panel.dart';
import '../widgets/geofence_breach_warning.dart';
import '../widgets/geofence_layer.dart';
import '../widgets/incident_target_marker.dart';

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
    if (ref.read(flightReplayProvider).isPlaying) return;

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

  List<DeviceMapMarker> _effectiveMarkers(
    List<DeviceMapMarker> markers,
    FlightReplayState replay,
  ) {
    if (!replay.enabled || replay.currentPosition == null || replay.deviceId == null) {
      return markers;
    }
    final replayPoint = replay.currentPosition!.point;
    final replayPos = replay.currentPosition!;
    return markers.map((marker) {
      if (marker.device.id != replay.deviceId) return marker;
      return DeviceMapMarker(
        device: marker.device,
        fix: DeviceGpsFix(
          latitude: replayPoint.latitude,
          longitude: replayPoint.longitude,
          altitudeM: replayPos.alt ?? marker.fix.altitudeM,
          speed: replayPos.speed ?? marker.fix.speed,
        ),
        battery: marker.battery,
        roll: marker.roll,
        pitch: marker.pitch,
        yaw: replayPos.heading ?? marker.yaw,
        speed: replayPos.speed ?? marker.speed,
        hasActiveAlert: marker.hasActiveAlert,
        recordedAt: marker.recordedAt,
      );
    }).toList();
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

  LatLng? _weatherCenter(TacticalMapState mapState) {
    final selected = mapState.selected;
    if (selected != null) {
      return LatLng(selected.fix.latitude, selected.fix.longitude);
    }
    if (mapState.markers.isNotEmpty) {
      final first = mapState.markers.first;
      return LatLng(first.fix.latitude, first.fix.longitude);
    }
    return null;
  }

  Future<void> _loadWeatherForMap(TacticalMapState mapState) async {
    final center = _weatherCenter(mapState);
    if (center == null) return;
    await ref.read(weatherVectorProvider.notifier).loadForLocation(
          lat: center.latitude,
          lon: center.longitude,
        );
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
    final sarGrid = ref.watch(sarGridProvider);
    final replay = ref.watch(flightReplayProvider);
    final swarmOverlay = ref.watch(swarmOverlayProvider);
    final videoFeed = ref.watch(videoFeedProvider);
    final mavlink = ref.watch(mavlinkProvider);
    final mavlinkHud = ref.watch(mavlinkHudProvider);
    final weather = ref.watch(weatherVectorProvider);
    final geofence = ref.watch(geofenceProvider);
    final sarIncidents = ref.watch(sarIncidentProvider);
    final selected = mapState.selected;
    final activeIncidents = sarIncidents.activeIncidents;
    final hasGeofenceBreach = anomalies.items.any((a) => a.anomalyType == 'geofence_breach');
    final displayMarkers = _effectiveMarkers(mapState.markers, replay);
    final swarmNodes = swarmNodesFromMarkers(displayMarkers);
    final swarmLinks = computeSwarmLinks(swarmNodes);
    final hasSwarmRisk = swarmLinks.any((l) => l.collisionRisk);

    ref.listen(tacticalMapProvider.select((s) => s.selectedDeviceId), (prev, next) {
      if (next != null) {
        ref.read(missionPlannerProvider.notifier).setTargetDevice(next);
        if (ref.read(signalHeatmapProvider).enabled) {
          ref.read(signalHeatmapProvider.notifier).loadForDevice(next);
        }
        ref.read(telemetryAnomalyProvider.notifier).loadForDevice(next);
        ref.read(mavlinkProvider.notifier).loadForDevice(
              next,
              marker: ref.read(tacticalMapProvider).selected,
            );
        if (ref.read(weatherVectorProvider).enabled) {
          final marker = ref.read(tacticalMapProvider).selected;
          if (marker != null) {
            ref.read(weatherVectorProvider.notifier).loadForLocation(
                  lat: marker.fix.latitude,
                  lon: marker.fix.longitude,
                );
          }
        }
      } else {
        ref.read(mavlinkProvider.notifier).clear();
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
            FilterChip(
              label: Text(hasGeofenceBreach ? 'Geofence BREACH' : 'Geofence'),
              selected: geofence.enabled,
              onSelected: (_) async {
                await ref.read(geofenceProvider.notifier).toggle();
              },
              selectedColor: hasGeofenceBreach
                  ? TacticalColors.critical.withOpacity(0.25)
                  : TacticalColors.critical.withOpacity(0.12),
              checkmarkColor: TacticalColors.critical,
              avatar: Icon(
                Icons.fence,
                size: 16,
                color: hasGeofenceBreach
                    ? TacticalColors.critical
                    : (geofence.enabled ? TacticalColors.critical : TacticalColors.textSecondary),
              ),
            ),
            FilterChip(
              label: const Text('Wind Vectors'),
              selected: weather.enabled,
              onSelected: (_) async {
                await ref.read(weatherVectorProvider.notifier).toggle();
                if (ref.read(weatherVectorProvider).enabled) {
                  await _loadWeatherForMap(mapState);
                }
              },
              selectedColor: TacticalColors.borderNeon.withOpacity(0.15),
              checkmarkColor: TacticalColors.borderNeon,
              avatar: Icon(
                Icons.air,
                size: 16,
                color: weather.enabled ? TacticalColors.borderNeon : TacticalColors.textSecondary,
              ),
            ),
            if (weather.enabled || weather.data != null)
              FlightSafetyWeatherCard(
                data: weather.data,
                isLoading: weather.isLoading,
                compact: true,
              ),
            if (selected != null && !mission.plannerMode)
              OutlinedButton.icon(
                onPressed: _centerOnSelected,
                icon: const Icon(Icons.my_location, size: 18),
                label: const Text('Center on Device'),
              ),
            FilterChip(
              label: Text(mavlinkHud.enabled ? 'MAVLink HUD' : 'MAVLink HUD Off'),
              selected: mavlinkHud.enabled,
              onSelected: selected != null ? (_) => ref.read(mavlinkHudProvider.notifier).toggle() : null,
              selectedColor: TacticalColors.success.withOpacity(0.2),
              checkmarkColor: TacticalColors.success,
              avatar: Icon(
                Icons.flight,
                size: 16,
                color: mavlinkHud.enabled ? TacticalColors.success : TacticalColors.textSecondary,
              ),
            ),
            FilterChip(
              label: Text(videoFeed.enabled ? 'HUD ON' : 'HUD / AI Stream'),
              selected: videoFeed.enabled,
              onSelected: (_) async {
                await ref.read(videoFeedProvider.notifier).toggleForDevice(mapState.selectedDeviceId);
              },
              selectedColor: TacticalColors.cyan.withOpacity(0.25),
              checkmarkColor: TacticalColors.cyan,
              avatar: Icon(
                Icons.videocam,
                size: 16,
                color: videoFeed.enabled ? TacticalColors.cyan : TacticalColors.textSecondary,
              ),
            ),
            FilterChip(
              label: Text(replay.enabled ? 'Replay ON' : 'Flight Replay'),
              selected: replay.enabled,
              onSelected: (_) async {
                await ref.read(flightReplayProvider.notifier).toggleForDevice(mapState.selectedDeviceId);
              },
              selectedColor: TacticalColors.cyan.withOpacity(0.2),
              checkmarkColor: TacticalColors.cyan,
              avatar: Icon(
                Icons.play_circle_outline,
                size: 16,
                color: replay.enabled ? TacticalColors.cyan : TacticalColors.textSecondary,
              ),
            ),
            FilterChip(
              label: Text(hasSwarmRisk ? 'Swarm RISK' : 'Swarm Matrix'),
              selected: swarmOverlay.enabled,
              onSelected: displayMarkers.length >= 2
                  ? (_) => ref.read(swarmOverlayProvider.notifier).toggle()
                  : null,
              selectedColor: hasSwarmRisk
                  ? TacticalColors.critical.withOpacity(0.25)
                  : TacticalColors.borderNeon.withOpacity(0.15),
              checkmarkColor: hasSwarmRisk ? TacticalColors.critical : TacticalColors.borderNeon,
              avatar: Icon(
                Icons.hub,
                size: 16,
                color: hasSwarmRisk
                    ? TacticalColors.critical
                    : (swarmOverlay.enabled ? TacticalColors.borderNeon : TacticalColors.textSecondary),
              ),
            ),
            FilterChip(
              label: Text(
                activeIncidents.isNotEmpty
                    ? 'SAR Room (${activeIncidents.length})'
                    : 'SAR Incident Room',
              ),
              selected: sarIncidents.panelOpen,
              onSelected: (_) => ref.read(sarIncidentProvider.notifier).togglePanel(),
              selectedColor: TacticalColors.critical.withOpacity(0.22),
              checkmarkColor: TacticalColors.critical,
              avatar: Icon(
                Icons.emergency_share,
                size: 16,
                color: activeIncidents.isNotEmpty || sarIncidents.panelOpen
                    ? TacticalColors.critical
                    : TacticalColors.textSecondary,
              ),
            ),
            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                foregroundColor: TacticalColors.critical,
                side: BorderSide(color: TacticalColors.critical.withOpacity(0.6)),
              ),
              onPressed: () => showEmergencyFailSafeDialog(context, ref),
              icon: const Icon(Icons.emergency, size: 18),
              label: const Text('Fail-Safe'),
            ),
            if (sarGrid.result != null)
              FilterChip(
                label: Text('SAR Grid (${sarGrid.result!.waypoints.length} WP)'),
                selected: sarGrid.visible,
                onSelected: (_) => ref.read(sarGridProvider.notifier).toggleVisibility(),
                selectedColor: TacticalColors.cyan.withOpacity(0.2),
                checkmarkColor: TacticalColors.cyan,
                avatar: Icon(
                  Icons.grid_on,
                  size: 16,
                  color: sarGrid.visible ? TacticalColors.cyan : TacticalColors.textSecondary,
                ),
              ),
            FilterChip(
              label: const Text('Export Data'),
              selected: false,
              onSelected: mapState.selectedDeviceId != null
                  ? (_) => TelemetryExportDialog.show(
                        context,
                        deviceId: mapState.selectedDeviceId!,
                        deviceName: selected?.device.name,
                      )
                  : null,
              avatar: Icon(
                Icons.download,
                size: 16,
                color: mapState.selectedDeviceId != null
                    ? TacticalColors.cyan
                    : TacticalColors.textSecondary,
              ),
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
          child: Column(
            children: [
              Expanded(
                flex: videoFeed.enabled && videoFeed.layout == VideoPanelLayout.splitScreen ? 3 : 1,
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
                      if (weather.enabled && weather.data != null && weather.data!.vectors.isNotEmpty)
                        ...WindVectorOverlay.buildMapLayers(weather.data!.vectors),
                      if (geofence.enabled && geofence.zones.isNotEmpty)
                        ...GeofenceLayer.buildMapLayers(geofence.zones),
                      if (sarGrid.visible && sarGrid.result != null)
                        ...SarGridOverlay.buildMapLayers(sarGrid.result!),
                      if (replay.enabled && replay.trailPoints.length >= 2)
                        PolylineLayer(
                          polylines: [
                            Polyline(
                              points: replay.trailPoints,
                              color: TacticalColors.cyan.withOpacity(0.75),
                              strokeWidth: 4,
                            ),
                          ],
                        ),
                      if (swarmOverlay.enabled && swarmLinks.isNotEmpty)
                        ...SwarmDistanceOverlay.buildMapLayers(
                          nodes: swarmNodes,
                          links: swarmLinks,
                        ),
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
                      if (displayMarkers.isNotEmpty)
                        MarkerLayer(
                          markers: displayMarkers.map((marker) {
                            final point = LatLng(marker.fix.latitude, marker.fix.longitude);
                            final isSelected = marker.device.id == mapState.selectedDeviceId;
                            final isReplayTarget =
                                replay.enabled && marker.device.id == replay.deviceId;
                            return Marker(
                              point: point,
                              width: 90,
                              height: 90,
                              alignment: Alignment.topCenter,
                              child: DeviceMapMarkerWidget(
                                marker: marker,
                                isSelected: isSelected || isReplayTarget,
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
                      if (activeIncidents.isNotEmpty)
                        MarkerLayer(
                          markers: activeIncidents.map((incident) {
                            return Marker(
                              point: LatLng(incident.targetLat, incident.targetLon),
                              width: 72,
                              height: 72,
                              alignment: Alignment.bottomCenter,
                              child: IncidentTargetMarker(
                                incident: incident,
                                isSelected: sarIncidents.selectedIncidentId == incident.id,
                                onTap: () => ref.read(sarIncidentProvider.notifier).selectIncident(incident.id),
                              ),
                            );
                          }).toList(),
                        ),
                    ],
                  ),
                const MissionControlOverlay(),
                if (selected != null && !mission.plannerMode && !replay.enabled)
                  Positioned(
                    left: 0,
                    right: 0,
                    bottom: 0,
                    child: TelemetryMapOverlay(
                      marker: selected,
                      onCenter: _centerOnSelected,
                      mavlinkStatus: mavlink.status,
                      showMavlinkHud: mavlinkHud.enabled,
                    ),
                  ),
                if (hasGeofenceBreach)
                  const Positioned(
                    top: 12,
                    left: 12,
                    child: GeofenceBreachWarning(),
                  ),
                if (anomalies.hasAnomalies)
                  Positioned(
                    top: hasGeofenceBreach ? 72 : 12,
                    left: 12,
                    child: AnomalyAlertPanel(
                      anomalies: anomalies.items,
                      isLoading: anomalies.isLoading,
                      onGenerateSarGrid: (lat, lon) async {
                        await ref.read(sarGridProvider.notifier).generateFromLkp(lat: lat, lon: lon);
                        _mapController.move(LatLng(lat, lon), 15);
                      },
                    ),
                  ),
                if (sarGrid.isLoading)
                  Positioned(
                    top: 12,
                    right: 60,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: TacticalColors.surface.withOpacity(0.9),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: TacticalColors.cyan),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(
                            width: 14,
                            height: 14,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                          SizedBox(width: 8),
                          Text('Generating SAR grid...', style: TextStyle(fontSize: 11)),
                        ],
                      ),
                    ),
                  ),
                if (sarIncidents.panelOpen)
                  Positioned(
                    right: 12,
                    bottom: selected != null && !mission.plannerMode ? 130 : 12,
                    child: SarIncidentResponsePanel(
                      selectedDeviceId: mapState.selectedDeviceId,
                      onCenterIncident: (incident) {
                        _mapController.move(LatLng(incident.targetLat, incident.targetLon), 16);
                      },
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
                if (videoFeed.enabled && videoFeed.layout == VideoPanelLayout.pip)
                  Positioned(
                    right: 12,
                    bottom: selected != null && !mission.plannerMode && !replay.enabled ? 132 : 12,
                    width: 280,
                    height: 168,
                    child: TacticalVideoPanel(
                      streamInfo: videoFeed.streamInfo,
                      currentFrame: videoFeed.currentFrame,
                      isConnecting: videoFeed.isConnecting,
                      compact: true,
                      onToggleLayout: ref.read(videoFeedProvider.notifier).toggleLayout,
                      onClose: ref.read(videoFeedProvider.notifier).stop,
                    ),
                  ),
                  ],
                ),
              ),
            ),
              if (videoFeed.enabled && videoFeed.layout == VideoPanelLayout.splitScreen) ...[
                const SizedBox(height: 8),
                SizedBox(
                  height: 200,
                  child: TacticalVideoPanel(
                    streamInfo: videoFeed.streamInfo,
                    currentFrame: videoFeed.currentFrame,
                    isConnecting: videoFeed.isConnecting,
                    onToggleLayout: ref.read(videoFeedProvider.notifier).toggleLayout,
                    onClose: ref.read(videoFeedProvider.notifier).stop,
                  ),
                ),
              ],
              const FlightReplayControlBar(),
            ],
          ),
        ),
      ],
    );
  }
}

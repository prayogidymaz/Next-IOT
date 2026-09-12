import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/glowing_led_badge.dart';
import '../../mavlink/models/mavlink_models.dart';
import '../../mavlink/widgets/mavlink_attitude_horizon.dart';
import '../../mavlink/widgets/mavlink_status_badge.dart';
import '../models/device_map_models.dart';

class TelemetryMapOverlay extends StatelessWidget {
  const TelemetryMapOverlay({
    super.key,
    required this.marker,
    this.onCenter,
    this.compact = false,
    this.mavlinkStatus,
    this.showMavlinkHud = true,
  });

  final DeviceMapMarker marker;
  final VoidCallback? onCenter;
  final bool compact;
  final MavlinkStatus? mavlinkStatus;
  final bool showMavlinkHud;

  String _fmt(double? value, {String suffix = ''}) {
    if (value == null) return '—';
    return '${value.toStringAsFixed(value.truncateToDouble() == value ? 0 : 1)}$suffix';
  }

  MavlinkAttitude get _attitude {
    final metrics = {
      ...?mavlinkStatus?.metrics,
      if (marker.roll != null) 'roll': marker.roll!,
      if (marker.pitch != null) 'pitch': marker.pitch!,
      if (marker.yaw != null) 'yaw': marker.yaw!,
    };
    return MavlinkAttitude.fromMetrics(metrics);
  }

  bool get _mavlinkConnected => mavlinkStatus?.connected ?? false;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: TacticalColors.surface.withOpacity(0.92),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: TacticalColors.borderNeon.withOpacity(0.5)),
        boxShadow: [
          BoxShadow(color: TacticalColors.cyanGlow, blurRadius: 12),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  marker.device.name.toUpperCase(),
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: TacticalColors.borderNeon,
                      ),
                ),
              ),
              if (_mavlinkConnected)
                Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: MavlinkStatusBadge(
                    connected: true,
                    protocolVersion: mavlinkStatus?.protocolVersion ?? '2.0',
                    compact: compact,
                  ),
                ),
              GlowingLedBadge(
                label: marker.status.name,
                color: marker.status.color,
                pulse: marker.status.pulse,
              ),
            ],
          ),
          if (!compact) ...[
            const SizedBox(height: 8),
            Text(
              'GPS: ${marker.fix.latitude.toStringAsFixed(6)}, ${marker.fix.longitude.toStringAsFixed(6)}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            Text(
              'ALT: ${_fmt(marker.fix.altitudeM, suffix: ' m')}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
          if (showMavlinkHud && (_mavlinkConnected || marker.roll != null)) ...[
            const SizedBox(height: 10),
            Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                MavlinkAttitudeHorizon(attitude: _attitude, size: compact ? 96 : 120),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'MAVLink ATTITUDE',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: TacticalColors.cyan,
                              fontWeight: FontWeight.w800,
                            ),
                      ),
                      const SizedBox(height: 6),
                      _MetricChip(label: 'ROLL', value: _fmt(_attitude.roll, suffix: '°')),
                      const SizedBox(height: 4),
                      _MetricChip(label: 'PITCH', value: _fmt(_attitude.pitch, suffix: '°')),
                      const SizedBox(height: 4),
                      _MetricChip(label: 'YAW', value: _fmt(_attitude.yaw, suffix: '°')),
                    ],
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 10),
          Wrap(
            spacing: 12,
            runSpacing: 8,
            children: [
              _MetricChip(label: 'SPEED', value: _fmt(marker.speed, suffix: ' m/s')),
              _MetricChip(label: 'BATT', value: _fmt(marker.battery, suffix: '%')),
              if (!showMavlinkHud || !_mavlinkConnected) ...[
                _MetricChip(label: 'ROLL', value: _fmt(marker.roll, suffix: '°')),
                _MetricChip(label: 'PITCH', value: _fmt(marker.pitch, suffix: '°')),
                _MetricChip(label: 'YAW', value: _fmt(marker.yaw, suffix: '°')),
              ],
            ],
          ),
          if (onCenter != null) ...[
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerRight,
              child: FilledButton.icon(
                onPressed: onCenter,
                icon: const Icon(Icons.my_location, size: 18),
                label: const Text('Center on Device'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: TacticalColors.background,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: TacticalColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(label, style: const TextStyle(fontSize: 10, color: TacticalColors.textSecondary)),
          Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: TacticalColors.textPrimary,
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }
}

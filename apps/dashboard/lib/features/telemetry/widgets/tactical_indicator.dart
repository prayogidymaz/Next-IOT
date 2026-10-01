import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../dashboard/widgets/smart_home_bento_telemetry.dart';
import '../models/telemetry_models.dart';

class TacticalIndicator extends StatelessWidget {
  const TacticalIndicator({
    super.key,
    required this.latest,
    required this.deviceName,
    required this.deviceStatusLabel,
  });

  final TelemetryLatest? latest;
  final String deviceName;
  final String deviceStatusLabel;

  @override
  Widget build(BuildContext context) {
    final metrics = latest?.metrics ?? {};
    final lat = metrics['latitude'];
    final lon = metrics['longitude'];
    final alt = metrics['altitude_m'];
    final hasFix = lat != null && lon != null;
    final recordedAt = latest?.recordedAt;
    final indoor = metricsLookLikeSmartHome(metrics) ||
        (!hasFix && metrics.isNotEmpty);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: TacticalColors.surfaceElevated,
        borderRadius: BorderRadius.circular(BentoTokens.radius),
        border: Border.all(color: TacticalColors.border.withOpacity( 0.7)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.sensors, color: BentoTokens.accentLavender, size: 22),
              const SizedBox(width: 10),
              Text(
                'Live telemetry',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const Spacer(),
              _StatusPill(label: deviceStatusLabel),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            deviceName,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          if (indoor && !hasFix)
            _Row(label: 'Placement', value: 'Indoor / room anchor', highlight: true)
          else
            _Row(
              label: 'GPS fix',
              value: hasFix ? 'Locked' : 'No fix',
              highlight: hasFix,
            ),
          if (hasFix)
            _Row(
              label: 'Coordinates',
              value:
                  '${lat!.toStringAsFixed(6)}, ${lon!.toStringAsFixed(6)}',
            ),
          _Row(
            label: 'Altitude',
            value: alt != null ? '${alt.toStringAsFixed(1)} m' : '—',
          ),
          _Row(
            label: 'Last telemetry',
            value: recordedAt != null
                ? recordedAt.toLocal().toString().split('.').first
                : '—',
          ),
          _Row(label: 'Source', value: latest?.source ?? '—'),
        ],
      ),
    );
  }
}

class _StatusPill extends StatelessWidget {
  const _StatusPill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final normalized = label.toLowerCase();
    final isOnline = normalized.contains('online') || normalized.contains('active');
    final color = isOnline ? TacticalColors.success : TacticalColors.textSecondary;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity( 0.14),
        borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
        border: Border.all(color: color.withOpacity( 0.4)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({
    required this.label,
    required this.value,
    this.highlight = false,
  });

  final String label;
  final String value;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: Theme.of(context).textTheme.bodySmall),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: highlight
                        ? TacticalColors.textPrimary
                        : TacticalColors.textSecondary,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

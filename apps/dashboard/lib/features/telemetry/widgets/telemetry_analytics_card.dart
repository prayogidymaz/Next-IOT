import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/telemetry_analytics_models.dart';

class TelemetryAnalyticsCard extends StatelessWidget {
  const TelemetryAnalyticsCard({
    super.key,
    this.analytics,
    this.isLoading = false,
  });

  final TelemetryAnalytics? analytics;
  final bool isLoading;

  String _formatDistance(double meters) {
    if (meters >= 1000) return '${(meters / 1000).toStringAsFixed(2)} km';
    return '${meters.toStringAsFixed(0)} m';
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading && analytics == null) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }

    if (analytics == null) {
      return Text(
        'No analytics available for this window.',
        style: Theme.of(context).textTheme.bodySmall?.copyWith(color: TacticalColors.textSecondary),
      );
    }

    final data = analytics!;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: TacticalColors.surfaceElevated.withOpacity(0.6),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: TacticalColors.borderNeon.withOpacity(0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.analytics_outlined, size: 16, color: TacticalColors.cyan),
              const SizedBox(width: 6),
              Text(
                'FLIGHT ANALYTICS (${data.hours}h)',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: TacticalColors.cyan,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.6,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 16,
            runSpacing: 10,
            children: [
              _MetricTile(
                label: 'Jarak Tempuh',
                value: _formatDistance(data.totalDistanceM),
                icon: Icons.route,
              ),
              _MetricTile(
                label: 'Kecepatan Maks',
                value: data.maxSpeedMs != null ? '${data.maxSpeedMs!.toStringAsFixed(1)} m/s' : '—',
                icon: Icons.speed,
              ),
              _MetricTile(
                label: 'Baterai Terendah',
                value: data.minVoltageV != null ? '${data.minVoltageV!.toStringAsFixed(1)} V' : '—',
                icon: Icons.battery_alert,
                accent: data.minVoltageV != null && data.minVoltageV! < 11.5
                    ? TacticalColors.warning
                    : TacticalColors.success,
              ),
              _MetricTile(
                label: 'Anomali',
                value: '${data.anomalyCount}',
                icon: Icons.warning_amber,
                accent: data.anomalyCount > 0 ? TacticalColors.warning : TacticalColors.textSecondary,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({
    required this.label,
    required this.value,
    required this.icon,
    this.accent,
  });

  final String label;
  final String value;
  final IconData icon;
  final Color? accent;

  @override
  Widget build(BuildContext context) {
    final color = accent ?? TacticalColors.textPrimary;
    return SizedBox(
      width: 140,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 14, color: color),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  label,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: TacticalColors.textSecondary,
                        fontSize: 10,
                      ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: color,
                  fontWeight: FontWeight.w700,
                ),
          ),
        ],
      ),
    );
  }
}

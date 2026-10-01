import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/telemetry_analytics_models.dart';
import '../models/telemetry_models.dart';

class TelemetryMetricSummaryCards extends StatelessWidget {
  const TelemetryMetricSummaryCards({
    super.key,
    required this.series,
    required this.metricKey,
  });

  final MetricTimeSeries? series;
  final String metricKey;

  @override
  Widget build(BuildContext context) {
    final stats = series?.stats;
    final label = MetricDefinition.lookup(metricKey)?.label ?? metricKey;
    final unit = MetricDefinition.lookup(metricKey)?.unit ?? '';

    String fmt(double? v) =>
        v == null ? '—' : '${v.toStringAsFixed(2)}${unit.isNotEmpty ? ' $unit' : ''}';

    return Wrap(
      spacing: 12,
      runSpacing: 10,
      children: [
        _SummaryCard(title: 'Average', value: fmt(stats?.avg), icon: Icons.show_chart),
        _SummaryCard(title: 'Max', value: fmt(stats?.max), icon: Icons.north),
        _SummaryCard(title: 'Min', value: fmt(stats?.min), icon: Icons.south),
        _SummaryCard(title: 'Current', value: fmt(stats?.latest), icon: Icons.gps_fixed),
        _SummaryCard(title: 'Metric', value: label, icon: Icons.sensors),
      ],
    );
  }
}

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({
    required this.title,
    required this.value,
    required this.icon,
  });

  final String title;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 150,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: TacticalColors.surfaceElevated.withOpacity(0.55),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: TacticalColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 14, color: TacticalColors.cyan),
              const SizedBox(width: 6),
              Text(title, style: Theme.of(context).textTheme.labelSmall),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
        ],
      ),
    );
  }
}

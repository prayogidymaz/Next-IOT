import 'package:flutter/material.dart';

import '../models/telemetry_models.dart';

class MetricGaugeCard extends StatelessWidget {
  const MetricGaugeCard({
    super.key,
    required this.definition,
    required this.value,
  });

  final MetricDefinition definition;
  final double value;

  @override
  Widget build(BuildContext context) {
    final range = definition.max - definition.min;
    final normalized = range <= 0 ? 0.0 : ((value - definition.min) / range).clamp(0.0, 1.0);
    final color = _colorForKind(definition.kind, normalized);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(definition.label, style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 12),
            SizedBox(
              height: 72,
              width: 72,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(
                    value: normalized,
                    strokeWidth: 8,
                    backgroundColor: color.withOpacity(0.15),
                    color: color,
                  ),
                  Text(
                    value.toStringAsFixed(1),
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              definition.unit.isEmpty ? 'value' : definition.unit,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  Color _colorForKind(MetricKind kind, double normalized) {
    switch (kind) {
      case MetricKind.temperature:
        return Color.lerp(Colors.blue, Colors.red, normalized)!;
      case MetricKind.humidity:
        return Colors.cyan.shade700;
      case MetricKind.battery:
        return normalized < 0.2 ? Colors.red : Colors.green.shade600;
      case MetricKind.orientation:
        return Colors.deepPurple;
      case MetricKind.gps:
      case MetricKind.custom:
        return Colors.blueGrey;
    }
  }
}

import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../utils/signal_strength_utils.dart';

class SignalHeatmapLegend extends StatelessWidget {
  const SignalHeatmapLegend({super.key, this.pointCount = 0, this.hours = 24});

  final int pointCount;
  final int hours;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: TacticalColors.surface.withOpacity(0.92),
      elevation: 6,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: TacticalColors.borderNeon.withOpacity(0.35)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('RSSI / SNR LEGEND', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 6),
            _LegendRow(color: colorForRssi(-75), label: labelForBand(SignalStrengthBand.strong)),
            _LegendRow(color: colorForRssi(-95), label: labelForBand(SignalStrengthBand.marginal)),
            _LegendRow(color: colorForRssi(-115), label: labelForBand(SignalStrengthBand.weak)),
            const SizedBox(height: 6),
            Text(
              '$pointCount samples · ${hours}h window',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }
}

class _LegendRow extends StatelessWidget {
  const _LegendRow({required this.color, required this.label});

  final Color color;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color.withOpacity(0.7),
              borderRadius: BorderRadius.circular(3),
              border: Border.all(color: color),
            ),
          ),
          const SizedBox(width: 8),
          Text(label, style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 10)),
        ],
      ),
    );
  }
}

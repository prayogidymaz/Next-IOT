import 'package:flutter/material.dart';

import '../theme/tactical_theme.dart';

class GlowingLedBadge extends StatelessWidget {
  const GlowingLedBadge({
    super.key,
    required this.label,
    required this.color,
    this.pulse = false,
  });

  final String label;
  final Color color;
  final bool pulse;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity( 0.14),
        borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
        border: Border.all(color: color.withOpacity( 0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(shape: BoxShape.circle, color: color),
          ),
          const SizedBox(width: 8),
          Text(
            label.toUpperCase(),
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}

Color ledColorForStatus(String status) {
  final normalized = status.toLowerCase();
  if (normalized.contains('online') || normalized.contains('active')) {
    return TacticalColors.success;
  }
  if (normalized.contains('offline') || normalized.contains('critical')) {
    return TacticalColors.critical;
  }
  if (normalized.contains('pending') || normalized.contains('warning')) {
    return TacticalColors.warning;
  }
  return TacticalColors.cyan;
}

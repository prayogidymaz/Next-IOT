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
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.45)),
        boxShadow: [
          BoxShadow(color: color.withOpacity(pulse ? 0.35 : 0.2), blurRadius: pulse ? 10 : 6),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: color,
              boxShadow: [
                BoxShadow(color: color.withOpacity(0.8), blurRadius: 6, spreadRadius: 1),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Text(
            label.toUpperCase(),
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.6,
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
  return TacticalColors.info;
}

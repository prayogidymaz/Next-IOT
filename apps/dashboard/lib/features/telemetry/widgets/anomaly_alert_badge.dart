import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';

class AnomalyAlertBadge extends StatelessWidget {
  const AnomalyAlertBadge({
    super.key,
    required this.count,
    this.hasCritical = false,
    this.compact = false,
  });

  final int count;
  final bool hasCritical;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    if (count <= 0) return const SizedBox.shrink();

    final color = hasCritical ? TacticalColors.critical : TacticalColors.warning;

    if (compact) {
      return Container(
        width: 18,
        height: 18,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: color,
          shape: BoxShape.circle,
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: [
            BoxShadow(color: color.withOpacity(0.6), blurRadius: 6),
          ],
        ),
        child: Text(
          count > 9 ? '9+' : '$count',
          style: const TextStyle(
            color: Colors.white,
            fontSize: 9,
            fontWeight: FontWeight.w800,
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.warning_amber_rounded, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            '$count ANOMAL${count == 1 ? 'Y' : 'IES'}',
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

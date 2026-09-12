import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';

class GeofenceBreachWarning extends StatelessWidget {
  const GeofenceBreachWarning({super.key, this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: TacticalColors.critical.withOpacity(0.15),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: TacticalColors.critical, width: 1.5),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.warning_amber_rounded, color: TacticalColors.critical, size: 16),
            SizedBox(width: 6),
            Text(
              'GEOFENCE BREACH',
              style: TextStyle(
                color: TacticalColors.critical,
                fontSize: 11,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: TacticalColors.critical.withOpacity(0.18),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: TacticalColors.critical, width: 2),
        boxShadow: [
          BoxShadow(
            color: TacticalColors.critical.withOpacity(0.35),
            blurRadius: 12,
            spreadRadius: 1,
          ),
        ],
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.fence, color: TacticalColors.critical, size: 22),
          SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'GEOFENCE BREACH WARNING',
                style: TextStyle(
                  color: TacticalColors.critical,
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                ),
              ),
              SizedBox(height: 2),
              Text(
                'Drone entered forbidden zone',
                style: TextStyle(color: TacticalColors.textSecondary, fontSize: 10),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

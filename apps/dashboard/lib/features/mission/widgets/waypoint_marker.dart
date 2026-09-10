import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';

class WaypointMarker extends StatelessWidget {
  const WaypointMarker({super.key, required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 28,
          height: 28,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: TacticalColors.warning.withOpacity(0.25),
            border: Border.all(color: TacticalColors.warning, width: 2),
            boxShadow: [
              BoxShadow(color: TacticalColors.warning.withOpacity(0.4), blurRadius: 8),
            ],
          ),
          child: Center(
            child: Text(
              label.replaceAll('P', ''),
              style: const TextStyle(
                color: TacticalColors.warning,
                fontWeight: FontWeight.w800,
                fontSize: 11,
              ),
            ),
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            color: TacticalColors.warning,
            fontSize: 9,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}

import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../mission/models/sar_incident_models.dart';

class IncidentTargetMarker extends StatelessWidget {
  const IncidentTargetMarker({
    super.key,
    required this.incident,
    this.isSelected = false,
    this.onTap,
  });

  final SarIncident incident;
  final bool isSelected;
  final VoidCallback? onTap;

  Color get _accent {
    switch (incident.incidentType) {
      case SarIncidentType.personLost:
        return TacticalColors.warning;
      case SarIncidentType.vehicleCrash:
        return TacticalColors.critical;
      case SarIncidentType.droneDown:
        return TacticalColors.info;
    }
  }

  IconData get _icon {
    switch (incident.incidentType) {
      case SarIncidentType.personLost:
        return Icons.person_search;
      case SarIncidentType.vehicleCrash:
        return Icons.car_crash;
      case SarIncidentType.droneDown:
        return Icons.flight_land;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: isSelected ? 52 : 44,
            height: isSelected ? 52 : 44,
            decoration: BoxDecoration(
              color: _accent.withOpacity(0.2),
              shape: BoxShape.circle,
              border: Border.all(color: _accent, width: isSelected ? 3 : 2),
              boxShadow: isSelected
                  ? [BoxShadow(color: _accent.withOpacity(0.45), blurRadius: 10)]
                  : null,
            ),
            child: Icon(_icon, color: _accent, size: isSelected ? 24 : 20),
          ),
          const SizedBox(height: 2),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: TacticalColors.surface.withOpacity(0.92),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: _accent.withOpacity(0.7)),
            ),
            child: Text(
              incident.incidentType.label.toUpperCase(),
              style: TextStyle(
                color: _accent,
                fontSize: 8,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

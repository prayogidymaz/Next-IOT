import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/weather_vector_models.dart';

class FlightSafetyWeatherCard extends StatelessWidget {
  const FlightSafetyWeatherCard({
    super.key,
    required this.data,
    this.compact = false,
    this.isLoading = false,
  });

  final WeatherVectorData? data;
  final bool compact;
  final bool isLoading;

  Color _statusColor(FlightSafetyStatus status) {
    switch (status) {
      case FlightSafetyStatus.safe:
        return TacticalColors.success;
      case FlightSafetyStatus.caution:
        return TacticalColors.warning;
      case FlightSafetyStatus.noFly:
        return TacticalColors.critical;
    }
  }

  String _statusLabel(FlightSafetyStatus status) {
    switch (status) {
      case FlightSafetyStatus.safe:
        return 'SAFE';
      case FlightSafetyStatus.caution:
        return 'CAUTION';
      case FlightSafetyStatus.noFly:
        return 'NO-FLY HAZARD';
    }
  }

  IconData _statusIcon(FlightSafetyStatus status) {
    switch (status) {
      case FlightSafetyStatus.safe:
        return Icons.check_circle_outline;
      case FlightSafetyStatus.caution:
        return Icons.warning_amber_rounded;
      case FlightSafetyStatus.noFly:
        return Icons.block;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return _shell(
        child: const SizedBox(
          width: 14,
          height: 14,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }

    if (data == null) return const SizedBox.shrink();

    final color = _statusColor(data!.flightSafetyStatus);

    return _shell(
      color: color,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_statusIcon(data!.flightSafetyStatus), size: compact ? 14 : 16, color: color),
          const SizedBox(width: 6),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                compact ? _statusLabel(data!.flightSafetyStatus) : 'FLIGHT SAFETY & WEATHER',
                style: TextStyle(
                  color: color,
                  fontSize: compact ? 9 : 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.5,
                ),
              ),
              if (!compact) ...[
                Text(
                  _statusLabel(data!.flightSafetyStatus),
                  style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 2),
              ],
              Text(
                'Wind ${data!.windSpeedMs.toStringAsFixed(1)} m/s · Rain ${data!.rainRateMmH.toStringAsFixed(1)} mm/h',
                style: const TextStyle(fontSize: 9, color: TacticalColors.textSecondary),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _shell({required Widget child, Color? color}) {
    final borderColor = (color ?? TacticalColors.border).withOpacity(0.65);
    return Container(
      padding: EdgeInsets.symmetric(horizontal: compact ? 8 : 10, vertical: compact ? 6 : 8),
      decoration: BoxDecoration(
        color: TacticalColors.surface.withOpacity(0.95),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: borderColor, width: compact ? 1 : 1.5),
        boxShadow: color != null
            ? [BoxShadow(color: color.withOpacity(0.18), blurRadius: 10)]
            : null,
      ),
      child: child,
    );
  }
}

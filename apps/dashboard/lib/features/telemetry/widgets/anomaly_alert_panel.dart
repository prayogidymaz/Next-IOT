import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/telemetry_anomaly_models.dart';
import '../utils/anomaly_utils.dart';

class AnomalyAlertPanel extends StatelessWidget {
  const AnomalyAlertPanel({
    super.key,
    required this.anomalies,
    this.isLoading = false,
    this.onClose,
    this.onGenerateSarGrid,
  });

  final List<TelemetryAnomaly> anomalies;
  final bool isLoading;
  final VoidCallback? onClose;
  final void Function(double lat, double lon)? onGenerateSarGrid;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 320,
      constraints: const BoxConstraints(maxHeight: 320),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: TacticalColors.surface.withOpacity(0.95),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: TacticalColors.critical.withOpacity(0.5)),
        boxShadow: [
          BoxShadow(color: TacticalColors.critical.withOpacity(0.2), blurRadius: 12),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              const Icon(Icons.warning_amber_rounded, color: TacticalColors.warning, size: 18),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  'TELEMETRY ANOMALIES',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: TacticalColors.warning,
                        fontWeight: FontWeight.w800,
                      ),
                ),
              ),
              if (onClose != null)
                IconButton(
                  visualDensity: VisualDensity.compact,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
                  onPressed: onClose,
                  icon: const Icon(Icons.close, size: 18, color: TacticalColors.textSecondary),
                ),
            ],
          ),
          const SizedBox(height: 8),
          if (isLoading)
            const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
            )
          else if (anomalies.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Text(
                'No anomalies detected.',
                style: TextStyle(color: TacticalColors.textSecondary, fontSize: 12),
              ),
            )
          else
            Flexible(
              child: ListView.separated(
                shrinkWrap: true,
                itemCount: anomalies.length,
                separatorBuilder: (_, __) => const Divider(height: 12, color: TacticalColors.border),
                itemBuilder: (context, index) {
                  final anomaly = anomalies[index];
                  final color = anomalySeverityColor(anomaly.severity);
                  final lkp = anomalyLkp(anomaly.metadata);
                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(anomalyTypeIcon(anomaly.anomalyType), size: 16, color: color),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  anomalyTypeLabel(anomaly.anomalyType).toUpperCase(),
                                  style: TextStyle(
                                    color: color,
                                    fontSize: 10,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                  decoration: BoxDecoration(
                                    color: color.withOpacity(0.15),
                                    borderRadius: BorderRadius.circular(4),
                                    border: Border.all(color: color.withOpacity(0.5)),
                                  ),
                                  child: Text(
                                    anomaly.severity.toUpperCase(),
                                    style: TextStyle(color: color, fontSize: 8, fontWeight: FontWeight.w700),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 2),
                            Text(
                              anomaly.message,
                              style: const TextStyle(
                                color: TacticalColors.textPrimary,
                                fontSize: 11,
                              ),
                            ),
                            if (lkp != null && onGenerateSarGrid != null) ...[
                              const SizedBox(height: 6),
                              OutlinedButton.icon(
                                style: OutlinedButton.styleFrom(
                                  visualDensity: VisualDensity.compact,
                                  foregroundColor: TacticalColors.cyan,
                                  side: BorderSide(color: TacticalColors.cyan.withOpacity(0.6)),
                                ),
                                onPressed: () => onGenerateSarGrid!(lkp.$2, lkp.$3),
                                icon: const Icon(Icons.grid_on, size: 14),
                                label: const Text('Generate SAR Grid', style: TextStyle(fontSize: 10)),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
}

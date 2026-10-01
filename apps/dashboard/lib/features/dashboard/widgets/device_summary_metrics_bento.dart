import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../devices/models/device_models.dart';
import 'bento_compact_surface.dart';

class DeviceSummaryMetricsBento extends StatelessWidget {
  const DeviceSummaryMetricsBento({super.key, required this.devices});

  final List<Device> devices;

  @override
  Widget build(BuildContext context) {
    var online = 0, offline = 0, pending = 0;
    for (final d in devices) {
      switch (d.connectionStatus) {
        case DeviceConnectionStatus.online:
          online++;
        case DeviceConnectionStatus.offline:
          offline++;
        case DeviceConnectionStatus.pending:
          pending++;
      }
    }

    return BentoCompactSurface(
      height: 132,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Device summary', style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 10),
          Expanded(
            child: GridView.count(
              crossAxisCount: 2,
              mainAxisSpacing: 8,
              crossAxisSpacing: 8,
              childAspectRatio: 2.4,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _MiniMetric(
                  label: 'Online',
                  value: '$online',
                  color: TacticalColors.success,
                ),
                _MiniMetric(
                  label: 'Offline',
                  value: '$offline',
                  color: TacticalColors.critical,
                ),
                _MiniMetric(
                  label: 'Pending',
                  value: '$pending',
                  color: TacticalColors.warning,
                ),
                _MiniMetric(
                  label: 'Total',
                  value: '${devices.length}',
                  color: BentoTokens.accentLavender,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MiniMetric extends StatelessWidget {
  const _MiniMetric({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withOpacity(0.28)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            value,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                  color: color,
                  height: 1,
                ),
          ),
          Text(label, style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}

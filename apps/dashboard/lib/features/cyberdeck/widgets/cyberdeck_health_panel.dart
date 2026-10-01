import 'package:flutter/material.dart';

import '../models/cyberdeck_models.dart';
import '../theme/cyberdeck_theme.dart';

class CyberdeckHealthPanel extends StatelessWidget {
  const CyberdeckHealthPanel({super.key, this.health});

  final CyberdeckHealth? health;

  @override
  Widget build(BuildContext context) {
    final h = health;
    return Container(
      key: const Key('cyberdeck-health-panel'),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: CyberdeckColors.panel,
        border: Border.all(color: CyberdeckColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('HARDWARE HEALTH MONITOR', style: TextStyle(color: CyberdeckColors.amber, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          if (h == null)
            const Text('Loading SBC metrics…', style: TextStyle(color: CyberdeckColors.muted))
          else ...[
            _row('CPU TEMP', '${h.cpuTempC.toStringAsFixed(1)} °C'),
            _row('RAM USED', '${h.ramUsedPct.toStringAsFixed(0)} %'),
            _row('BATTERY', '${h.batteryPct.toStringAsFixed(0)} %'),
            _row('POWER', h.powerSource),
            _row('UPTIME', '${h.uptimeSec ~/ 3600}h ${(h.uptimeSec % 3600) ~/ 60}m'),
            _row('LoRa CH', '${h.loraChannel}'),
            _row('CRYPTO', h.encryption),
          ],
        ],
      ),
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          SizedBox(width: 110, child: Text(label, style: const TextStyle(color: CyberdeckColors.muted, fontSize: 11))),
          Expanded(child: Text(value, style: const TextStyle(color: CyberdeckColors.green, fontSize: 12))),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';

import '../theme/cyberdeck_theme.dart';

class CyberdeckPttPanel extends StatelessWidget {
  const CyberdeckPttPanel({
    super.key,
    required this.channel,
    required this.isTransmitting,
    required this.waveform,
    required this.onChannelChanged,
    required this.onTransmitStart,
    required this.onTransmitEnd,
    this.statusMessage,
  });

  final int channel;
  final bool isTransmitting;
  final List<double> waveform;
  final ValueChanged<int> onChannelChanged;
  final VoidCallback onTransmitStart;
  final VoidCallback onTransmitEnd;
  final String? statusMessage;

  @override
  Widget build(BuildContext context) {
    return Container(
      key: const Key('cyberdeck-ptt-panel'),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: CyberdeckColors.panel,
        border: Border.all(color: isTransmitting ? CyberdeckColors.amber : CyberdeckColors.border),
        boxShadow: isTransmitting
            ? [BoxShadow(color: CyberdeckColors.amber.withOpacity(0.35), blurRadius: 18)]
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              const Text('LoRa PTT VOICE', style: TextStyle(color: CyberdeckColors.green, fontWeight: FontWeight.bold)),
              const Spacer(),
              DropdownButton<int>(
                value: channel,
                dropdownColor: CyberdeckColors.panel,
                items: List.generate(8, (i) => DropdownMenuItem(value: i + 1, child: Text('CH ${i + 1}'))),
                onChanged: (v) {
                  if (v != null) onChannelChanged(v);
                },
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 64,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: List.generate(24, (index) {
                final level = index < waveform.length ? waveform[index] : 0.08;
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 1),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 80),
                      height: 8 + level * 52,
                      color: isTransmitting ? CyberdeckColors.amber : CyberdeckColors.green.withOpacity(0.35),
                    ),
                  ),
                );
              }),
            ),
          ),
          const SizedBox(height: 12),
          Listener(
            onPointerDown: (_) => onTransmitStart(),
            onPointerUp: (_) => onTransmitEnd(),
            onPointerCancel: (_) => onTransmitEnd(),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 120),
              height: 72,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: isTransmitting ? CyberdeckColors.amber.withOpacity(0.25) : CyberdeckColors.background,
                border: Border.all(color: CyberdeckColors.amber, width: isTransmitting ? 3 : 1),
              ),
              child: Text(
                isTransmitting ? 'TRANSMITTING…' : 'HOLD TO PTT',
                style: TextStyle(
                  color: isTransmitting ? CyberdeckColors.amber : CyberdeckColors.text,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.4,
                ),
              ),
            ),
          ),
          if (statusMessage != null) ...[
            const SizedBox(height: 8),
            Text(statusMessage!, style: const TextStyle(color: CyberdeckColors.muted, fontSize: 11)),
          ],
        ],
      ),
    );
  }
}

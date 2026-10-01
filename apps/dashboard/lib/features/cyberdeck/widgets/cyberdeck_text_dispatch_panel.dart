import 'package:flutter/material.dart';

import '../theme/cyberdeck_theme.dart';

class CyberdeckTextDispatchPanel extends StatelessWidget {
  const CyberdeckTextDispatchPanel({
    super.key,
    required this.controller,
    required this.onSend,
    required this.onBeacon,
    this.lastDispatch,
  });

  final TextEditingController controller;
  final VoidCallback onSend;
  final VoidCallback onBeacon;
  final String? lastDispatch;

  @override
  Widget build(BuildContext context) {
    return Container(
      key: const Key('cyberdeck-text-panel'),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: CyberdeckColors.panel,
        border: Border.all(color: CyberdeckColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('TEXT & COMMAND DISPATCHER', style: TextStyle(color: CyberdeckColors.green, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: controller,
            maxLength: 160,
            style: const TextStyle(color: CyberdeckColors.text),
            decoration: const InputDecoration(
              hintText: 'Short LoRa message (AES encrypted)',
              hintStyle: TextStyle(color: CyberdeckColors.muted),
              counterStyle: TextStyle(color: CyberdeckColors.muted),
              enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: CyberdeckColors.border)),
              focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: CyberdeckColors.amber)),
            ),
          ),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: onSend,
                  style: OutlinedButton.styleFrom(foregroundColor: CyberdeckColors.green),
                  child: const Text('SEND TEXT'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: FilledButton(
                  onPressed: onBeacon,
                  style: FilledButton.styleFrom(backgroundColor: CyberdeckColors.red),
                  child: const Text('EMERGENCY BEACON'),
                ),
              ),
            ],
          ),
          if (lastDispatch != null) ...[
            const SizedBox(height: 8),
            Text('LAST: $lastDispatch', style: const TextStyle(color: CyberdeckColors.muted, fontSize: 11)),
          ],
        ],
      ),
    );
  }
}

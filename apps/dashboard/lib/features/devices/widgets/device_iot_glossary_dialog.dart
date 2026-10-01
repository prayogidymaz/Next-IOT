import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../data/device_glossary.dart';

class DeviceIotGlossaryDialog extends StatelessWidget {
  const DeviceIotGlossaryDialog({super.key});

  static Future<void> show(BuildContext context) {
    return showDialog<void>(
      context: context,
      builder: (_) => const DeviceIotGlossaryDialog(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: TacticalColors.surface,
      title: const Text('Kamus Istilah IoT'),
      content: SizedBox(
        width: 520,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Guide for Beginners — penjelasan singkat istilah teknis yang '
                'sering muncul di Device Management & Automation Studio.',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: TacticalColors.textSecondary,
                    ),
              ),
              const SizedBox(height: 16),
              ...deviceIotGlossary.map(
                (entry) => Padding(
                  padding: const EdgeInsets.only(bottom: 14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        entry.term,
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              color: TacticalColors.cyan,
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        entry.plainExplanation,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Tutup'),
        ),
      ],
    );
  }
}

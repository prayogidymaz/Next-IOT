import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../providers/irrigation_provider.dart";
import "../theme/tactical_warm_cream.dart";

class IrrigationControlScreen extends ConsumerWidget {
  const IrrigationControlScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(irrigationProvider);
    final controller = ref.read(irrigationProvider.notifier);

    return Scaffold(
      backgroundColor: TacticalWarmCream.base,
      body: Center(
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  state.valveOpen ? "Valve OPEN" : "Valve CLOSED",
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                Text(
                  state.valveOpen ? "${state.countdownSeconds}s remaining" : "Tap to irrigate",
                  style: const TextStyle(fontFamily: "monospace"),
                ),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () => controller.toggleValve(),
                  style: FilledButton.styleFrom(
                    backgroundColor: TacticalWarmCream.olive,
                    minimumSize: const Size(120, 44),
                  ),
                  child: Text(state.valveOpen ? "Stop" : "Start"),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

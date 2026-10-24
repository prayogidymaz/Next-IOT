import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../providers/sensor_provider.dart";
import "../theme/tactical_warm_cream.dart";

class SensorMonitorScreen extends ConsumerStatefulWidget {
  const SensorMonitorScreen({super.key});

  @override
  ConsumerState<SensorMonitorScreen> createState() => _SensorMonitorScreenState();
}

class _SensorMonitorScreenState extends ConsumerState<SensorMonitorScreen> {
  int _page = 0;

  @override
  Widget build(BuildContext context) {
    final sensors = ref.watch(sensorReadingsProvider);
    return Scaffold(
      backgroundColor: TacticalWarmCream.base,
      body: sensors.when(
        data: (items) {
          if (items.isEmpty) {
            return const Center(child: Text("No sensors"));
          }
          final reading = items[_page % items.length];
          return GestureDetector(
            onHorizontalDragEnd: (details) {
              if (details.primaryVelocity == null) return;
              if (details.primaryVelocity! < 0) {
                setState(() => _page = (_page + 1) % items.length);
              } else if (details.primaryVelocity! > 0) {
                setState(() => _page = (_page - 1 + items.length) % items.length);
              }
            },
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(reading.label, style: Theme.of(context).textTheme.headlineSmall),
                  Text(
                    reading.value.toStringAsFixed(2),
                    style: const TextStyle(
                      fontFamily: "monospace",
                      fontSize: 36,
                      color: TacticalWarmCream.clay,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text("${_page + 1} / ${items.length} — swipe"),
                ],
              ),
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text("Failed to load sensors")),
      ),
    );
  }
}

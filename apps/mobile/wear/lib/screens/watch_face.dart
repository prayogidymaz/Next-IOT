import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../providers/mesh_connection.dart";
import "../providers/sensor_provider.dart";
import "../theme/tactical_warm_cream.dart";

class WatchFaceScreen extends ConsumerWidget {
  const WatchFaceScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connection = ref.watch(meshConnectionProvider);
    final sensors = ref.watch(sensorReadingsProvider);

    return Scaffold(
      backgroundColor: TacticalWarmCream.base,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                "Field mesh",
                style: Theme.of(context).textTheme.headlineSmall,
                textAlign: TextAlign.center,
              ),
              Text(
                connection.name,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: "monospace",
                  color: TacticalWarmCream.olive,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 12),
              sensors.when(
                data: (items) => Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: items.take(3).map(_kpiChip).toList(),
                ),
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (_, __) => const Text("Sensor KPI unavailable"),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _kpiChip(SensorReading reading) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
        child: Column(
          children: [
            Text(
              reading.value.toStringAsFixed(1),
              style: const TextStyle(
                fontFamily: "monospace",
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            Text(
              reading.label,
              style: const TextStyle(fontSize: 10),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

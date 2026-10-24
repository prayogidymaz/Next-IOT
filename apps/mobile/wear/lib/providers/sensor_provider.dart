import "package:flutter_riverpod/flutter_riverpod.dart";

import "../services/mesh_api.dart";

final meshApiProvider = Provider<MeshApi>((ref) => MeshApi());

final sensorReadingsProvider =
    FutureProvider<List<SensorReading>>((ref) async {
  final api = ref.watch(meshApiProvider);
  final farms = await api.getFarms();
  final farmId = farms.first["id"]?.toString() ?? "farm-1";
  final sensors = await api.getSensors(farmId);
  return sensors
      .map(
        (s) => SensorReading(
          label: s["name"]?.toString() ?? "Sensor",
          value: (s["last_moisture"] as num?)?.toDouble() ?? 0,
        ),
      )
      .toList();
});

class SensorReading {
  const SensorReading({required this.label, required this.value});

  final String label;
  final double value;
}

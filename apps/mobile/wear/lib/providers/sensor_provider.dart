import "package:flutter_riverpod/flutter_riverpod.dart";

import "../services/mesh_api.dart";

final meshApiProvider = Provider<MeshApi>((ref) => MeshApi());

final sensorReadingsProvider =
    FutureProvider<List<SensorReading>>((ref) async {
  final api = ref.watch(meshApiProvider);
  try {
    final farms = await api.getFarms();
    if (farms.isEmpty) {
      return _mockSensors();
    }
    final farmId = farms.first["id"]?.toString() ?? "farm-1";
    final sensors = await api.getSensors(farmId);
    if (sensors.isEmpty) {
      return _mockSensors();
    }
    return sensors
      .map(
        (s) => SensorReading(
          label: s["name"]?.toString() ?? "Sensor",
          value: (s["last_moisture"] as num?)?.toDouble() ?? 0,
        ),
      )
      .toList();
  } catch (_) {
    return _mockSensors();
  }
});

List<SensorReading> _mockSensors() => const [
      SensorReading(label: "Soil moisture", value: 42.5),
      SensorReading(label: "Air temp", value: 28.1),
      SensorReading(label: "Humidity", value: 76.0),
    ];

class SensorReading {
  const SensorReading({required this.label, required this.value});

  final String label;
  final double value;
}

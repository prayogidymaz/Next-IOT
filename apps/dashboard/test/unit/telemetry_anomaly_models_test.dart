import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_anomaly_models.dart';

void main() {
  test('TelemetryAnomaly.fromJson parses API payload', () {
    final anomaly = TelemetryAnomaly.fromJson({
      'id': 'a1',
      'device_id': 'd1',
      'severity': 'warning',
      'anomaly_type': 'signal_loss',
      'message': 'Sudden signal loss',
      'metadata': {'rssi_dbm': -110},
      'recorded_at': '2026-09-10T12:00:00Z',
      'detected_at': '2026-09-10T12:00:01Z',
    });

    expect(anomaly.id, 'a1');
    expect(anomaly.anomalyType, 'signal_loss');
    expect(anomaly.metadata['rssi_dbm'], -110);
  });

  test('TelemetryAnomalyList.hasCritical detects critical items', () {
    final list = TelemetryAnomalyList.fromJson({
      'device_id': 'd1',
      'hours': 24,
      'count': 2,
      'items': [
        {
          'id': 'a1',
          'device_id': 'd1',
          'severity': 'critical',
          'anomaly_type': 'voltage_drop',
          'message': 'drop',
          'metadata': {},
          'recorded_at': '2026-09-10T12:00:00Z',
          'detected_at': '2026-09-10T12:00:01Z',
        },
        {
          'id': 'a2',
          'device_id': 'd1',
          'severity': 'warning',
          'anomaly_type': 'battery_overheat',
          'message': 'hot',
          'metadata': {},
          'recorded_at': '2026-09-10T12:05:00Z',
          'detected_at': '2026-09-10T12:05:01Z',
        },
      ],
    });

    expect(list.hasCritical, isTrue);
    expect(list.hasWarning, isTrue);
    expect(list.count, 2);
  });
}

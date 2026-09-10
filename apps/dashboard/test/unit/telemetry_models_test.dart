import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_models.dart';

void main() {
  group('TelemetryLatest.fromJson', () {
    test('parses latest telemetry response', () {
      final latest = TelemetryLatest.fromJson({
        'device_id': 'd1',
        'reading_id': 'r1',
        'recorded_at': '2026-09-10T10:00:00Z',
        'metrics': {'temperature': 25.5, 'humidity': 60, 'battery': 88},
        'cached_at': '2026-09-10T10:00:05Z',
        'source': 'redis',
      });

      expect(latest.deviceId, 'd1');
      expect(latest.metrics['temperature'], 25.5);
      expect(latest.metrics['humidity'], 60.0);
    });
  });

  group('TelemetryHistory.fromJson', () {
    test('parses history items', () {
      final history = TelemetryHistory.fromJson({
        'device_id': 'd1',
        'count': 2,
        'items': [
          {
            'reading_id': 'r1',
            'recorded_at': '2026-09-10T09:00:00Z',
            'metrics': {'temperature': 20.0},
            'ingested_at': '2026-09-10T09:00:01Z',
          },
          {
            'reading_id': 'r2',
            'recorded_at': '2026-09-10T10:00:00Z',
            'metrics': {'temperature': 30.0},
            'ingested_at': '2026-09-10T10:00:01Z',
          },
        ],
      });

      expect(history.count, 2);
      expect(history.items.first.metrics['temperature'], 20.0);
    });
  });

  group('resolveGaugeMetrics', () {
    test('returns known metrics first and skips gps keys', () {
      final defs = resolveGaugeMetrics({
        'temperature': 22,
        'humidity': 55,
        'latitude': -6.2,
        'custom_metric': 42,
      });

      expect(defs.map((d) => d.key), ['temperature', 'humidity', 'custom_metric']);
    });
  });

  group('sortHistoryChronologically', () {
    test('orders items oldest to newest', () {
      final items = [
        TelemetryHistoryItem(
          readingId: '2',
          recordedAt: DateTime.parse('2026-09-10T11:00:00Z'),
          metrics: const {'temperature': 30},
          ingestedAt: DateTime.parse('2026-09-10T11:00:01Z'),
        ),
        TelemetryHistoryItem(
          readingId: '1',
          recordedAt: DateTime.parse('2026-09-10T10:00:00Z'),
          metrics: const {'temperature': 20},
          ingestedAt: DateTime.parse('2026-09-10T10:00:01Z'),
        ),
      ];

      final sorted = sortHistoryChronologically(items);
      expect(sorted.first.readingId, '1');
      expect(sorted.last.readingId, '2');
    });
  });
}

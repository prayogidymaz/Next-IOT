import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/telemetry/data/telemetry_stream_service.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_stream_event.dart';

void main() {
  test('TelemetryStreamEvent.fromJson parses metrics and status', () {
    final event = TelemetryStreamEvent.fromJson({
      'type': 'telemetry_update',
      'device_id': 'd1',
      'status': 'online',
      'metrics': {
        'latitude': -6.2,
        'longitude': 106.8,
        'battery': 77,
        'do_mg_l': 6.1,
        'ph': 7.4,
      },
      'recorded_at': '2026-09-16T05:00:00Z',
    });

    expect(event.deviceId, 'd1');
    expect(event.status, 'online');
    expect(event.metrics['latitude'], -6.2);
    expect(event.metrics['do_mg_l'], 6.1);
    expect(event.recordedAt?.toUtc().hour, 5);
  });

  test('MockTelemetryStreamConnection emits GPS drift events', () async {
    final device = Device(
      id: 'dev-1',
      tenantId: 't1',
      name: 'Stream Device',
      deviceType: 'sensor',
      status: 'online',
      createdAt: DateTime(2026, 9, 1),
    );
    final mock = MockTelemetryStreamConnection(
      interval: const Duration(milliseconds: 50),
      seedDevices: [device],
    );

    final events = <TelemetryStreamEvent>[];
    final done = Completer<void>();

    await mock.connect(
      onEvent: events.add,
      onError: (_) {},
      onDone: () {},
    );

    await Future<void>.delayed(const Duration(milliseconds: 180));
    await mock.disconnect();

    expect(events, isNotEmpty);
    expect(events.first.deviceId, 'dev-1');
    expect(events.first.metrics.containsKey('latitude'), isTrue);
    expect(events.last.metrics['latitude'], isNot(equals(events.first.metrics['latitude'])));
    done.complete();
    await done.future;
  });
}

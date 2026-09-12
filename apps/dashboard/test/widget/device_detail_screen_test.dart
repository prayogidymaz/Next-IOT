import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';
import 'package:next_iot_dashboard/features/devices/screens/device_detail_screen.dart';
import 'package:next_iot_dashboard/features/telemetry/data/telemetry_repository.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_models.dart';
import 'package:next_iot_dashboard/features/telemetry/providers/telemetry_analytics_provider.dart';
import 'package:next_iot_dashboard/features/telemetry/providers/telemetry_provider.dart';
import 'package:next_iot_dashboard/features/telemetry/widgets/metric_gauge_card.dart';
import 'package:next_iot_dashboard/features/telemetry/widgets/tactical_indicator.dart';

final _deviceDetailListScrollable = find.descendant(
  of: find.byType(ListView),
  matching: find.byType(Scrollable),
);

class _TestTelemetryNotifier extends TelemetryNotifier {
  _TestTelemetryNotifier(TelemetryState initial, String deviceId)
      : super(TelemetryRepository(), deviceId) {
    state = initial;
  }

  @override
  Future<void> load({TelemetryTimeRange? range}) async {}
}

class _TestTelemetryAnalyticsNotifier extends TelemetryAnalyticsNotifier {
  _TestTelemetryAnalyticsNotifier(String deviceId) : super(TelemetryRepository(), deviceId);

  @override
  Future<void> load({int? hours}) async {}
}

void main() {
  final device = Device(
    id: 'dev-1',
    tenantId: 't1',
    name: 'Demo Sensor Node',
    deviceType: 'sensor',
    status: 'online',
    lastSeenAt: DateTime(2026, 9, 10, 12, 0),
    createdAt: DateTime(2026, 9, 10, 8, 0),
  );

  final telemetryState = TelemetryState(
    latest: TelemetryLatest(
      deviceId: 'dev-1',
      recordedAt: DateTime(2026, 9, 10, 12, 0),
      metrics: {
        'temperature': 24.5,
        'humidity': 58.0,
        'battery': 91.0,
        'roll': 5.0,
        'pitch': -2.0,
        'yaw': 120.0,
        'latitude': -6.2088,
        'longitude': 106.8456,
        'altitude_m': 28.0,
      },
    ),
    history: [
      TelemetryHistoryItem(
        readingId: 'r1',
        recordedAt: DateTime(2026, 9, 10, 11, 0),
        metrics: const {'temperature': 22.0},
        ingestedAt: DateTime(2026, 9, 10, 11, 0, 1),
      ),
      TelemetryHistoryItem(
        readingId: 'r2',
        recordedAt: DateTime(2026, 9, 10, 12, 0),
        metrics: const {'temperature': 24.5},
        ingestedAt: DateTime(2026, 9, 10, 12, 0, 1),
      ),
    ],
  );

  Widget buildApp(TelemetryState state) {
    return ProviderScope(
      overrides: [
        telemetryProvider('dev-1').overrideWith(
          (ref) => _TestTelemetryNotifier(state, 'dev-1'),
        ),
        telemetryAnalyticsProvider('dev-1').overrideWith(
          (ref) => _TestTelemetryAnalyticsNotifier('dev-1'),
        ),
      ],
      child: MaterialApp(
        home: DeviceDetailScreen(deviceId: 'dev-1', device: device),
      ),
    );
  }

  testWidgets('DeviceDetailScreen renders tactical indicator, map and gauge cards', (tester) async {
    await tester.pumpWidget(buildApp(telemetryState));
    await tester.pump();

    expect(find.byType(TacticalIndicator), findsOneWidget);
    expect(find.text('TACTICAL TELEMETRY'), findsOneWidget);
    expect(find.textContaining('-6.208800'), findsOneWidget);
    expect(find.text('MAP TRACKING'), findsOneWidget);

    await tester.scrollUntilVisible(
      find.text('LIVE GAUGES'),
      500,
      scrollable: _deviceDetailListScrollable,
    );
    await tester.pump();

    expect(find.byType(MetricGaugeCard), findsWidgets);
    expect(find.text('Temperature'), findsWidgets);
    expect(find.text('LIVE GAUGES'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });

  testWidgets('DeviceDetailScreen renders time range filters and chart section', (tester) async {
    await tester.pumpWidget(buildApp(telemetryState));
    await tester.pump();

    await tester.scrollUntilVisible(
      find.text('TELEMETRY LOG PANEL'),
      500,
      scrollable: _deviceDetailListScrollable,
    );
    await tester.pump();

    expect(find.text('TELEMETRY LOG PANEL'), findsOneWidget);
    expect(find.text('1H'), findsOneWidget);
    expect(find.text('24H'), findsOneWidget);
    expect(find.text('7D'), findsOneWidget);
    expect(find.text('Chart metric'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  });
}

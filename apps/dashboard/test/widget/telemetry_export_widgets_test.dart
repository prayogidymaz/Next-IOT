import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_analytics_models.dart';
import 'package:next_iot_dashboard/features/telemetry/widgets/telemetry_analytics_card.dart';
import 'package:next_iot_dashboard/features/telemetry/widgets/telemetry_export_dialog.dart';

void main() {
  const sampleAnalytics = TelemetryAnalytics(
    deviceId: 'device-1',
    hours: 24,
    readingCount: 42,
    maxSpeedMs: 18.5,
    avgAltitudeM: 55.0,
    minVoltageV: 11.2,
    totalDistanceM: 1250.0,
    anomalyCount: 2,
  );

  testWidgets('TelemetryAnalyticsCard shows flight summary metrics', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: TelemetryAnalyticsCard(analytics: sampleAnalytics),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('FLIGHT ANALYTICS (24h)'), findsOneWidget);
    expect(find.text('Jarak Tempuh'), findsOneWidget);
    expect(find.text('1.25 km'), findsOneWidget);
    expect(find.text('18.5 m/s'), findsOneWidget);
    expect(find.text('11.2 V'), findsOneWidget);
  });

  testWidgets('TelemetryAnalyticsCard shows loading indicator', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: TelemetryAnalyticsCard(isLoading: true),
        ),
      ),
    );
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('TelemetryExportDialog renders format and time range controls', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () => TelemetryExportDialog.show(
                    context,
                    deviceId: 'device-abc-123',
                    deviceName: 'Alpha Drone',
                  ),
                  child: const Text('Open'),
                );
              },
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    expect(find.text('EXPORT TELEMETRY DATA'), findsOneWidget);
    expect(find.text('ALPHA DRONE'), findsOneWidget);
    expect(find.text('1 Hour'), findsOneWidget);
    expect(find.text('24 Hours'), findsOneWidget);
    expect(find.text('Download'), findsOneWidget);
    expect(find.text('CSV'), findsOneWidget);
  });
}

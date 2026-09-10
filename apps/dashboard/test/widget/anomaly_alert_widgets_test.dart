import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_anomaly_models.dart';
import 'package:next_iot_dashboard/features/telemetry/widgets/anomaly_alert_badge.dart';
import 'package:next_iot_dashboard/features/telemetry/widgets/anomaly_alert_panel.dart';

void main() {
  final sampleAnomalies = [
    TelemetryAnomaly(
      id: 'a1',
      deviceId: 'd1',
      severity: 'critical',
      anomalyType: 'voltage_drop',
      message: 'Voltage dropped 20%',
      metadata: const {},
      recordedAt: DateTime(2026, 9, 10, 12),
      detectedAt: DateTime(2026, 9, 10, 12),
    ),
    TelemetryAnomaly(
      id: 'a2',
      deviceId: 'd1',
      severity: 'warning',
      anomalyType: 'battery_overheat',
      message: 'Battery temperature 58°C exceeds threshold',
      metadata: const {},
      recordedAt: DateTime(2026, 9, 10, 12, 5),
      detectedAt: DateTime(2026, 9, 10, 12, 5),
    ),
  ];

  testWidgets('AnomalyAlertBadge shows count for non-zero anomalies', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AnomalyAlertBadge(count: 3, hasCritical: true),
        ),
      ),
    );

    expect(find.text('3 ANOMALIES'), findsOneWidget);
    expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
  });

  testWidgets('AnomalyAlertBadge hidden when count is zero', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AnomalyAlertBadge(count: 0),
        ),
      ),
    );

    expect(find.byType(AnomalyAlertBadge), findsOneWidget);
    expect(find.textContaining('ANOMAL'), findsNothing);
  });

  testWidgets('AnomalyAlertPanel renders anomaly list', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AnomalyAlertPanel(anomalies: sampleAnomalies),
        ),
      ),
    );

    expect(find.text('TELEMETRY ANOMALIES'), findsOneWidget);
    expect(find.text('Voltage dropped 20%'), findsOneWidget);
    expect(find.text('Battery temperature 58°C exceeds threshold'), findsOneWidget);
    expect(find.text('VOLTAGE DROP'), findsOneWidget);
    expect(find.text('OVERHEAT'), findsOneWidget);
  });

  testWidgets('AnomalyAlertPanel shows empty state', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AnomalyAlertPanel(anomalies: []),
        ),
      ),
    );

    expect(find.text('No anomalies detected.'), findsOneWidget);
  });
}

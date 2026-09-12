import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/map/widgets/sar_grid_overlay.dart';
import 'package:next_iot_dashboard/features/mission/models/mission_models.dart';
import 'package:next_iot_dashboard/features/mission/models/sar_grid_models.dart';
import 'package:next_iot_dashboard/features/mission/providers/mission_provider.dart';
import 'package:next_iot_dashboard/features/mission/widgets/emergency_fail_safe_dialog.dart';
import 'package:next_iot_dashboard/features/telemetry/models/telemetry_anomaly_models.dart';
import 'package:next_iot_dashboard/features/telemetry/widgets/anomaly_alert_panel.dart';

void main() {
  final sarGridResult = SarGridResult(
    pattern: 'expanding_square',
    lkp: const SarGridPoint(lat: -6.2088, lon: 106.8456),
    radiusM: 500,
    waypoints: [
      const SarGridWaypoint(sequence: 1, lat: -6.2088, lon: 106.8456, label: 'LKP'),
      const SarGridWaypoint(sequence: 2, lat: -6.2079, lon: 106.8456),
    ],
    tracks: [
      SarGridTrack(
        trackIndex: 1,
        points: const [
          SarGridPoint(lat: -6.2088, lon: 106.8456),
          SarGridPoint(lat: -6.2079, lon: 106.8456),
        ],
      ),
    ],
    searchAreas: [
      SarGridSearchArea(
        label: 'search_boundary',
        points: const [
          SarGridPoint(lat: -6.2133, lon: 106.8411),
          SarGridPoint(lat: -6.2133, lon: 106.8501),
          SarGridPoint(lat: -6.2043, lon: 106.8501),
          SarGridPoint(lat: -6.2043, lon: 106.8411),
        ],
      ),
    ],
  );

  test('SarGridOverlay.buildMapLayers returns polygon, polyline, and marker layers', () {
    final layers = SarGridOverlay.buildMapLayers(sarGridResult);
    expect(layers.length, greaterThanOrEqualTo(3));
  });

  test('SarGridOverlay.buildMapLayers returns empty for no tracks and areas', () {
    final empty = SarGridResult(
      pattern: 'expanding_square',
      lkp: const SarGridPoint(lat: 0, lon: 0),
      radiusM: 100,
      waypoints: const [],
      tracks: const [],
      searchAreas: const [],
    );
    final layers = SarGridOverlay.buildMapLayers(empty);
    expect(layers, hasLength(1));
  });

  testWidgets('EmergencyFailSafeDialog renders tactical confirmation UI', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          missionPlannerProvider.overrideWith(
            (ref) => MissionPlannerNotifier(ref.watch(commandRepositoryProvider))
              ..setTargetDevice('device-1'),
          ),
        ],
        child: const MaterialApp(home: Scaffold(body: EmergencyFailSafeDialog())),
      ),
    );
    await tester.pump();

    expect(find.text('EMERGENCY FAIL-SAFE'), findsOneWidget);
    expect(find.text('Return to Home (RTH)'), findsOneWidget);
    expect(find.text('Emergency Land'), findsOneWidget);
    expect(find.text('CONFIRM FAIL-SAFE'), findsOneWidget);
  });

  testWidgets('AnomalyAlertPanel shows Generate SAR Grid for location anomalies', (tester) async {
    var tapped = false;
    final anomalies = [
      TelemetryAnomaly(
        id: 'a1',
        deviceId: 'd1',
        severity: 'critical',
        anomalyType: 'signal_loss',
        message: 'Signal critically weak',
        metadata: const {'lat': -6.2088, 'lon': 106.8456},
        recordedAt: DateTime(2026, 9, 10),
        detectedAt: DateTime(2026, 9, 10),
      ),
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AnomalyAlertPanel(
            anomalies: anomalies,
            onGenerateSarGrid: (_, __) => tapped = true,
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('Generate SAR Grid'), findsOneWidget);
    await tester.tap(find.text('Generate SAR Grid'));
    expect(tapped, isTrue);
  });
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/map/utils/swarm_distance_utils.dart';
import 'package:next_iot_dashboard/features/telemetry/data/flight_replay_repository.dart';
import 'package:next_iot_dashboard/features/map/widgets/flight_replay_control_bar.dart';
import 'package:next_iot_dashboard/features/map/widgets/swarm_distance_overlay.dart';
import 'package:next_iot_dashboard/features/telemetry/models/flight_replay_models.dart';
import 'package:next_iot_dashboard/features/telemetry/providers/flight_replay_provider.dart';

class _TestReplayNotifier extends FlightReplayNotifier {
  _TestReplayNotifier(FlightReplayRepository repo, FlightReplayState initial) : super(repo) {
    state = initial;
  }

  @override
  Future<void> toggleForDevice(String? deviceId) async {}
}

void main() {
  final replayData = FlightReplayData(
    deviceId: 'd1',
    sessionStart: DateTime(2026, 9, 10, 10),
    sessionEnd: DateTime(2026, 9, 10, 10, 30),
    hours: 24,
    samples: [
      FlightReplaySample(
        timestamp: DateTime(2026, 9, 10, 10),
        lat: -6.2088,
        lon: 106.8456,
        speed: 10,
      ),
      FlightReplaySample(
        timestamp: DateTime(2026, 9, 10, 10, 15),
        lat: -6.2095,
        lon: 106.8465,
        speed: 12,
      ),
      FlightReplaySample(
        timestamp: DateTime(2026, 9, 10, 10, 30),
        lat: -6.2102,
        lon: 106.8472,
        speed: 8,
      ),
    ],
  );

  testWidgets('FlightReplayControlBar renders play controls when enabled', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          flightReplayProvider.overrideWith(
            (ref) => _TestReplayNotifier(
              FlightReplayRepository(),
              FlightReplayState(enabled: true, data: replayData, progress: 0.5),
            ),
          ),
        ],
        child: const MaterialApp(home: Scaffold(body: FlightReplayControlBar())),
      ),
    );
    await tester.pump();

    expect(find.text('FLIGHT REPLAY'), findsOneWidget);
    expect(find.byIcon(Icons.play_circle_filled), findsOneWidget);
    expect(find.text('1x'), findsOneWidget);
    expect(find.byType(Slider), findsOneWidget);
  });

  testWidgets('FlightReplayControlBar hidden when disabled', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          flightReplayProvider.overrideWith(
            (ref) => _TestReplayNotifier(
              FlightReplayRepository(),
              const FlightReplayState(),
            ),
          ),
        ],
        child: const MaterialApp(home: Scaffold(body: FlightReplayControlBar())),
      ),
    );
    await tester.pump();

    expect(find.text('FLIGHT REPLAY'), findsNothing);
  });

  test('SwarmDistanceOverlay.buildMapLayers returns layers for linked nodes', () {
    final nodes = [
      const SwarmNodePosition(deviceId: 'a', deviceName: 'Alpha', lat: -6.2088, lon: 106.8456),
      const SwarmNodePosition(deviceId: 'b', deviceName: 'Bravo', lat: -6.20881, lon: 106.84561),
    ];
    final links = computeSwarmLinks(nodes);
    final layers = SwarmDistanceOverlay.buildMapLayers(nodes: nodes, links: links);
    expect(layers.length, greaterThanOrEqualTo(2));
    expect(links.first.collisionRisk, isTrue);
    expect(links.first.warning, collisionRiskWarning);
  });

  test('computeSwarmLinks safe distance has no warning', () {
    final nodes = [
      const SwarmNodePosition(deviceId: 'a', deviceName: 'Alpha', lat: -6.2088, lon: 106.8456),
      const SwarmNodePosition(deviceId: 'b', deviceName: 'Bravo', lat: -6.2188, lon: 106.8556),
    ];
    final links = computeSwarmLinks(nodes);
    expect(links.single.collisionRisk, isFalse);
    expect(links.single.warning, isNull);
  });
}

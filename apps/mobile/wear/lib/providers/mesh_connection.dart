import "dart:async";

import "package:flutter_riverpod/flutter_riverpod.dart";

import "../services/sse_connection.dart";
import "alert_provider.dart";
import "sensor_provider.dart";

enum MeshConnectionState { disconnected, connecting, live }

final meshConnectionProvider =
    StateNotifierProvider<MeshConnectionNotifier, MeshConnectionState>(
  (ref) => MeshConnectionNotifier(ref),
);

class MeshConnectionNotifier extends StateNotifier<MeshConnectionState> {
  MeshConnectionNotifier(this._ref) : super(MeshConnectionState.disconnected);

  final Ref _ref;
  MeshSseConnection? _sse;
  void connectLive(String jwt) {
    state = MeshConnectionState.connecting;
    _sse?.stop();
    _sse = MeshSseConnection(
      baseUrl: const String.fromEnvironment("WEAR_API_BASE", defaultValue: "http://10.0.2.2:8000"),
      jwt: jwt,
      onEvent: (event) {
        state = MeshConnectionState.live;
        _ref.read(liveMeshEventsProvider.notifier).push(event);
        final domain = event["domain"]?.toString() ?? "";
        final eventType = event["event_type"]?.toString() ?? "";
        if (domain == "sensor" && eventType == "reading_update") {
          _ref.invalidate(sensorReadingsProvider);
        }
        if (domain == "ui" || domain == "security") {
          _ref.invalidate(alertProvider);
        }
      },
    );
    unawaited(_sse!.connect());
  }

  void connectSkeleton() {
    state = MeshConnectionState.connecting;
    Future<void>.delayed(const Duration(milliseconds: 300), () {
      state = MeshConnectionState.live;
    });
  }

  @override
  void dispose() {
    _sse?.stop();
    super.dispose();
  }
}

final liveMeshEventsProvider =
    StateNotifierProvider<LiveMeshEvents, List<Map<String, dynamic>>>(
  (ref) => LiveMeshEvents(),
);

class LiveMeshEvents extends StateNotifier<List<Map<String, dynamic>>> {
  LiveMeshEvents() : super(const []);

  void push(Map<String, dynamic> event) {
    state = [event, ...state].take(50).toList();
  }
}

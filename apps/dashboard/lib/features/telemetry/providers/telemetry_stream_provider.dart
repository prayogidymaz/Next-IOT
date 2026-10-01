import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../devices/providers/device_provider.dart';
import '../../map/providers/map_provider.dart';
import '../../map/widgets/tactical_tile_layer.dart'
    show isFlutterTestEnvironment;
import '../data/telemetry_stream_service.dart';
import '../models/telemetry_stream_event.dart';

final telemetryStreamConnectionProvider =
    Provider<TelemetryStreamConnection>((ref) {
  if (isFlutterTestEnvironment) {
    final devices = ref.watch(deviceProvider).devices;
    return MockTelemetryStreamConnection(seedDevices: devices);
  }
  return WebSocketTelemetryStreamConnection();
});

class TelemetryStreamState {
  const TelemetryStreamState({
    this.isActive = false,
    this.isConnected = false,
    this.useMockFallback = false,
    this.eventsReceived = 0,
    this.error,
  });

  final bool isActive;
  final bool isConnected;
  final bool useMockFallback;
  final int eventsReceived;
  final String? error;

  TelemetryStreamState copyWith({
    bool? isActive,
    bool? isConnected,
    bool? useMockFallback,
    int? eventsReceived,
    String? error,
    bool clearError = false,
  }) {
    return TelemetryStreamState(
      isActive: isActive ?? this.isActive,
      isConnected: isConnected ?? this.isConnected,
      useMockFallback: useMockFallback ?? this.useMockFallback,
      eventsReceived: eventsReceived ?? this.eventsReceived,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class TelemetryStreamNotifier extends StateNotifier<TelemetryStreamState> {
  TelemetryStreamNotifier(this._ref, this._connection)
      : super(const TelemetryStreamState());

  final Ref _ref;
  TelemetryStreamConnection _connection;
  MockTelemetryStreamConnection? _mockFallback;

  Future<void> start() async {
    if (state.isActive) return;
    state = state.copyWith(isActive: true, clearError: true);
    await _connect(_connection);
  }

  Future<void> _connect(TelemetryStreamConnection connection) async {
    await connection.connect(
      onEvent: (event) {
        if (!state.isConnected) {
          state = state.copyWith(isConnected: true);
        }
        _handleEvent(event);
      },
      onError: (_) async {
        if (!state.useMockFallback && !isFlutterTestEnvironment) {
          await connection.disconnect();
          _mockFallback ??= MockTelemetryStreamConnection(
            seedDevices: _ref.read(deviceProvider).devices,
          );
          _connection = _mockFallback!;
          state = state.copyWith(useMockFallback: true, clearError: true);
          await _connect(_mockFallback!);
          return;
        }
        state = state.copyWith(
          isConnected: false,
          error: 'Telemetry stream disconnected.',
        );
      },
      onDone: () {
        state = state.copyWith(isConnected: false);
      },
    );
  }

  void _handleEvent(TelemetryStreamEvent event) {
    state = state.copyWith(eventsReceived: state.eventsReceived + 1);
    _ref.read(tacticalMapProvider.notifier).applyStreamEvent(event);
    if (event.status != null) {
      _ref
          .read(deviceProvider.notifier)
          .applyStreamStatus(event.deviceId, event.status!);
    }
  }

  Future<void> stop() async {
    await _connection.disconnect();
    await _mockFallback?.disconnect();
    _mockFallback = null;
    state = const TelemetryStreamState();
  }
}

final telemetryStreamProvider =
    StateNotifierProvider<TelemetryStreamNotifier, TelemetryStreamState>((ref) {
  return TelemetryStreamNotifier(
    ref,
    ref.watch(telemetryStreamConnectionProvider),
  );
});

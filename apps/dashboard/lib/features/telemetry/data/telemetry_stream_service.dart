import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../core/auth/token_storage.dart';
import '../../../core/config/api_config.dart';
import '../../devices/models/device_models.dart';
import '../models/telemetry_stream_event.dart';

typedef TelemetryStreamHandler = void Function(TelemetryStreamEvent event);

abstract class TelemetryStreamConnection {
  Future<void> connect({
    required TelemetryStreamHandler onEvent,
    required void Function(Object error) onError,
    required void Function() onDone,
  });

  Future<void> disconnect();
}

class WebSocketTelemetryStreamConnection implements TelemetryStreamConnection {
  WebSocketTelemetryStreamConnection({TokenStorage? tokenStorage})
      : _tokenStorage = tokenStorage ?? TokenStorage();

  final TokenStorage _tokenStorage;
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;

  @override
  Future<void> connect({
    required TelemetryStreamHandler onEvent,
    required void Function(Object error) onError,
    required void Function() onDone,
  }) async {
    final token = await _tokenStorage.getAccessToken();
    if (token == null || token.isEmpty) {
      onError(StateError('Missing access token'));
      return;
    }

    final uri = Uri.parse(
      '${ApiConfig.wsBaseUrl}/api/v1/telemetry/stream?token=$token',
    );
    _channel = WebSocketChannel.connect(uri);
    _subscription = _channel!.stream.listen(
      (event) {
        try {
          final decoded = jsonDecode(event as String) as Map<String, dynamic>;
          final type = decoded['type'] as String?;
          if (type != null &&
              type != 'telemetry_update' &&
              type != 'telemetry') {
            return;
          }
          onEvent(TelemetryStreamEvent.fromJson(decoded));
        } catch (e) {
          onError(e);
        }
      },
      onError: onError,
      onDone: onDone,
      cancelOnError: true,
    );
  }

  @override
  Future<void> disconnect() async {
    await _subscription?.cancel();
    await _channel?.sink.close();
    _subscription = null;
    _channel = null;
  }
}

/// Local mock stream for dev/test when backend WebSocket/MQTT is unavailable.
class MockTelemetryStreamConnection implements TelemetryStreamConnection {
  MockTelemetryStreamConnection({
    this.interval = const Duration(seconds: 2),
    List<Device>? seedDevices,
  }) : _seedDevices = seedDevices ?? const [];

  final Duration interval;
  final List<Device> _seedDevices;
  StreamSubscription<int>? _subscription;
  final _rng = math.Random(42);
  final Map<String, _MockDeviceState> _states = {};

  @override
  Future<void> connect({
    required TelemetryStreamHandler onEvent,
    required void Function(Object error) onError,
    required void Function() onDone,
  }) async {
    _initStates();
    _subscription = Stream.periodic(interval, (tick) => tick).listen(
      (_) => _emit(onEvent),
      onError: onError,
      onDone: onDone,
    );
  }

  void _initStates() {
    if (_states.isNotEmpty) return;
    final devices = _seedDevices.isNotEmpty
        ? _seedDevices
        : [
            Device(
              id: 'mock-drone-1',
              tenantId: 't1',
              name: 'Mock Drone Alpha',
              deviceType: 'drone',
              status: 'online',
              createdAt: DateTime(2026, 9, 1),
            ),
            Device(
              id: 'mock-sensor-1',
              tenantId: 't1',
              name: 'Mock Pond Sensor',
              deviceType: 'sensor',
              status: 'online',
              createdAt: DateTime(2026, 9, 1),
            ),
          ];

    var i = 0;
    for (final device in devices) {
      final baseLat = -6.2088 + (i * 0.008);
      final baseLon = 106.8456 + (i * 0.006);
      _states[device.id] = _MockDeviceState(
        deviceId: device.id,
        lat: baseLat,
        lon: baseLon,
        battery: 88 - (i * 4),
        isDrone: device.deviceType == 'drone',
      );
      i += 1;
    }
  }

  void _emit(TelemetryStreamHandler onEvent) {
    for (final state in _states.values) {
      state.lat += (_rng.nextDouble() - 0.5) * 0.00015;
      state.lon += (_rng.nextDouble() - 0.5) * 0.00015;
      state.battery = math.max(10, state.battery - _rng.nextDouble() * 0.2);
      state.yaw = (state.yaw + _rng.nextDouble() * 8 - 4) % 360;
      state.roll = math.sin(_rng.nextDouble() * math.pi) * 12;
      state.pitch = math.cos(_rng.nextDouble() * math.pi) * 8;

      final metrics = <String, double>{
        'latitude': state.lat,
        'longitude': state.lon,
        'altitude_m': 28 + _rng.nextDouble() * 6,
        'battery': state.battery,
        'speed': 2 + _rng.nextDouble() * 4,
        'yaw': state.yaw,
        'roll': state.roll,
        'pitch': state.pitch,
      };

      if (state.isDrone) {
        metrics['mavlink_connected'] = 1;
      } else {
        metrics['do_mg_l'] = 5.5 + _rng.nextDouble() * 2;
        metrics['ph'] = 6.8 + _rng.nextDouble() * 0.8;
        metrics['rssi'] = -70 - _rng.nextDouble() * 15;
      }

      onEvent(
        TelemetryStreamEvent(
          deviceId: state.deviceId,
          metrics: metrics,
          status: 'online',
          recordedAt: DateTime.now().toUtc(),
          source: 'mock',
        ),
      );
    }
  }

  @override
  Future<void> disconnect() async {
    await _subscription?.cancel();
    _subscription = null;
  }
}

class _MockDeviceState {
  _MockDeviceState({
    required this.deviceId,
    required this.lat,
    required this.lon,
    required this.battery,
    required this.isDrone,
  });

  final String deviceId;
  double lat;
  double lon;
  double battery;
  final bool isDrone;
  double yaw = 90;
  double roll = 0;
  double pitch = 0;
}

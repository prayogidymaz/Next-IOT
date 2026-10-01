import 'dart:async';
import 'dart:math';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api/field_api_client.dart';
import '../../core/ble/ble_relay_service.dart';
import '../../core/storage/offline_telemetry_store.dart';
import '../../core/sync/telemetry_sync_service.dart';
import '../../core/theme/field_theme.dart';
import '../auth/auth_controller.dart';
import '../scanner/scanner_service.dart';

class TacticalHudScreen extends ConsumerStatefulWidget {
  const TacticalHudScreen({super.key, this.device});

  final DiscoveredDevice? device;

  @override
  ConsumerState<TacticalHudScreen> createState() => _TacticalHudScreenState();
}

class _TacticalHudScreenState extends ConsumerState<TacticalHudScreen> {
  bool relayOn = false;
  double temp = 29.2;
  double ph = 7.1;
  double humidity = 62;
  double battery = 78;
  int rssi = -61;
  int _pendingQueue = 0;
  bool _syncing = false;
  Timer? _telemetryTimer;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySub;

  final _offline = OfflineTelemetryStore();
  final _sync = TelemetrySyncService();
  final _bleRelay = BleRelayService();

  @override
  void initState() {
    super.initState();
    _telemetryTimer = Timer.periodic(const Duration(seconds: 3), (_) => _tickTelemetry());
    _refreshPendingCount();
    _connectivitySub = Connectivity().onConnectivityChanged.listen((_) => _autoFlush());
  }

  @override
  void dispose() {
    _telemetryTimer?.cancel();
    _connectivitySub?.cancel();
    super.dispose();
  }

  Future<void> _refreshPendingCount() async {
    final count = await _sync.pendingCount();
    if (mounted) setState(() => _pendingQueue = count);
  }

  Future<void> _autoFlush() async {
    if (_syncing) return;
    if (!await _sync.hasNetwork) return;
    final pending = await _sync.pendingCount();
    if (pending == 0) return;
    await _flushQueue(silent: true);
  }

  void _tickTelemetry() {
    final rnd = Random();
    setState(() {
      temp += (rnd.nextDouble() - 0.5) * 0.4;
      ph += (rnd.nextDouble() - 0.5) * 0.05;
      humidity += (rnd.nextDouble() - 0.5);
      battery = (battery - 0.05).clamp(10, 100);
      rssi = -55 - rnd.nextInt(12);
    });
    _offline.enqueue(
      widget.device?.apiDeviceId ?? widget.device?.id ?? 'field-device',
      {
        'temperature': temp,
        'ph': ph,
        'humidity': humidity,
        'battery': battery,
        'rssi': rssi,
      },
    );
    _refreshPendingCount();
  }

  Future<void> _toggleRelay(FieldApiClient api) async {
    final next = !relayOn;
    setState(() => relayOn = next);
    final channel = 'ch1';
    final deviceUuid = widget.device?.apiDeviceId;
    final bleRemoteId = widget.device?.bleRemoteId;

    try {
      if (await _sync.hasNetwork && deviceUuid != null && _isUuid(deviceUuid)) {
        await api.dispatchRelayCommand(deviceId: deviceUuid, on: next, channel: channel);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Relay ${next ? 'ON' : 'OFF'} via cloud')),
          );
        }
        return;
      }
      if (bleRemoteId != null) {
        await _bleRelay.writeRelayCommand(remoteId: bleRemoteId, on: next, channel: channel);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Relay ${next ? 'ON' : 'OFF'} via BLE GATT')),
          );
        }
        return;
      }
      throw StateError('No cloud UUID or BLE peripheral for relay command');
    } on DioException catch (e) {
      if (bleRemoteId != null) {
        try {
          await _bleRelay.writeRelayCommand(remoteId: bleRemoteId, on: next, channel: channel);
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Cloud failed — relay ${next ? 'ON' : 'OFF'} via BLE')),
            );
          }
          return;
        } catch (bleErr) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Relay failed: $bleErr')),
            );
          }
          setState(() => relayOn = !next);
          return;
        }
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Relay failed: ${e.message}')),
        );
      }
      setState(() => relayOn = !next);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Relay failed: $e')),
        );
      }
      setState(() => relayOn = !next);
    }
  }

  Future<void> _flushQueue({bool silent = false}) async {
    if (_syncing) return;
    setState(() => _syncing = true);
    final api = ref.read(fieldApiProvider);
    final result = await _sync.flush(api: api);
    await _refreshPendingCount();
    if (mounted) {
      setState(() => _syncing = false);
      if (!silent) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Sync: ${result.synced} uploaded, ${result.failed} failed, ${result.skipped} skipped (non-UUID device id)',
            ),
          ),
        );
      }
    }
  }

  bool _isUuid(String value) {
    final re = RegExp(
      r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
    );
    return re.hasMatch(value);
  }

  @override
  Widget build(BuildContext context) {
    final api = ref.watch(fieldApiProvider);
    final title = widget.device?.name ?? 'Tactical HUD';

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        actions: [
          if (_pendingQueue > 0)
            Center(
              child: Padding(
                padding: const EdgeInsets.only(right: 8),
                child: Text('Queue $_pendingQueue', style: const TextStyle(fontSize: 12)),
              ),
            ),
          IconButton(
            tooltip: 'Sync offline queue to /telemetry/bulk',
            onPressed: _syncing ? null : () => _flushQueue(),
            icon: _syncing
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.cloud_upload_outlined),
          ),
          IconButton(
            onPressed: () => ref.read(authControllerProvider.notifier).logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: SwitchListTile(
              title: const Text('Direct relay switch'),
              subtitle: const Text('REST when online · BLE GATT write when field link is down'),
              value: relayOn,
              onChanged: (_) => _toggleRelay(api),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _MetricTile(label: 'Temp °C', value: temp.toStringAsFixed(1), color: FieldColors.emerald),
              _MetricTile(label: 'pH', value: ph.toStringAsFixed(2), color: FieldColors.indigo),
              _MetricTile(label: 'Humidity %', value: humidity.toStringAsFixed(0), color: FieldColors.amber),
              _MetricTile(label: 'Battery %', value: battery.toStringAsFixed(0), color: FieldColors.indigo),
              _MetricTile(label: 'LoRa RSSI', value: '$rssi dBm', color: FieldColors.emerald),
            ],
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'Offline queue (SQLite): $_pendingQueue readings. '
                'Auto-flush when connectivity returns, or tap cloud upload. '
                'Bulk endpoint: POST /api/v1/telemetry/bulk (operator JWT). '
                'Set apiDeviceId to a fleet UUID for successful upload.',
                style: const TextStyle(color: FieldColors.inkMuted),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({required this.label, required this.value, required this.color});

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 150,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: const TextStyle(color: FieldColors.inkMuted, fontSize: 12)),
              const SizedBox(height: 6),
              Text(
                value,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: color),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

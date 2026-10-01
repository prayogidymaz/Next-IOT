import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/field_theme.dart';
import '../auth/auth_controller.dart';
import 'scanner_service.dart';

class DeviceScannerScreen extends ConsumerStatefulWidget {
  const DeviceScannerScreen({super.key});

  @override
  ConsumerState<DeviceScannerScreen> createState() => _DeviceScannerScreenState();
}

class _DeviceScannerScreenState extends ConsumerState<DeviceScannerScreen> {
  late final ScannerService _scanner;
  StreamSubscription<List<DiscoveredDevice>>? _sub;
  List<DiscoveredDevice> _devices = const [];

  @override
  void initState() {
    super.initState();
    _scanner = ScannerService(apiClient: ref.read(fieldApiProvider));
    _sub = _scanner.stream.listen((items) => setState(() => _devices = items));
    unawaited(_scanner.start());
  }

  @override
  void dispose() {
    _sub?.cancel();
    _scanner.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Device scanner')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Bluetooth LE + local Wi-Fi discovery (ESP32-S3 / Orange Pi field nodes).',
            style: TextStyle(color: FieldColors.inkMuted),
          ),
          const SizedBox(height: 16),
          ..._devices.map(
            (d) => Card(
              child: ListTile(
                leading: Icon(
                  d.transport == 'ble' ? Icons.bluetooth : Icons.wifi,
                  color: FieldColors.indigo,
                ),
                title: Text(d.name),
                subtitle: Text(
                  '${d.transport.toUpperCase()} · ${d.address} · RSSI ${d.rssi}'
                  '${d.apiDeviceId != null ? '\nPaired UUID ${d.apiDeviceId!.substring(0, 8)}…' : '\nUnpaired — add ble_mac/field_slug in device metadata'}',
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go('/hud', extra: d),
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _scanner.rescan,
        label: const Text('Rescan'),
        icon: const Icon(Icons.radar),
      ),
    );
  }
}

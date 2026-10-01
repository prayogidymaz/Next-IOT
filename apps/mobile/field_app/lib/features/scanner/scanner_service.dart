import 'dart:async';
import 'dart:io' show Platform;

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'package:permission_handler/permission_handler.dart';

import '../../core/api/field_api_client.dart';
import '../../core/discovery/mdns_discovery_service.dart';
import '../../core/pairing/device_pairing_registry.dart';

class DiscoveredDevice {
  const DiscoveredDevice({
    required this.id,
    required this.name,
    required this.address,
    required this.transport,
    required this.rssi,
    this.bleRemoteId,
    this.apiDeviceId,
    this.mdnsHost,
  });

  final String id;
  final String name;
  final String address;
  final String transport;
  final int rssi;
  final String? bleRemoteId;
  final String? apiDeviceId;
  final String? mdnsHost;

  DiscoveredDevice copyWith({String? apiDeviceId}) {
    return DiscoveredDevice(
      id: id,
      name: name,
      address: address,
      transport: transport,
      rssi: rssi,
      bleRemoteId: bleRemoteId,
      apiDeviceId: apiDeviceId ?? this.apiDeviceId,
      mdnsHost: mdnsHost,
    );
  }
}

class ScannerService {
  ScannerService({FieldApiClient? apiClient}) : _apiClient = apiClient;

  final FieldApiClient? _apiClient;

  late final StreamController<List<DiscoveredDevice>> _controller =
      StreamController<List<DiscoveredDevice>>.broadcast();
  StreamSubscription<List<ScanResult>>? _scanSub;
  StreamSubscription<List<MdnsEndpoint>>? _mdnsSub;
  final MdnsDiscoveryService _mdns = MdnsDiscoveryService();
  Timer? _mockTimer;
  final Map<String, DiscoveredDevice> _merged = {};
  DevicePairingRegistry _pairing = DevicePairingRegistry([]);

  Stream<List<DiscoveredDevice>> get stream => _controller.stream;

  bool get _nativeBle => !kIsWeb && (Platform.isAndroid || Platform.isIOS);

  Future<void> start() async {
    _merged.clear();
    await _loadPairingRegistry();
    _emit();

    _mdnsSub = _mdns.stream.listen(_onMdnsResults);
    await _mdns.start();

    if (!_nativeBle) {
      _startMockFallback();
      return;
    }

    final supported = await FlutterBluePlus.isSupported;
    if (!supported) {
      _startMockFallback();
      return;
    }

    final granted = await _ensureBlePermissions();
    if (!granted) {
      _startMockFallback();
      return;
    }

    _scanSub = FlutterBluePlus.onScanResults.listen(_onScanResults);
    await FlutterBluePlus.startScan(timeout: const Duration(seconds: 15));
  }

  Future<void> _loadPairingRegistry() async {
    final api = _apiClient;
    if (api == null) return;
    try {
      final devices = await api.listDevices();
      _pairing = DevicePairingRegistry.fromApiDtos(devices);
    } catch (_) {
      _pairing = DevicePairingRegistry([]);
    }
  }

  Future<void> rescan() async {
    await _stopBleScanOnly();
    _merged.clear();
    await _loadPairingRegistry();
    _emit();
    await _mdns.start();
    if (!_nativeBle) {
      _startMockFallback();
      return;
    }
    final supported = await FlutterBluePlus.isSupported;
    if (!supported) {
      _startMockFallback();
      return;
    }
    await FlutterBluePlus.startScan(timeout: const Duration(seconds: 15));
  }

  void _onScanResults(List<ScanResult> results) {
    for (final result in results) {
      final device = result.device;
      final name = device.platformName.isNotEmpty
          ? device.platformName
          : (device.advName.isNotEmpty ? device.advName : 'BLE peripheral');
      final remoteId = device.remoteId.str;
      final id = 'ble-$remoteId';
      final discovered = DiscoveredDevice(
        id: id,
        name: name,
        address: remoteId,
        transport: 'ble',
        rssi: result.rssi,
        bleRemoteId: remoteId,
      );
      _merged[id] = _applyPairing(discovered);
    }
    _emit();
  }

  void _onMdnsResults(List<MdnsEndpoint> endpoints) {
    for (final endpoint in endpoints) {
      final slug = DevicePairingRegistry.normalizeSlug(endpoint.serviceName);
      final id = 'wifi-$slug-${endpoint.ip}';
      final discovered = DiscoveredDevice(
        id: id,
        name: endpoint.serviceName,
        address: endpoint.ip,
        transport: 'wifi',
        rssi: -40 - (endpoint.port % 20),
        mdnsHost: endpoint.host,
      );
      _merged[id] = _applyPairing(discovered);
    }
    if (endpoints.isEmpty && _merged.values.every((d) => d.transport != 'wifi')) {
      /* no mDNS nodes — do not inject stub in production path */
    }
    _emit();
  }

  DiscoveredDevice _applyPairing(DiscoveredDevice device) {
    final apiId = _pairing.resolve(
      bleMac: device.bleRemoteId ?? device.address,
      localSlug: device.id,
      mdnsHost: device.mdnsHost ?? device.name,
      displayName: device.name,
    );
    if (apiId == null) return device;
    return device.copyWith(apiDeviceId: apiId);
  }

  void _startMockFallback() {
    const mockBase = DiscoveredDevice(
      id: 'esp32-mock',
      name: 'ESP32-S3 Biofloc Node (simulator)',
      address: 'AA:BB:CC:11:22:33',
      transport: 'ble',
      rssi: -58,
      bleRemoteId: 'AA:BB:CC:11:22:33',
    );
    _merged['esp32-mock'] = _applyPairing(mockBase);

    const lan = DiscoveredDevice(
      id: 'wifi-orangepi-edge-1',
      name: 'orangepi-edge-1._next-iot._tcp.local',
      address: '192.168.4.12',
      transport: 'wifi',
      rssi: -42,
      mdnsHost: 'orangepi-edge-1.local',
    );
    _merged['wifi-orangepi-edge-1'] = _applyPairing(lan);
    _mockTimer = Timer.periodic(const Duration(seconds: 6), (_) => _emit());
  }

  Future<bool> _ensureBlePermissions() async {
    if (Platform.isAndroid) {
      final scan = await Permission.bluetoothScan.request();
      final connect = await Permission.bluetoothConnect.request();
      final location = await Permission.locationWhenInUse.request();
      return scan.isGranted && connect.isGranted && location.isGranted;
    }
    if (Platform.isIOS) {
      final bt = await Permission.bluetooth.request();
      return bt.isGranted;
    }
    return true;
  }

  void _emit() {
    if (_controller.isClosed) return;
    final list = _merged.values.map(_applyPairing).toList()
      ..sort((a, b) => b.rssi.compareTo(a.rssi));
    _controller.add(list);
  }

  Future<void> _stopBleScanOnly() async {
    _mockTimer?.cancel();
    _mockTimer = null;
    if (_nativeBle && await FlutterBluePlus.isSupported) {
      try {
        await FlutterBluePlus.stopScan();
      } catch (_) {
        /* ignore */
      }
    }
  }

  Future<void> dispose() async {
    await _scanSub?.cancel();
    _scanSub = null;
    await _mdnsSub?.cancel();
    _mdnsSub = null;
    await _stopBleScanOnly();
    await _mdns.dispose();
    if (!_controller.isClosed) {
      await _controller.close();
    }
  }
}

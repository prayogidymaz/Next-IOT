import 'dart:async';
import 'dart:io' show Platform;

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:multicast_dns/multicast_dns.dart';

class MdnsEndpoint {
  const MdnsEndpoint({
    required this.serviceName,
    required this.host,
    required this.ip,
    required this.port,
  });

  final String serviceName;
  final String host;
  final String ip;
  final int port;
}

/// Local LAN discovery for ESP32 / Orange Pi (_next-iot._tcp).
class MdnsDiscoveryService {
  static const serviceTypes = [
    '_next-iot._tcp.local',
    '_nextiot._tcp.local',
    '_next-iot-edge._tcp.local',
  ];

  static const _nameHints = ['next-iot', 'nextiot', 'esp32', 'orangepi', 'biofloc'];

  MDnsClient? _client;
  Timer? _pollTimer;
  bool _running = false;
  final _endpoints = <String, MdnsEndpoint>{};
  final _controller = StreamController<List<MdnsEndpoint>>.broadcast();

  Stream<List<MdnsEndpoint>> get stream => _controller.stream;

  bool get _supported => !kIsWeb && (Platform.isAndroid || Platform.isIOS || Platform.isMacOS || Platform.isLinux);

  Future<void> start() async {
    if (!_supported) {
      _controller.add(const []);
      return;
    }
    if (_running) {
      await _scanOnce();
      return;
    }
    _client ??= MDnsClient();
    await _client!.start();
    _running = true;
    await _scanOnce();
    _pollTimer = Timer.periodic(const Duration(seconds: 12), (_) => _scanOnce());
  }

  Future<void> _scanOnce() async {
    final client = _client;
    if (client == null) return;
    try {
      for (final serviceType in serviceTypes) {
        await for (final PtrResourceRecord ptr in client.lookup<PtrResourceRecord>(
          ResourceRecordQuery.serverPointer(serviceType),
        )) {
          final serviceName = ptr.domainName;
          if (!_looksLikeFieldNode(serviceName)) continue;

          await for (final SrvResourceRecord srv in client.lookup<SrvResourceRecord>(
            ResourceRecordQuery.service(serviceName),
          )) {
            var ip = '';
            await for (final IPAddressResourceRecord a in client.lookup<IPAddressResourceRecord>(
              ResourceRecordQuery.addressIPv4(srv.target),
            )) {
              ip = a.address.address;
              break;
            }
            if (ip.isEmpty) continue;
            final host = srv.target;
            _endpoints[serviceName] = MdnsEndpoint(
              serviceName: serviceName,
              host: host,
              ip: ip,
              port: srv.port,
            );
          }
        }
      }
    } catch (_) {
      /* LAN mDNS may be blocked — keep last results */
    }
    _controller.add(_endpoints.values.toList());
  }

  bool _looksLikeFieldNode(String name) {
    final lower = name.toLowerCase();
    return _nameHints.any((hint) => lower.contains(hint));
  }

  Future<void> dispose() async {
    _pollTimer?.cancel();
    _pollTimer = null;
    _client?.stop();
    _client = null;
    _running = false;
    if (!_controller.isClosed) {
      await _controller.close();
    }
  }
}

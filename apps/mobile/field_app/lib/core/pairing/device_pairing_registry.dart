import '../models/field_api_models.dart';

class FleetDeviceRecord {
  FleetDeviceRecord({
    required this.id,
    required this.name,
    required this.metadata,
  });

  final String id;
  final String name;
  final Map<String, String> metadata;
}

/// Maps BLE MAC / field slug / mDNS host → PostgreSQL device UUID from fleet API.
class DevicePairingRegistry {
  DevicePairingRegistry(this._records);

  final List<FleetDeviceRecord> _records;

  static DevicePairingRegistry fromFleetDevices(List<FleetDeviceRecord> devices) {
    return DevicePairingRegistry(devices.where((r) => r.id.isNotEmpty).toList());
  }

  static DevicePairingRegistry fromApiDtos(List<FleetDeviceDto> devices) {
    final records = devices
        .map(
          (dto) => FleetDeviceRecord(
            id: dto.id,
            name: dto.name,
            metadata: {for (final m in dto.metadata) m.key: m.value},
          ),
        )
        .toList();
    return fromFleetDevices(records);
  }

  String? resolve({
    String? bleMac,
    String? localSlug,
    String? mdnsHost,
    String? displayName,
  }) {
    final mac = normalizeMac(bleMac);
    final slug = normalizeSlug(localSlug ?? displayName ?? '');
    final host = (mdnsHost ?? '').toLowerCase();

    for (final record in _records) {
      if (_matchMac(record, mac)) return record.id;
      if (slug.isNotEmpty && _matchSlug(record, slug)) return record.id;
      if (host.isNotEmpty && _matchMdns(record, host)) return record.id;
      if (displayName != null && _matchSlug(record, normalizeSlug(displayName))) {
        return record.id;
      }
    }
    return null;
  }

  bool _matchMac(FleetDeviceRecord record, String mac) {
    if (mac.isEmpty) return false;
    for (final key in const ['ble_mac', 'bluetooth_mac', 'mac_address', 'mac']) {
      final candidate = normalizeMac(record.metadata[key]);
      if (candidate.isNotEmpty && candidate == mac) return true;
    }
    return false;
  }

  bool _matchSlug(FleetDeviceRecord record, String slug) {
    if (slug.isEmpty) return false;
    for (final key in const ['field_slug', 'slug', 'edge_slug']) {
      final candidate = normalizeSlug(record.metadata[key]);
      if (candidate.isNotEmpty && candidate == slug) return true;
    }
    final nameSlug = normalizeSlug(record.name);
    return nameSlug.isNotEmpty && nameSlug == slug;
  }

  bool _matchMdns(FleetDeviceRecord record, String host) {
    for (final key in const ['mdns_name', 'mdns_host', 'lan_host', 'hostname']) {
      final candidate = (record.metadata[key] ?? '').toLowerCase();
      if (candidate.isEmpty) continue;
      if (host.contains(candidate) || candidate.contains(host.split('.').first)) {
        return true;
      }
    }
    final slug = normalizeSlug(record.metadata['field_slug'] ?? record.name);
    if (slug.isNotEmpty && host.contains(slug)) return true;
    return false;
  }

  static String normalizeMac(String? raw) {
    if (raw == null || raw.isEmpty) return '';
    return raw.replaceAll(':', '').replaceAll('-', '').toUpperCase();
  }

  static String normalizeSlug(String? raw) {
    if (raw == null || raw.isEmpty) return '';
    var s = raw.toLowerCase();
    if (s.startsWith('ble-')) s = s.substring(4);
    if (s.startsWith('wifi-')) s = s.substring(5);
    return s.replaceAll(RegExp(r'[^a-z0-9]+'), '-').replaceAll(RegExp(r'^-|-$'), '');
  }
}

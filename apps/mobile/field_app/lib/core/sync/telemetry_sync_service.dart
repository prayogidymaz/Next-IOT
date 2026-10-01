import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';

import '../api/field_api_client.dart';
import '../storage/offline_telemetry_store.dart';

class TelemetrySyncResult {
  const TelemetrySyncResult({
    required this.synced,
    required this.failed,
    required this.skipped,
  });

  final int synced;
  final int failed;
  final int skipped;
}

class TelemetrySyncService {
  TelemetrySyncService({
    OfflineTelemetryStore? store,
    Connectivity? connectivity,
  })  : _store = store ?? OfflineTelemetryStore(),
        _connectivity = connectivity ?? Connectivity();

  final OfflineTelemetryStore _store;
  final Connectivity _connectivity;

  Future<bool> get hasNetwork async {
    final results = await _connectivity.checkConnectivity();
    return results.any((r) => r != ConnectivityResult.none);
  }

  Future<int> pendingCount() => _store.pendingCount();

  Future<TelemetrySyncResult> flush({required FieldApiClient api, int batchSize = 50}) async {
    if (!await hasNetwork) {
      final pending = await _store.pendingCount();
      return TelemetrySyncResult(synced: 0, failed: 0, skipped: pending);
    }

    final rows = await _store.pendingRows(limit: batchSize);
    if (rows.isEmpty) {
      return const TelemetrySyncResult(synced: 0, failed: 0, skipped: 0);
    }

    final items = <Map<String, Object?>>[];
    final rowIds = <int>[];
    var skipped = 0;

    for (final row in rows) {
      final id = row['id'] as int?;
      final deviceId = row['device_id'] as String? ?? '';
      if (!_isUuid(deviceId)) {
        skipped++;
        continue;
      }
      final createdAt = row['created_at'] as String? ?? DateTime.now().toIso8601String();
      final metricsRaw = row['metrics_json'] as String? ?? '{}';
      items.add({
        'device_id': deviceId,
        'timestamp': createdAt,
        'metrics': _decodeMetrics(metricsRaw),
      });
      if (id != null) rowIds.add(id);
    }

    if (items.isEmpty) {
      return TelemetrySyncResult(synced: 0, failed: 0, skipped: skipped);
    }

    try {
      final response = await api.pushTelemetryBulk(items: items);
      final accepted = response.accepted;
      if (accepted > 0 && rowIds.isNotEmpty) {
        final toDelete = rowIds.take(accepted).toList();
        await _store.deleteRows(toDelete);
      }
      final failed = items.length - accepted;
      return TelemetrySyncResult(synced: accepted, failed: failed, skipped: skipped);
    } catch (_) {
      return TelemetrySyncResult(synced: 0, failed: items.length, skipped: skipped);
    }
  }

  bool _isUuid(String value) {
    final re = RegExp(
      r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
    );
    return re.hasMatch(value);
  }

  Map<String, Object?> _decodeMetrics(String raw) {
    try {
      final decoded = jsonDecode(raw);
      if (decoded is Map<Object?, Object?>) {
        return decoded.map((k, v) => MapEntry(k.toString(), v));
      }
      return const {};
    } catch (_) {
      return const {};
    }
  }
}

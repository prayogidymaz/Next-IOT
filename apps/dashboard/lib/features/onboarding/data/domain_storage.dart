import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../models/operational_domain.dart';

class DomainStorage {
  DomainStorage({FlutterSecureStorage? secure})
      : _secure = secure ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
            );

  static const _domainKey = 'operational_domain';
  static const _segmentKey = 'enterprise_segment';

  final FlutterSecureStorage _secure;

  Future<void> save({
    required OperationalDomain domain,
    required EnterpriseSegment segment,
  }) async {
    await _secure.write(key: _domainKey, value: domain.name);
    await _secure.write(key: _segmentKey, value: segment.name);
  }

  Future<OperationalDomain?> readDomain() async {
    final raw = await _secure.read(key: _domainKey);
    return OperationalDomainMeta.fromStorage(raw);
  }

  Future<EnterpriseSegment?> readSegment() async {
    final raw = await _secure.read(key: _segmentKey);
    return EnterpriseSegmentMeta.fromStorage(raw);
  }

  Future<void> clear() async {
    await _secure.delete(key: _domainKey);
    await _secure.delete(key: _segmentKey);
  }

  Future<bool> hasSelection() async {
    final domain = await readDomain();
    return domain != null;
  }
}

import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/models/ota_models.dart';

void main() {
  test('FirmwareRelease.fromJson parses release', () {
    final release = FirmwareRelease.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'version': '2.0.1',
      'target_device_category': 'SMART_HOME',
      'file_url': '/api/v1/ota/device/releases/x/download',
      'checksum_sha256': 'abc',
      'status': 'active',
      'created_at': '2026-09-17T10:00:00Z',
    });
    expect(release.version, '2.0.1');
    expect(release.isActive, isTrue);
  });
}

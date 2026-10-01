import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/devices/data/smart_home_device_seed.dart';
import 'package:next_iot_dashboard/features/devices/models/device_models.dart';

void main() {
  test('mergeSmartHomeSeed adds demo devices once', () {
    final merged = mergeSmartHomeSeed(const []);
    expect(merged.length, 5);
    expect(
      merged.every(
        (d) =>
            d.deviceType == DeviceType.smartHome.apiValue &&
            d.deviceCategory == DeviceCategoryApi.smartHome,
      ),
      isTrue,
    );

    final again = mergeSmartHomeSeed(merged);
    expect(again.length, 5);
  });
}

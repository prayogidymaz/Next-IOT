import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/hardware/models/gateway_models.dart';

void main() {
  test('GatewayStatus.fromJson parses gateway status payload', () {
    final status = GatewayStatus.fromJson({
      'serial_connected': true,
      'serial_port': '/dev/ttyUSB0',
      'lora_link': 'connected',
      'rssi': -82.5,
      'snr': 8.1,
      'packets_received': 15,
    });

    expect(status.serialConnected, isTrue);
    expect(status.loraLink, 'connected');
    expect(status.rssi, -82.5);
    expect(status.isLinkHealthy, isTrue);
  });
}

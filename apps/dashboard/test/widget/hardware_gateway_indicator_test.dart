import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/core/widgets/hardware_gateway_indicator.dart';
import 'package:next_iot_dashboard/features/hardware/data/hardware_repository.dart';
import 'package:next_iot_dashboard/features/hardware/models/gateway_models.dart';
import 'package:next_iot_dashboard/features/hardware/providers/gateway_provider.dart';

class _TestGatewayNotifier extends GatewayNotifier {
  _TestGatewayNotifier(GatewayStatus initial) : super(HardwareRepository()) {
    state = initial;
  }

  @override
  Future<void> refresh() async {}
}

void main() {
  testWidgets('HardwareGatewayIndicator shows serial and LoRa badges', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          gatewayStatusProvider.overrideWith(
            (ref) => _TestGatewayNotifier(
              const GatewayStatus(
                serialConnected: true,
                serialPort: 'COM3',
                loraLink: 'connected',
                rssi: -78,
                snr: 9.2,
                packetsReceived: 4,
              ),
            ),
          ),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: Center(child: HardwareGatewayIndicator()),
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.textContaining('SERIAL'), findsOneWidget);
    expect(find.textContaining('LoRa CONNECTED'), findsOneWidget);
    expect(find.textContaining('-78 dBm'), findsOneWidget);
  });
}

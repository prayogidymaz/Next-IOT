import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/cyberdeck/data/cyberdeck_repository.dart';
import 'package:next_iot_dashboard/features/cyberdeck/models/cyberdeck_models.dart';
import 'package:next_iot_dashboard/features/cyberdeck/providers/cyberdeck_provider.dart';
import 'package:next_iot_dashboard/features/cyberdeck/screens/cyberdeck_console_screen.dart';

class _TestCyberdeckNotifier extends CyberdeckNotifier {
  _TestCyberdeckNotifier(CyberdeckState initial) : super(CyberdeckRepository()) {
    state = initial;
  }

  @override
  Future<void> load() async {}
}

void main() {
  testWidgets('CyberdeckConsoleScreen renders PTT and mesh panels', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          cyberdeckProvider.overrideWith(
            (ref) => _TestCyberdeckNotifier(
              CyberdeckState(
                nodes: const [
                  CyberdeckMeshNode(nodeId: 'CDK-01', label: 'Cyberdeck Unit 1', deviceType: 'cyberdeck', rssi: -80),
                ],
                channel: 2,
              ),
            ),
          ),
        ],
        child: const MaterialApp(home: CyberdeckConsoleScreen()),
      ),
    );
    await tester.pump();

    expect(find.text('CYBERDECK // LoRa PTT CONSOLE'), findsOneWidget);
    expect(find.byKey(const Key('cyberdeck-ptt-panel')), findsOneWidget);
    expect(find.byKey(const Key('cyberdeck-mesh-panel')), findsOneWidget);
    expect(find.text('HOLD TO PTT'), findsOneWidget);
    expect(find.text('Cyberdeck Unit 1'), findsOneWidget);
  });
}

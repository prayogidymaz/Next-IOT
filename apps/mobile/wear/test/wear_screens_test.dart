import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:flutter_test/flutter_test.dart";
import "package:next_iot_wear/screens/alert_center.dart";
import "package:next_iot_wear/screens/irrigation_control.dart";
import "package:next_iot_wear/screens/sensor_monitor.dart";
import "package:next_iot_wear/screens/watch_face.dart";
import "package:next_iot_wear/theme/tactical_warm_cream.dart";

void main() {
  Widget wrap(Widget child) {
    return ProviderScope(
      child: MaterialApp(theme: TacticalWarmCream.theme(), home: child),
    );
  }

  testWidgets("watch face renders KPI cards", (tester) async {
    await tester.pumpWidget(wrap(const WatchFaceScreen()));
    await tester.pumpAndSettle();
    expect(find.text("Field mesh"), findsOneWidget);
  });

  testWidgets("sensor monitor renders", (tester) async {
    await tester.pumpWidget(wrap(const SensorMonitorScreen()));
    await tester.pumpAndSettle();
    expect(find.textContaining("swipe"), findsOneWidget);
  });

  testWidgets("irrigation control renders valve state", (tester) async {
    await tester.pumpWidget(wrap(const IrrigationControlScreen()));
    expect(find.text("Valve CLOSED"), findsOneWidget);
  });

  testWidgets("alert center renders stream", (tester) async {
    await tester.pumpWidget(wrap(const AlertCenterScreen()));
    await tester.pumpAndSettle();
    expect(find.textContaining("Intrusion"), findsOneWidget);
  });

  test("tactical theme uses warm cream base", () {
    expect(TacticalWarmCream.base, const Color(0xFFF5EFE0));
    expect(TacticalWarmCream.olive, const Color(0xFF556B4A));
  });
}

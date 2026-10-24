import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "providers/mesh_connection.dart";
import "screens/alert_center.dart";
import "screens/irrigation_control.dart";
import "screens/sensor_monitor.dart";
import "screens/watch_face.dart";
import "theme/tactical_warm_cream.dart";

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: WearCompanionApp()));
}

class WearCompanionApp extends ConsumerStatefulWidget {
  const WearCompanionApp({super.key});

  @override
  ConsumerState<WearCompanionApp> createState() => _WearCompanionAppState();
}

class _WearCompanionAppState extends ConsumerState<WearCompanionApp> {
  final _pageController = PageController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(meshConnectionProvider.notifier).connectSkeleton();
    });
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Next-IoT Wear",
      theme: TacticalWarmCream.theme(),
      home: Scaffold(
        body: PageView(
          controller: _pageController,
          children: const [
            WatchFaceScreen(),
            SensorMonitorScreen(),
            IrrigationControlScreen(),
            AlertCenterScreen(),
          ],
        ),
      ),
    );
  }
}

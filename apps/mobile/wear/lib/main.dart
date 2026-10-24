import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "providers/mesh_connection.dart";
import "screens/alert_center.dart";
import "screens/irrigation_control.dart";
import "screens/pairing.dart";
import "screens/sensor_monitor.dart";
import "screens/watch_face.dart";
import "services/auth_storage.dart";
import "providers/sensor_provider.dart";
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
  bool _paired = false;
  bool _booted = false;

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    final jwt = await AuthStorage().readJwt();
    if (jwt != null && jwt.isNotEmpty) {
      ref.read(meshApiProvider).setJwt(jwt);
      ref.read(meshConnectionProvider.notifier).connectLive(jwt);
      setState(() {
        _paired = true;
        _booted = true;
      });
      return;
    }
    ref.read(meshConnectionProvider.notifier).connectSkeleton();
    setState(() => _booted = true);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_booted) {
      return MaterialApp(
        theme: TacticalWarmCream.theme(),
        home: const Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }
    if (!_paired) {
      return MaterialApp(
        theme: TacticalWarmCream.theme(),
        home: PairingScreen(onPaired: () => setState(() => _paired = true)),
      );
    }
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

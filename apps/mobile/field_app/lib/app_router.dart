import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'features/auth/auth_controller.dart';
import 'features/auth/login_screen.dart';
import 'features/hud/tactical_hud_screen.dart';
import 'features/scanner/device_scanner_screen.dart';
import 'features/scanner/scanner_service.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authControllerProvider);

  return GoRouter(
    initialLocation: '/login',
    refreshListenable: _AuthRefresh(ref),
    redirect: (context, state) {
      final loggedIn = auth.isAuthenticated;
      final onLogin = state.matchedLocation == '/login';
      if (!loggedIn && !onLogin) return '/login';
      if (loggedIn && onLogin) return '/scanner';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/scanner', builder: (_, __) => const DeviceScannerScreen()),
      GoRoute(
        path: '/hud',
        builder: (context, state) {
          final device = state.extra as DiscoveredDevice?;
          return TacticalHudScreen(device: device);
        },
      ),
    ],
  );
});

class _AuthRefresh extends ChangeNotifier {
  _AuthRefresh(this._ref) {
    _ref.listen(authControllerProvider, (_, __) => notifyListeners());
  }

  final Ref _ref;
}

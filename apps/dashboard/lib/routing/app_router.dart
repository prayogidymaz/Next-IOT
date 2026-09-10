import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/providers/auth_provider.dart';
import '../features/auth/screens/home_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/devices/models/device_models.dart';
import '../features/devices/screens/device_detail_screen.dart';
import '../features/devices/screens/device_list_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final loggingIn = state.matchedLocation == '/login';
      if (!authState.isAuthenticated && !loggingIn) return '/login';
      if (authState.isAuthenticated && loggingIn) return '/home';
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) {
          final tab = state.uri.queryParameters['tab'];
          final initialTab = switch (tab) {
            'alerts' => 2,
            'map' => 1,
            _ => 0,
          };
          return HomeScreen(initialTab: initialTab);
        },
      ),
      GoRoute(
        path: '/devices',
        builder: (context, state) => const Scaffold(
          body: SafeArea(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: DeviceListScreen(),
            ),
          ),
        ),
      ),
      GoRoute(
        path: '/devices/:id',
        builder: (context, state) {
          final deviceId = state.pathParameters['id']!;
          final device = state.extra as Device?;
          return DeviceDetailScreen(deviceId: deviceId, device: device);
        },
      ),
    ],
    refreshListenable: _RouterRefresh(ref),
  );
});

class _RouterRefresh extends ChangeNotifier {
  _RouterRefresh(this.ref) {
    ref.listen<AuthState>(authProvider, (_, __) => notifyListeners());
  }

  final Ref ref;
}

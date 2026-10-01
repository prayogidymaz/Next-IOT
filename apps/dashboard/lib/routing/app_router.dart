import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/providers/auth_provider.dart';
import '../features/auth/screens/home_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/devices/models/device_models.dart';
import '../features/alerts/screens/alert_engine_screen.dart';
import '../features/studio/screens/automation_studio_screen.dart';
import '../features/devices/screens/device_detail_screen.dart';
import '../features/devices/screens/device_list_screen.dart';
import '../features/devices/screens/ota_firmware_screen.dart';
import '../features/audit/screens/audit_log_screen.dart';
import '../features/settings/screens/organization_members_screen.dart';
import '../features/telemetry/screens/telemetry_analytics_screen.dart';
import '../features/cyberdeck/screens/cyberdeck_console_screen.dart';
import '../features/onboarding/providers/domain_context_provider.dart';
import '../features/onboarding/screens/domain_onboarding_screen.dart';
import 'navigation_config.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);
  final domainState = ref.watch(domainContextProvider);

  return GoRouter(
    initialLocation: AppRoutes.login,
    redirect: (context, state) {
      if (authState.isLoading || domainState.isLoading) return null;
      final path = state.matchedLocation;
      final loggingIn = path == AppRoutes.login;
      final onboarding = path == AppRoutes.onboarding;
      if (!authState.isAuthenticated && !loggingIn) return AppRoutes.login;
      if (authState.isAuthenticated && loggingIn) {
        return domainState.hasSelection ? AppRoutes.dashboard : AppRoutes.onboarding;
      }
      if (authState.isAuthenticated && !domainState.hasSelection && !onboarding) {
        return AppRoutes.onboarding;
      }
      if (authState.isAuthenticated && domainState.hasSelection && onboarding) {
        return AppRoutes.dashboard;
      }
      if (path == AppRoutes.dashboard &&
          state.uri.queryParameters['tab'] == 'alerts') {
        return AppRoutes.alerts;
      }
      return null;
    },
    routes: [
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: AppRoutes.onboarding,
        builder: (context, state) => const DomainOnboardingScreen(),
      ),
      GoRoute(
        path: AppRoutes.dashboard,
        builder: (context, state) {
          final tab = state.uri.queryParameters['tab'];
          final initialTab = switch (tab) {
            'map' => 1,
            _ => 0,
          };
          return HomeScreen(initialTab: initialTab);
        },
      ),
      GoRoute(
        path: AppRoutes.home,
        redirect: (_, __) => AppRoutes.dashboard,
      ),
      GoRoute(
        path: AppRoutes.mapView,
        redirect: (_, __) => '${AppRoutes.dashboard}?tab=map',
      ),
      GoRoute(
        path: AppRoutes.alerts,
        builder: (context, state) => const AlertEngineScreen(),
      ),
      GoRoute(
        path: AppRoutes.studio,
        builder: (context, state) => const AutomationStudioScreen(),
      ),
      GoRoute(
        path: AppRoutes.automation,
        redirect: (_, __) => AppRoutes.studio,
      ),
      GoRoute(
        path: AppRoutes.devices,
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
        path: AppRoutes.devicesOta,
        builder: (context, state) => const OtaFirmwareScreen(),
      ),
      GoRoute(
        path: AppRoutes.settings,
        builder: (context, state) => const OrganizationMembersScreen(),
      ),
      GoRoute(
        path: AppRoutes.audit,
        builder: (context, state) => const AuditLogScreen(),
      ),
      GoRoute(
        path: AppRoutes.analytics,
        builder: (context, state) {
          final deviceId = state.uri.queryParameters['device'];
          return TelemetryAnalyticsScreen(initialDeviceId: deviceId);
        },
      ),
      GoRoute(
        path: AppRoutes.cyberdeck,
        builder: (context, state) => const CyberdeckConsoleScreen(),
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
    ref.listen<DomainContextState>(domainContextProvider, (_, __) => notifyListeners());
  }

  final Ref ref;
}

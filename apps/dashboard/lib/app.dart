import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/theme/tactical_theme.dart';
import 'features/auth/providers/auth_provider.dart';
import 'features/auth/providers/permissions_provider.dart';
import 'features/tenants/providers/tenant_provider.dart';
import 'routing/app_router.dart';

/// Keeps permissions + tenant list in sync with auth session.
final sessionSyncProvider = Provider<void>((ref) {
  ref.listen<AuthState>(authProvider, (previous, next) {
    if (next.isAuthenticated && next.user != null) {
      final user = next.user!;
      ref.read(permissionsProvider.notifier).seedFromRole(
            role: user.role,
            tenantId: user.tenantId,
            userId: user.userId,
          );
      ref.read(permissionsProvider.notifier).refresh();
      ref.read(tenantProvider.notifier).loadTenants();
    } else {
      ref.read(permissionsProvider.notifier).clear();
      ref.read(tenantProvider.notifier).clear();
    }
  }, fireImmediately: true);
});

class NextIotApp extends ConsumerWidget {
  const NextIotApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(sessionSyncProvider);
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'Next-IOT Dashboard',
      debugShowCheckedModeBanner: false,
      theme: buildTacticalTheme(),
      routerConfig: router,
    );
  }
}

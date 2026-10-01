import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/providers/auth_provider.dart';
import '../../features/auth/providers/permissions_provider.dart';

/// Hides [child] when the active user lacks [permission].
class PermissionGuard extends ConsumerWidget {
  const PermissionGuard({
    super.key,
    required this.permission,
    required this.child,
    this.fallback,
  });

  final String permission;
  final Widget child;
  final Widget? fallback;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final allowed = ref.watch(
      permissionsProvider.select(
        (s) => s.can(permission, fallbackRole: auth.user?.role),
      ),
    );
    if (allowed) return child;
    if (fallback != null) return fallback!;
    return const SizedBox.shrink();
  }
}

extension PermissionRef on WidgetRef {
  bool hasPermission(String permission) =>
      read(permissionsProvider).can(permission);
}

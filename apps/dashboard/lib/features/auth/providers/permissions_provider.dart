import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../../core/rbac/role_permissions.dart';
import '../../../core/auth/token_storage.dart';
import '../data/permissions_repository.dart';
import '../models/permissions_models.dart';

final permissionsRepositoryProvider =
    Provider<PermissionsRepository>((ref) => PermissionsRepository());

class PermissionsState {
  const PermissionsState({
    this.profile,
    this.isLoading = false,
    this.error,
  });

  final UserPermissions? profile;
  final bool isLoading;
  final String? error;

  bool can(String permission, {String? fallbackRole}) {
    if (profile != null) return profile!.can(permission);
    if (fallbackRole != null && roleCan(fallbackRole, permission)) return true;
    if (isLoading) return true;
    return false;
  }

  PermissionsState copyWith({
    UserPermissions? profile,
    bool? isLoading,
    String? error,
    bool clearProfile = false,
  }) {
    return PermissionsState(
      profile: clearProfile ? null : (profile ?? this.profile),
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class PermissionsNotifier extends StateNotifier<PermissionsState> {
  PermissionsNotifier(this._repository, {TokenStorage? tokenStorage})
      : _tokenStorage = tokenStorage ?? TokenStorage(),
        super(const PermissionsState());

  final PermissionsRepository _repository;
  final TokenStorage _tokenStorage;

  Future<void> refresh() async {
    final cached = state.profile;
    state = state.copyWith(isLoading: true, error: null);
    try {
      final profile = await _repository.fetchMyPermissions();
      await _tokenStorage.saveActiveTenantId(profile.tenantId);
      state = PermissionsState(profile: profile);
    } catch (e) {
      state = PermissionsState(
        profile: cached,
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void seedFromRole({required String role, required String tenantId, required String userId}) {
    if (state.profile != null) return;
    state = PermissionsState(
      profile: UserPermissions(
        userId: userId,
        tenantId: tenantId,
        role: role,
        permissions: permissionsForRole(role),
      ),
      isLoading: true,
    );
  }

  void clear() {
    state = const PermissionsState();
  }
}

final permissionsProvider =
    StateNotifierProvider<PermissionsNotifier, PermissionsState>((ref) {
  return PermissionsNotifier(ref.watch(permissionsRepositoryProvider));
});

/// Test helper — full tenant-admin capability set.
PermissionsNotifier fullAccessPermissionsNotifier(PermissionsRepository repo) {
  final notifier = PermissionsNotifier(repo);
  notifier.state = PermissionsState(
    profile: UserPermissions(
      userId: 'test',
      tenantId: 'test-tenant',
      role: 'tenant_admin',
      permissions: AppPermissions.all,
    ),
  );
  return notifier;
}

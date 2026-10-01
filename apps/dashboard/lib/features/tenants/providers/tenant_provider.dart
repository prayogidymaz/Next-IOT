import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/data/auth_repository.dart';
import '../../auth/providers/auth_provider.dart';
import '../../auth/providers/permissions_provider.dart';
import '../data/tenant_repository.dart';
import '../models/tenant_models.dart';

final tenantRepositoryProvider =
    Provider<TenantRepository>((ref) => TenantRepository());

class TenantState {
  const TenantState({
    this.tenants = const [],
    this.isLoading = false,
    this.isSwitching = false,
    this.error,
  });

  final List<TenantSummary> tenants;
  final bool isLoading;
  final bool isSwitching;
  final String? error;

  TenantSummary? activeTenant(String? activeId) {
    if (activeId == null) return null;
    for (final t in tenants) {
      if (t.id == activeId) return t;
    }
    return null;
  }

  TenantState copyWith({
    List<TenantSummary>? tenants,
    bool? isLoading,
    bool? isSwitching,
    String? error,
  }) {
    return TenantState(
      tenants: tenants ?? this.tenants,
      isLoading: isLoading ?? this.isLoading,
      isSwitching: isSwitching ?? this.isSwitching,
      error: error,
    );
  }
}

class TenantNotifier extends StateNotifier<TenantState> {
  TenantNotifier(this._repository, this._ref) : super(const TenantState());

  final TenantRepository _repository;
  final Ref _ref;

  Future<void> loadTenants() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final tenants = await _repository.listTenants();
      state = TenantState(tenants: tenants);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> switchTo(String tenantId) async {
    state = state.copyWith(isSwitching: true, error: null);
    try {
      await _repository.switchTenant(tenantId);
      await _ref.read(authProvider.notifier).refreshProfile();
      await _ref.read(permissionsProvider.notifier).refresh();
      await loadTenants();
      state = state.copyWith(isSwitching: false);
      return true;
    } catch (e) {
      state = state.copyWith(isSwitching: false, error: e.toString());
      return false;
    }
  }

  void clear() {
    state = const TenantState();
  }
}

final tenantProvider =
    StateNotifierProvider<TenantNotifier, TenantState>((ref) {
  return TenantNotifier(ref.watch(tenantRepositoryProvider), ref);
});

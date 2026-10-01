import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/audit_repository.dart';
import '../models/audit_log_models.dart';

final auditRepositoryProvider = Provider<AuditRepository>((ref) {
  return AuditRepository();
});

class AuditLogFilter {
  const AuditLogFilter({this.action, this.actor, this.page = 1});

  final String? action;
  final String? actor;
  final int page;

  AuditLogFilter copyWith({String? action, String? actor, int? page}) {
    return AuditLogFilter(
      action: action ?? this.action,
      actor: actor ?? this.actor,
      page: page ?? this.page,
    );
  }
}

class AuditLogState {
  const AuditLogState({
    this.page,
    this.isLoading = false,
    this.error,
    this.exporting = false,
  });

  final AuditLogPage? page;
  final bool isLoading;
  final String? error;
  final bool exporting;

  AuditLogState copyWith({
    AuditLogPage? page,
    bool? isLoading,
    String? error,
    bool? exporting,
    bool clearError = false,
  }) {
    return AuditLogState(
      page: page ?? this.page,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      exporting: exporting ?? this.exporting,
    );
  }
}

class AuditLogNotifier extends StateNotifier<AuditLogState> {
  AuditLogNotifier(this._repo) : super(const AuditLogState());

  final AuditRepository _repo;
  AuditLogFilter _filter = const AuditLogFilter();

  Future<void> load({AuditLogFilter? filter}) async {
    if (filter != null) _filter = filter;
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final page = await _repo.fetchLogs(
        action: _filter.action,
        actor: _filter.actor,
        page: _filter.page,
      );
      state = AuditLogState(page: page);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> exportCsv() async {
    state = state.copyWith(exporting: true, clearError: true);
    try {
      await _repo.downloadExportCsv(
        action: _filter.action,
        actor: _filter.actor,
      );
      state = state.copyWith(exporting: false);
    } catch (e) {
      state = state.copyWith(exporting: false, error: e.toString());
    }
  }
}

final auditLogProvider =
    StateNotifierProvider<AuditLogNotifier, AuditLogState>((ref) {
  return AuditLogNotifier(ref.watch(auditRepositoryProvider));
});

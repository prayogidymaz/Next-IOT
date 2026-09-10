import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/rule_repository.dart';
import '../models/rule_models.dart';

final ruleRepositoryProvider = Provider<RuleRepository>((ref) => RuleRepository());

class RuleListState {
  const RuleListState({
    this.rules = const [],
    this.isLoading = false,
    this.isSaving = false,
    this.error,
  });

  final List<AlertRule> rules;
  final bool isLoading;
  final bool isSaving;
  final String? error;

  RuleListState copyWith({
    List<AlertRule>? rules,
    bool? isLoading,
    bool? isSaving,
    String? error,
    bool clearError = false,
  }) {
    return RuleListState(
      rules: rules ?? this.rules,
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class RuleNotifier extends StateNotifier<RuleListState> {
  RuleNotifier(this._repository) : super(const RuleListState());

  final RuleRepository _repository;

  Future<void> loadRules() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final rules = await _repository.fetchRules();
      state = RuleListState(rules: rules);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: _mapError(e));
    }
  }

  Future<bool> createRule(CreateRuleRequest request) async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final rule = await _repository.createRule(request);
      state = state.copyWith(
        rules: [rule, ...state.rules],
        isSaving: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(isSaving: false, error: _mapError(e));
      return false;
    }
  }

  Future<bool> deleteRule(String ruleId) async {
    try {
      await _repository.deleteRule(ruleId);
      state = state.copyWith(
        rules: state.rules.where((r) => r.id != ruleId).toList(),
      );
      return true;
    } catch (e) {
      state = state.copyWith(error: _mapError(e));
      return false;
    }
  }

  String _mapError(Object e) {
    if (e is DioException && e.response?.statusCode == 403) {
      return 'You do not have permission to manage rules.';
    }
    return 'Failed to manage rules. Check connection and try again.';
  }
}

final ruleProvider = StateNotifierProvider<RuleNotifier, RuleListState>((ref) {
  return RuleNotifier(ref.watch(ruleRepositoryProvider));
});

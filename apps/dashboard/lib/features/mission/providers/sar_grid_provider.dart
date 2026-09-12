import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/sar_grid_repository.dart';
import '../models/sar_grid_models.dart';

final sarGridRepositoryProvider = Provider<SarGridRepository>((ref) => SarGridRepository());

class SarGridState {
  const SarGridState({
    this.visible = false,
    this.isLoading = false,
    this.result,
    this.error,
    this.pattern = SarGridPattern.expandingSquare,
    this.radiusM = 500,
  });

  final bool visible;
  final bool isLoading;
  final SarGridResult? result;
  final String? error;
  final SarGridPattern pattern;
  final double radiusM;

  SarGridState copyWith({
    bool? visible,
    bool? isLoading,
    SarGridResult? result,
    String? error,
    SarGridPattern? pattern,
    double? radiusM,
    bool clearResult = false,
    bool clearError = false,
  }) {
    return SarGridState(
      visible: visible ?? this.visible,
      isLoading: isLoading ?? this.isLoading,
      result: clearResult ? null : (result ?? this.result),
      error: clearError ? null : (error ?? this.error),
      pattern: pattern ?? this.pattern,
      radiusM: radiusM ?? this.radiusM,
    );
  }
}

class SarGridNotifier extends StateNotifier<SarGridState> {
  SarGridNotifier(this._repository) : super(const SarGridState());

  final SarGridRepository _repository;

  void clear() {
    state = const SarGridState();
  }

  void toggleVisibility() {
    state = state.copyWith(visible: !state.visible);
  }

  void applyResult(SarGridResult result) {
    state = state.copyWith(result: result, visible: true);
  }

  Future<void> generateFromLkp({
    required double lat,
    required double lon,
    SarGridPattern? pattern,
    double? radiusM,
  }) async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      pattern: pattern,
      radiusM: radiusM,
    );
    try {
      final result = await _repository.generateGrid(
        lkpLat: lat,
        lkpLon: lon,
        radiusM: radiusM ?? state.radiusM,
        pattern: pattern ?? state.pattern,
      );
      state = state.copyWith(
        isLoading: false,
        result: result,
        visible: true,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to generate SAR grid.',
      );
    }
  }
}

final sarGridProvider = StateNotifierProvider<SarGridNotifier, SarGridState>((ref) {
  return SarGridNotifier(ref.watch(sarGridRepositoryProvider));
});

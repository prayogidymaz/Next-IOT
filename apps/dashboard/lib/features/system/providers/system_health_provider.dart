import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/system_health_repository.dart';
import '../models/system_health_models.dart';

final systemHealthRepositoryProvider =
    Provider<SystemHealthRepository>((ref) => SystemHealthRepository());

class SystemHealthNotifier extends StateNotifier<AsyncValue<SystemHealthSnapshot>> {
  SystemHealthNotifier(this._repo) : super(const AsyncValue.loading()) {
    _poll();
  }

  final SystemHealthRepository _repo;
  Timer? _timer;

  Future<void> _poll() async {
    await refresh();
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 30), (_) => refresh());
  }

  Future<void> refresh() async {
    try {
      final snap = await _repo.fetchHealth();
      state = AsyncValue.data(snap);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}

final systemHealthProvider = StateNotifierProvider<SystemHealthNotifier,
    AsyncValue<SystemHealthSnapshot>>((ref) {
  return SystemHealthNotifier(ref.watch(systemHealthRepositoryProvider));
});

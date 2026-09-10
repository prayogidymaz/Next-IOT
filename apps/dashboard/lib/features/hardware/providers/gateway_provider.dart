import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/hardware_repository.dart';
import '../models/gateway_models.dart';

final hardwareRepositoryProvider = Provider<HardwareRepository>((ref) => HardwareRepository());

class GatewayNotifier extends StateNotifier<GatewayStatus> {
  GatewayNotifier(this._repository) : super(GatewayStatus.disconnected) {
    _poll();
  }

  final HardwareRepository _repository;
  Timer? _timer;

  Future<void> refresh() async {
    state = await _repository.fetchGatewayStatus();
  }

  void _poll() {
    refresh();
    _timer = Timer.periodic(const Duration(seconds: 2), (_) => refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}

final gatewayStatusProvider = StateNotifierProvider<GatewayNotifier, GatewayStatus>((ref) {
  return GatewayNotifier(ref.watch(hardwareRepositoryProvider));
});

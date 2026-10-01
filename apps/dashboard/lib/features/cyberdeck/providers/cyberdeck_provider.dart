import 'dart:async';
import 'dart:math';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/cyberdeck_repository.dart';
import '../models/cyberdeck_models.dart';

final cyberdeckRepositoryProvider = Provider<CyberdeckRepository>((ref) => CyberdeckRepository());

class CyberdeckState {
  const CyberdeckState({
    this.nodes = const [],
    this.health,
    this.channel = 1,
    this.selectedNodeId,
    this.isTransmitting = false,
    this.waveform = const [],
    this.isLoading = false,
    this.statusMessage,
    this.lastDispatch,
  });

  final List<CyberdeckMeshNode> nodes;
  final CyberdeckHealth? health;
  final int channel;
  final String? selectedNodeId;
  final bool isTransmitting;
  final List<double> waveform;
  final bool isLoading;
  final String? statusMessage;
  final String? lastDispatch;

  CyberdeckState copyWith({
    List<CyberdeckMeshNode>? nodes,
    CyberdeckHealth? health,
    int? channel,
    String? selectedNodeId,
    bool? isTransmitting,
    List<double>? waveform,
    bool? isLoading,
    String? statusMessage,
    String? lastDispatch,
  }) {
    return CyberdeckState(
      nodes: nodes ?? this.nodes,
      health: health ?? this.health,
      channel: channel ?? this.channel,
      selectedNodeId: selectedNodeId ?? this.selectedNodeId,
      isTransmitting: isTransmitting ?? this.isTransmitting,
      waveform: waveform ?? this.waveform,
      isLoading: isLoading ?? this.isLoading,
      statusMessage: statusMessage ?? this.statusMessage,
      lastDispatch: lastDispatch ?? this.lastDispatch,
    );
  }
}

class CyberdeckNotifier extends StateNotifier<CyberdeckState> {
  CyberdeckNotifier(this._repo) : super(const CyberdeckState());

  final CyberdeckRepository _repo;
  Timer? _waveTimer;
  final _rng = Random();

  Future<void> load() async {
    state = state.copyWith(isLoading: true, statusMessage: null);
    try {
      final results = await Future.wait([_repo.fetchMesh(), _repo.fetchHealth()]);
      final nodes = results[0] as List<CyberdeckMeshNode>;
      final health = results[1] as CyberdeckHealth;
      state = state.copyWith(
        nodes: nodes,
        health: health,
        isLoading: false,
        selectedNodeId: state.selectedNodeId ?? (nodes.isNotEmpty ? nodes.first.nodeId : null),
      );
    } catch (_) {
      state = state.copyWith(isLoading: false, statusMessage: 'Failed to load cyberdeck telemetry.');
    }
  }

  void setChannel(int channel) => state = state.copyWith(channel: channel);

  void selectNode(String? nodeId) => state = state.copyWith(selectedNodeId: nodeId);

  void startTransmit() {
    if (state.isTransmitting) return;
    state = state.copyWith(isTransmitting: true, statusMessage: 'TX • LoRa PTT voice frame…');
    _waveTimer?.cancel();
    _waveTimer = Timer.periodic(const Duration(milliseconds: 80), (_) {
      final bars = List<double>.generate(24, (_) => 0.15 + _rng.nextDouble() * 0.85);
      state = state.copyWith(waveform: bars);
    });
  }

  void stopTransmit() {
    _waveTimer?.cancel();
    state = state.copyWith(
      isTransmitting: false,
      waveform: List<double>.filled(24, 0.08),
      statusMessage: 'RX • Standby on CH ${state.channel}',
    );
  }

  Future<void> sendText(String message) async {
    if (message.trim().isEmpty) return;
    state = state.copyWith(isLoading: true);
    try {
      await _repo.sendText(
        message: message.trim(),
        channel: state.channel,
        targetNodeId: state.selectedNodeId,
      );
      state = state.copyWith(isLoading: false, lastDispatch: 'TEXT → ${message.trim()}');
    } catch (_) {
      state = state.copyWith(isLoading: false, statusMessage: 'Text dispatch failed.');
    }
  }

  Future<void> sendBeacon() async {
    state = state.copyWith(isLoading: true);
    try {
      await _repo.sendBeacon(channel: state.channel);
      state = state.copyWith(isLoading: false, lastDispatch: 'BEACON • EMERGENCY');
    } catch (_) {
      state = state.copyWith(isLoading: false, statusMessage: 'Beacon dispatch failed.');
    }
  }

  @override
  void dispose() {
    _waveTimer?.cancel();
    super.dispose();
  }
}

final cyberdeckProvider = StateNotifierProvider<CyberdeckNotifier, CyberdeckState>((ref) {
  return CyberdeckNotifier(ref.watch(cyberdeckRepositoryProvider));
});

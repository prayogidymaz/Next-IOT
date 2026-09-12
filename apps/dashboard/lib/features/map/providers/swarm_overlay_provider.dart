import 'package:flutter_riverpod/flutter_riverpod.dart';

class SwarmOverlayState {
  const SwarmOverlayState({this.enabled = false});

  final bool enabled;

  SwarmOverlayState copyWith({bool? enabled}) => SwarmOverlayState(enabled: enabled ?? this.enabled);
}

class SwarmOverlayNotifier extends StateNotifier<SwarmOverlayState> {
  SwarmOverlayNotifier() : super(const SwarmOverlayState());

  void toggle() => state = state.copyWith(enabled: !state.enabled);
}

final swarmOverlayProvider = StateNotifierProvider<SwarmOverlayNotifier, SwarmOverlayState>((ref) {
  return SwarmOverlayNotifier();
});

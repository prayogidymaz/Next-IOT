import 'package:flutter_riverpod/flutter_riverpod.dart';

class MavlinkHudState {
  const MavlinkHudState({this.enabled = true});

  final bool enabled;

  MavlinkHudState copyWith({bool? enabled}) => MavlinkHudState(enabled: enabled ?? this.enabled);
}

class MavlinkHudNotifier extends StateNotifier<MavlinkHudState> {
  MavlinkHudNotifier() : super(const MavlinkHudState());

  void toggle() => state = state.copyWith(enabled: !state.enabled);
}

final mavlinkHudProvider = StateNotifierProvider<MavlinkHudNotifier, MavlinkHudState>((ref) {
  return MavlinkHudNotifier();
});

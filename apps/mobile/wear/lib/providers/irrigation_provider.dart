import "package:flutter_riverpod/flutter_riverpod.dart";

import "../services/mesh_api.dart";
import "sensor_provider.dart";

final irrigationProvider =
    StateNotifierProvider<IrrigationController, IrrigationState>(
  (ref) => IrrigationController(ref.watch(meshApiProvider)),
);

class IrrigationState {
  const IrrigationState({
    required this.valveOpen,
    required this.countdownSeconds,
    required this.valveId,
  });

  final bool valveOpen;
  final int countdownSeconds;
  final String valveId;
}

class IrrigationController extends StateNotifier<IrrigationState> {
  IrrigationController(this._api)
      : super(
          const IrrigationState(
            valveOpen: false,
            countdownSeconds: 0,
            valveId: "valve-plot-a",
          ),
        );

  final MeshApi _api;

  Future<void> toggleValve() async {
    if (state.valveOpen) {
      await _api.postIrrigation(state.valveId, "close");
      state = IrrigationState(
        valveOpen: false,
        countdownSeconds: 0,
        valveId: state.valveId,
      );
      return;
    }
    await _api.postIrrigation(state.valveId, "open");
    state = IrrigationState(
      valveOpen: true,
      countdownSeconds: 300,
      valveId: state.valveId,
    );
  }

  void tick() {
    if (!state.valveOpen || state.countdownSeconds <= 0) return;
    state = IrrigationState(
      valveOpen: state.valveOpen,
      countdownSeconds: state.countdownSeconds - 1,
      valveId: state.valveId,
    );
  }
}

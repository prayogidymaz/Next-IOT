import "package:flutter_riverpod/flutter_riverpod.dart";

enum MeshConnectionState { disconnected, connecting, live }

/// Week 11-12 will attach SSE to /api/v1/mesh/events/stream.
final meshConnectionProvider =
    StateNotifierProvider<MeshConnectionNotifier, MeshConnectionState>(
  (ref) => MeshConnectionNotifier(),
);

class MeshConnectionNotifier extends StateNotifier<MeshConnectionState> {
  MeshConnectionNotifier() : super(MeshConnectionState.disconnected);

  void connectSkeleton() {
    state = MeshConnectionState.connecting;
    Future<void>.delayed(const Duration(milliseconds: 400), () {
      state = MeshConnectionState.live;
    });
  }
}

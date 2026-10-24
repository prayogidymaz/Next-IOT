import "package:flutter_riverpod/flutter_riverpod.dart";

import "mesh_connection.dart";
import "sensor_provider.dart";

final alertProvider = FutureProvider<List<WearAlert>>((ref) async {
  final api = ref.watch(meshApiProvider);
  try {
    final raw = await api.getAlerts();
    if (raw.isNotEmpty) {
      return raw
          .map(
            (a) => WearAlert(
              id: a["id"]?.toString() ?? "",
              title: a["title"]?.toString() ?? "Alert",
              severity: a["severity"]?.toString() ?? "info",
              acknowledged: a["status"]?.toString() == "acknowledged",
            ),
          )
          .toList();
    }
  } catch (_) {
    /* fall through to SSE buffer */
  }
  final live = ref.watch(liveMeshEventsProvider);
  final fromSse = live
      .where((e) => e["domain"] == "security" || e["domain"] == "ui")
      .map(
        (e) => WearAlert(
          id: e["event_id"]?.toString() ?? "",
          title: e["event_type"]?.toString() ?? "Mesh alert",
          severity: e["domain"] == "security" ? "critical" : "major",
          acknowledged: e["event_type"] == "user_acknowledged",
        ),
      )
      .toList();
  if (fromSse.isNotEmpty) {
    return fromSse;
  }
  return const [
    WearAlert(id: "a1", title: "Intrusion plot A", severity: "critical", acknowledged: false),
    WearAlert(id: "a2", title: "Tank low sprayer-2", severity: "major", acknowledged: false),
  ];
});

class WearAlert {
  const WearAlert({
    required this.id,
    required this.title,
    required this.severity,
    required this.acknowledged,
  });

  final String id;
  final String title;
  final String severity;
  final bool acknowledged;
}

final acknowledgedAlertsProvider =
    StateNotifierProvider<AcknowledgedAlerts, Set<String>>(
  (ref) => AcknowledgedAlerts(),
);

class AcknowledgedAlerts extends StateNotifier<Set<String>> {
  AcknowledgedAlerts() : super({});

  void acknowledge(String id) {
    state = {...state, id};
  }
}

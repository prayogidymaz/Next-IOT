import "package:flutter_riverpod/flutter_riverpod.dart";

import "sensor_provider.dart";

final alertProvider = FutureProvider<List<WearAlert>>((ref) async {
  final api = ref.watch(meshApiProvider);
  final raw = await api.getAlerts();
  return raw
      .map(
        (a) => WearAlert(
          id: a["id"]?.toString() ?? "",
          title: a["title"]?.toString() ?? "Alert",
          severity: a["severity"]?.toString() ?? "info",
          acknowledged: a["acknowledged"] == true,
        ),
      )
      .toList();
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

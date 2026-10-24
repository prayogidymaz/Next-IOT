import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";

import "../providers/alert_provider.dart";
import "../theme/tactical_warm_cream.dart";

class AlertCenterScreen extends ConsumerWidget {
  const AlertCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alerts = ref.watch(alertProvider);
    final acked = ref.watch(acknowledgedAlertsProvider);

    return Scaffold(
      backgroundColor: TacticalWarmCream.base,
      body: alerts.when(
        data: (items) => PageView.builder(
          itemCount: items.length,
          itemBuilder: (context, index) {
            final alert = items[index];
            final isAck = acked.contains(alert.id) || alert.acknowledged;
            final color = alert.severity == "critical"
                ? TacticalWarmCream.critical
                : TacticalWarmCream.clay;
            return Center(
              child: Dismissible(
                key: ValueKey(alert.id),
                direction: DismissDirection.horizontal,
                onDismissed: (_) =>
                    ref.read(acknowledgedAlertsProvider.notifier).acknowledge(alert.id),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          alert.title,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: color,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(isAck ? "Acknowledged" : "Swipe to acknowledge"),
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text("Alerts unavailable")),
      ),
    );
  }
}

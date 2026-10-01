import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/tactical_card.dart';
import '../providers/notification_channel_provider.dart';

class NotificationChannelsPanel extends ConsumerWidget {
  const NotificationChannelsPanel({super.key});

  IconData _iconFor(String id) => switch (id) {
        'telegram' => Icons.telegram,
        'whatsapp' => Icons.chat_outlined,
        _ => Icons.email_outlined,
      };

  Color _statusColor(ChannelConnectionStatus status) => switch (status) {
        ChannelConnectionStatus.connected => TacticalColors.success,
        ChannelConnectionStatus.testing => TacticalColors.cyan,
        ChannelConnectionStatus.disconnected => TacticalColors.critical,
        ChannelConnectionStatus.unknown => TacticalColors.textSecondary,
      };

  String _statusLabel(ChannelConnectionStatus status) => switch (status) {
        ChannelConnectionStatus.connected => 'Connected',
        ChannelConnectionStatus.testing => 'Testing…',
        ChannelConnectionStatus.disconnected => 'Disconnected',
        ChannelConnectionStatus.unknown => 'Not tested',
      };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(notificationChannelProvider);
    final notifier = ref.read(notificationChannelProvider.notifier);

    return TacticalCard(
      accentColor: TacticalColors.borderNeon,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(Icons.notifications_active_outlined,
                  color: TacticalColors.cyan.withOpacity(0.9), size: 20),
              const SizedBox(width: 8),
              Text('Notification Channels',
                  style: Theme.of(context).textTheme.titleMedium),
            ],
          ),
          const SizedBox(height: 14),
          ...state.channels.map((channel) {
            final testing = state.testingChannelId == channel.id;
            final statusColor = _statusColor(channel.status);
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                decoration: BoxDecoration(
                  color: TacticalColors.background.withOpacity(0.45),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: TacticalColors.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(_iconFor(channel.id),
                            color: TacticalColors.textPrimary, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(channel.label,
                              style: Theme.of(context)
                                  .textTheme
                                  .bodyMedium
                                  ?.copyWith(fontWeight: FontWeight.w600)),
                        ),
                        Switch.adaptive(
                          value: channel.enabled,
                          onChanged: testing
                              ? null
                              : (v) => notifier.setEnabled(channel.id, v),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: statusColor,
                            shape: BoxShape.circle,
                            boxShadow: channel.status ==
                                    ChannelConnectionStatus.connected
                                ? [
                                    BoxShadow(
                                      color: statusColor.withOpacity(0.55),
                                      blurRadius: 6,
                                    ),
                                  ]
                                : null,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _statusLabel(channel.status),
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall
                              ?.copyWith(color: statusColor),
                        ),
                        const Spacer(),
                        TextButton.icon(
                          onPressed: !channel.enabled || testing
                              ? null
                              : () => notifier.testChannel(channel.id),
                          icon: testing
                              ? const SizedBox(
                                  width: 14,
                                  height: 14,
                                  child:
                                      CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.send_outlined, size: 16),
                          label: const Text('Test'),
                        ),
                      ],
                    ),
                    if (channel.lastMessage != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        channel.lastMessage!,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: TacticalColors.textSecondary,
                              fontSize: 11,
                            ),
                      ),
                    ],
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}

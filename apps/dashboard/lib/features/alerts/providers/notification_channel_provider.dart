import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/notification_repository.dart';

enum ChannelConnectionStatus { connected, disconnected, testing, unknown }

class NotificationChannelConfig {
  const NotificationChannelConfig({
    required this.id,
    required this.label,
    required this.enabled,
    required this.status,
    this.lastMessage,
    this.testChannelKey,
  });

  final String id;
  final String label;
  final bool enabled;
  final ChannelConnectionStatus status;
  final String? lastMessage;
  final String? testChannelKey;

  NotificationChannelConfig copyWith({
    bool? enabled,
    ChannelConnectionStatus? status,
    String? lastMessage,
    bool clearMessage = false,
  }) {
    return NotificationChannelConfig(
      id: id,
      label: label,
      enabled: enabled ?? this.enabled,
      status: status ?? this.status,
      lastMessage: clearMessage ? null : (lastMessage ?? this.lastMessage),
      testChannelKey: testChannelKey,
    );
  }
}

class NotificationChannelsState {
  const NotificationChannelsState({
    this.channels = const [],
    this.testingChannelId,
  });

  final List<NotificationChannelConfig> channels;
  final String? testingChannelId;

  NotificationChannelsState copyWith({
    List<NotificationChannelConfig>? channels,
    String? testingChannelId,
    bool clearTesting = false,
  }) {
    return NotificationChannelsState(
      channels: channels ?? this.channels,
      testingChannelId:
          clearTesting ? null : (testingChannelId ?? this.testingChannelId),
    );
  }
}

class NotificationChannelsNotifier
    extends StateNotifier<NotificationChannelsState> {
  NotificationChannelsNotifier(this._repository)
      : super(const NotificationChannelsState()) {
    state = NotificationChannelsState(channels: _defaultChannels());
  }

  final NotificationRepository _repository;

  static List<NotificationChannelConfig> _defaultChannels() => const [
        NotificationChannelConfig(
          id: 'telegram',
          label: 'Telegram Bot',
          enabled: true,
          status: ChannelConnectionStatus.unknown,
          testChannelKey: 'telegram',
        ),
        NotificationChannelConfig(
          id: 'whatsapp',
          label: 'WhatsApp Webhook',
          enabled: true,
          status: ChannelConnectionStatus.unknown,
          testChannelKey: 'webhook',
        ),
        NotificationChannelConfig(
          id: 'email',
          label: 'Email Services',
          enabled: false,
          status: ChannelConnectionStatus.disconnected,
        ),
      ];

  void setEnabled(String channelId, bool enabled) {
    state = state.copyWith(
      channels: state.channels
          .map(
            (c) => c.id == channelId
                ? c.copyWith(
                    enabled: enabled,
                    status: enabled
                        ? ChannelConnectionStatus.unknown
                        : ChannelConnectionStatus.disconnected,
                    clearMessage: !enabled,
                  )
                : c,
          )
          .toList(),
    );
  }

  Future<void> testChannel(String channelId) async {
    final channel = state.channels.firstWhere((c) => c.id == channelId);
    if (channel.testChannelKey == null) {
      state = state.copyWith(
        channels: _updateChannel(
          channelId,
          (c) => c.copyWith(
            status: ChannelConnectionStatus.disconnected,
            lastMessage: 'Email dispatch is not configured on the backend yet.',
          ),
        ),
      );
      return;
    }

    state = state.copyWith(
      testingChannelId: channelId,
      channels: _updateChannel(
        channelId,
        (c) => c.copyWith(status: ChannelConnectionStatus.testing),
      ),
    );

    try {
      final result = await _repository.sendTest(
        channels: [channel.testChannelKey!],
      );
      final key = channel.testChannelKey!;
      final success = result.isSuccessFor(key);
      final error = result.errorFor(key);
      state = state.copyWith(
        clearTesting: true,
        channels: _updateChannel(
          channelId,
          (c) => c.copyWith(
            status: success
                ? ChannelConnectionStatus.connected
                : ChannelConnectionStatus.disconnected,
            lastMessage: success
                ? 'Test message delivered successfully.'
                : (error ?? 'Dispatch failed. Check backend configuration.'),
          ),
        ),
      );
    } catch (e) {
      state = state.copyWith(
        clearTesting: true,
        channels: _updateChannel(
          channelId,
          (c) => c.copyWith(
            status: ChannelConnectionStatus.disconnected,
            lastMessage: _mapError(e),
          ),
        ),
      );
    }
  }

  List<NotificationChannelConfig> _updateChannel(
    String channelId,
    NotificationChannelConfig Function(NotificationChannelConfig) transform,
  ) {
    return state.channels
        .map((c) => c.id == channelId ? transform(c) : c)
        .toList();
  }

  String _mapError(Object e) {
    if (e is DioException) {
      if (e.response?.statusCode == 403) {
        return 'Insufficient permissions (tenant_admin required).';
      }
      if (e.response?.statusCode == 401) {
        return 'Session expired. Please log in again.';
      }
    }
    return 'Failed to reach notification service.';
  }
}

final notificationChannelProvider = StateNotifierProvider<
    NotificationChannelsNotifier, NotificationChannelsState>((ref) {
  return NotificationChannelsNotifier(
    ref.watch(notificationRepositoryProvider),
  );
});

final notificationRepositoryProvider =
    Provider<NotificationRepository>((ref) => NotificationRepository());

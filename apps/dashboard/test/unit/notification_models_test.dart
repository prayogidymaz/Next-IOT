import 'package:flutter_test/flutter_test.dart';
import 'package:next_iot_dashboard/features/alerts/models/notification_models.dart';

void main() {
  test('NotificationTestResponse parses telegram success', () {
    final response = NotificationTestResponse.fromJson({
      'results': [
        {
          'provider': 'telegram',
          'success': true,
          'attempts': 1,
          'error': null,
        },
      ],
    });

    expect(response.telegramSuccess, isTrue);
    expect(response.telegramError, isNull);
  });

  test('NotificationTestResponse parses telegram failure', () {
    final response = NotificationTestResponse.fromJson({
      'results': [
        {
          'provider': 'telegram',
          'success': false,
          'attempts': 1,
          'error': 'Telegram notifier disabled or not configured',
        },
      ],
    });

    expect(response.telegramSuccess, isFalse);
    expect(response.telegramError, contains('not configured'));
  });
}

import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/notification_models.dart';

class NotificationRepository {
  NotificationRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<NotificationTestResponse> sendTest({
    String message = 'Next-IOT test notification from dashboard',
    List<String> channels = const ['telegram'],
  }) async {
    final response = await _api.post(
      '/api/v1/notifications/test',
      data: {
        'message': message,
        'channels': channels,
      },
    );
    return NotificationTestResponse.fromJson(response.data as Map<String, dynamic>);
  }
}

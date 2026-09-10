import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/mission_models.dart';

class CommandRepository {
  CommandRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<DeviceCommandResult> dispatchCommand({
    required String deviceId,
    required DeviceCommandType commandType,
    Map<String, dynamic> params = const {},
  }) async {
    final response = await _api.post(
      '/api/v1/devices/$deviceId/commands',
      data: {
        'command_type': commandType.apiValue,
        'params': params,
      },
    );
    return DeviceCommandResult.fromJson(response.data as Map<String, dynamic>);
  }
}

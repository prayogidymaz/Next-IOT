import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/rule_models.dart';

class RuleRepository {
  RuleRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<List<AlertRule>> fetchRules({String? deviceId}) async {
    final response = await _api.get(
      '/api/v1/rules',
      queryParameters: deviceId != null ? {'device_id': deviceId} : null,
    );
    final data = response.data as List<dynamic>;
    return data.map((e) => AlertRule.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<AlertRule> createRule(CreateRuleRequest request) async {
    final response = await _api.post('/api/v1/rules', data: request.toJson());
    return AlertRule.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deleteRule(String ruleId) async {
    await _api.delete('/api/v1/rules/$ruleId');
  }
}

import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/cyberdeck_models.dart';

class CyberdeckRepository {
  CyberdeckRepository({ApiClient? apiClient}) : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<List<CyberdeckMeshNode>> fetchMesh() async {
    final response = await _api.get('/api/v1/hardware/cyberdeck/mesh');
    final nodes = response.data['nodes'] as List<dynamic>;
    return nodes.map((e) => CyberdeckMeshNode.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<CyberdeckHealth> fetchHealth() async {
    final response = await _api.get('/api/v1/hardware/cyberdeck/health');
    return CyberdeckHealth.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> sendText({
    required String message,
    required int channel,
    String? targetNodeId,
    bool encrypt = true,
  }) async {
    await _api.post(
      '/api/v1/hardware/cyberdeck/ptt/text',
      data: {
        'message': message,
        'channel': channel,
        'target_node_id': targetNodeId,
        'encrypt': encrypt,
      },
    );
  }

  Future<void> sendBeacon({required int channel, String severity = 'critical'}) async {
    await _api.post(
      '/api/v1/hardware/cyberdeck/ptt/beacon',
      data: {'channel': channel, 'severity': severity},
    );
  }
}

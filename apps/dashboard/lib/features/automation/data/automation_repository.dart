import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../models/automation_pipeline_models.dart';

class AutomationRepository {
  AutomationRepository({ApiClient? apiClient})
      : _api = (apiClient ?? ApiClient()).dio;

  final Dio _api;

  Future<List<AutomationPipelineModel>> fetchPipelines() async {
    final response = await _api.get('/api/v1/automation/pipelines');
    final data = response.data as Map<String, dynamic>;
    final items = data['items'] as List<dynamic>? ?? [];
    return items
        .map((e) => AutomationPipelineModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<AutomationPipelineModel> getPipeline(String id) async {
    final response = await _api.get('/api/v1/automation/pipelines/$id');
    return AutomationPipelineModel.fromJson(
        response.data as Map<String, dynamic>);
  }

  Future<AutomationPipelineModel> createPipeline(
      AutomationPipelineModel pipeline) async {
    final response = await _api.post(
      '/api/v1/automation/pipelines',
      data: pipeline.toCreateJson(),
    );
    return AutomationPipelineModel.fromJson(
        response.data as Map<String, dynamic>);
  }

  Future<AutomationPipelineModel> updatePipeline(
    String id,
    AutomationPipelineModel pipeline,
  ) async {
    final response = await _api.put(
      '/api/v1/automation/pipelines/$id',
      data: pipeline.toCreateJson(),
    );
    return AutomationPipelineModel.fromJson(
        response.data as Map<String, dynamic>);
  }

  Future<void> deletePipeline(String id) async {
    await _api.delete('/api/v1/automation/pipelines/$id');
  }

  Future<Map<String, dynamic>> exportPipelineJson(String pipelineId) async {
    final response = await _api.get('/api/v1/rules/$pipelineId/export');
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> importPipelineJson(
      Map<String, dynamic> document) async {
    final response = await _api.post(
      '/api/v1/rules/import',
      data: {'document': document},
    );
    return response.data as Map<String, dynamic>;
  }

  Future<PipelineValidationResult> validatePipelineJson(
      Map<String, dynamic> document) async {
    final response = await _api.post(
      '/api/v1/rules/validate',
      data: {'document': document},
    );
    return PipelineValidationResult.fromJson(
        response.data as Map<String, dynamic>);
  }

  Future<PipelineTestRunResult> dryRunGraph({
    required String eventType,
    required List<Map<String, dynamic>> nodes,
    required List<Map<String, dynamic>> edges,
    Map<String, dynamic> context = const {},
    String pipelineName = 'Dry Run',
  }) async {
    final response = await _api.post(
      '/api/v1/automation/pipelines/dry-run',
      data: {
        'event_type': eventType,
        'context': context,
        'nodes': nodes,
        'edges': edges,
        'pipeline_name': pipelineName,
      },
    );
    return PipelineTestRunResult.fromJson(
        response.data as Map<String, dynamic>);
  }

  Future<PipelineTestRunResult> testRun({
    required String pipelineId,
    required String eventType,
    Map<String, dynamic> context = const {},
    List<Map<String, dynamic>>? nodes,
    List<Map<String, dynamic>>? edges,
  }) async {
    final response = await _api.post(
      '/api/v1/automation/pipelines/$pipelineId/test-run',
      data: {
        'event_type': eventType,
        'context': context,
        if (nodes != null) 'nodes': nodes,
        if (edges != null) 'edges': edges,
      },
    );
    return PipelineTestRunResult.fromJson(
        response.data as Map<String, dynamic>);
  }
}

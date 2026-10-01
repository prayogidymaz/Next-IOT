import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/automation_repository.dart';
import '../models/automation_pipeline_models.dart';
import 'automation_builder_provider.dart';

final automationPipelinesSummaryProvider =
    FutureProvider<List<AutomationPipelineModel>>((ref) async {
  final repo = ref.watch(automationRepositoryProvider);
  return repo.fetchPipelines();
});

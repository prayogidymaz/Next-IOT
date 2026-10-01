import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../auth/providers/permissions_provider.dart';
import '../../automation/screens/automation_builder_screen.dart';
import '../../automation/providers/automation_builder_provider.dart';
import '../widgets/pipeline_json_io_dialog.dart';

/// Enterprise Automation Studio entry (`/studio`).
class AutomationStudioScreen extends ConsumerWidget {
  const AutomationStudioScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return const AutomationBuilderScreen();
  }
}

/// Toolbar helpers shared by [AutomationBuilderScreen].
mixin AutomationStudioIoMixin<T extends ConsumerStatefulWidget>
    on ConsumerState<T> {
  Future<void> exportPipelineJson(BuildContext context) async {
    final doc = await ref.read(automationBuilderProvider.notifier).buildExportDocument();
    await copyPipelineJsonToClipboard(doc);
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pipeline JSON copied to clipboard')),
      );
    }
  }

  Future<void> importPipelineJson(BuildContext context) async {
    final canManage =
        ref.read(permissionsProvider).can(AppPermissions.automationManage);
    await PipelineJsonIoDialog.showImport(
      context,
      readOnlyPreview: !canManage,
      onImport: (document) async {
        if (canManage) {
          await ref.read(automationBuilderProvider.notifier).importDocument(document);
        } else {
          await ref.read(automationBuilderProvider.notifier).previewDocument(document);
        }
      },
    );
  }
}

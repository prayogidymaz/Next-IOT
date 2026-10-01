import 'package:flutter/material.dart';

import '../theme/tactical_theme.dart';

enum StudioDeployBadge { draft, deployed }

class StudioLayoutShell extends StatelessWidget {
  const StudioLayoutShell({
    super.key,
    required this.pipelineName,
    required this.onPipelineNameChanged,
    required this.deployBadge,
    required this.onBack,
    required this.onDryRun,
    required this.onSave,
    required this.body,
    this.isSaving = false,
    this.isTesting = false,
    this.statusMessage,
    this.onClearCanvas,
    this.onExportJson,
    this.onImportJson,
    this.canEditPipeline = true,
    this.canRunDryTest = true,
  });

  final String pipelineName;
  final ValueChanged<String> onPipelineNameChanged;
  final StudioDeployBadge deployBadge;
  final VoidCallback onBack;
  final Future<void> Function() onDryRun;
  final VoidCallback onSave;
  final VoidCallback? onClearCanvas;
  final VoidCallback? onExportJson;
  final VoidCallback? onImportJson;
  final bool canEditPipeline;
  final bool canRunDryTest;
  final Widget body;
  final bool isSaving;
  final bool isTesting;
  final String? statusMessage;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: TacticalColors.background,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _StudioHeader(
            pipelineName: pipelineName,
            onPipelineNameChanged: onPipelineNameChanged,
            deployBadge: deployBadge,
            onBack: onBack,
            onDryRun: onDryRun,
            onSave: onSave,
            onClearCanvas: onClearCanvas,
            onExportJson: onExportJson,
            onImportJson: onImportJson,
            canEditPipeline: canEditPipeline,
            canRunDryTest: canRunDryTest,
            isSaving: isSaving,
            isTesting: isTesting,
            statusMessage: statusMessage,
          ),
          Expanded(child: body),
        ],
      ),
    );
  }
}

class _StudioHeader extends StatefulWidget {
  const _StudioHeader({
    required this.pipelineName,
    required this.onPipelineNameChanged,
    required this.deployBadge,
    required this.onBack,
    required this.onDryRun,
    required this.onSave,
    this.onClearCanvas,
    this.onExportJson,
    this.onImportJson,
    required this.canEditPipeline,
    required this.canRunDryTest,
    required this.isSaving,
    required this.isTesting,
    this.statusMessage,
  });

  final String pipelineName;
  final ValueChanged<String> onPipelineNameChanged;
  final StudioDeployBadge deployBadge;
  final VoidCallback onBack;
  final Future<void> Function() onDryRun;
  final VoidCallback onSave;
  final VoidCallback? onClearCanvas;
  final VoidCallback? onExportJson;
  final VoidCallback? onImportJson;
  final bool canEditPipeline;
  final bool canRunDryTest;
  final bool isSaving;
  final bool isTesting;
  final String? statusMessage;

  @override
  State<_StudioHeader> createState() => _StudioHeaderState();
}

class _StudioHeaderState extends State<_StudioHeader> {
  late final TextEditingController _titleController;

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController(text: widget.pipelineName);
  }

  @override
  void didUpdateWidget(covariant _StudioHeader oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.pipelineName != widget.pipelineName &&
        _titleController.text != widget.pipelineName) {
      _titleController.text = widget.pipelineName;
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final badge = widget.deployBadge == StudioDeployBadge.deployed
        ? _StatusBadge(
            label: 'Deployed',
            color: TacticalColors.success,
          )
        : _StatusBadge(
            label: 'Draft',
            color: TacticalColors.warning,
          );

    return Material(
      color: TacticalColors.surface,
      child: DecoratedBox(
        decoration: const BoxDecoration(
          border: Border(bottom: BorderSide(color: TacticalColors.border)),
        ),
        child: SafeArea(
          bottom: false,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    IconButton(
                      key: const Key('studio-back-button'),
                      tooltip: 'Back to Dashboard',
                      icon: const Icon(Icons.arrow_back),
                      onPressed: widget.onBack,
                    ),
                    Text(
                      'Automation Studio',
                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                            color: TacticalColors.textSecondary,
                            letterSpacing: 0.4,
                          ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        key: const Key('studio-pipeline-title'),
                        controller: _titleController,
                        readOnly: !widget.canEditPipeline,
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                        decoration: const InputDecoration(
                          isDense: true,
                          border: InputBorder.none,
                          hintText: 'Untitled Pipeline',
                        ),
                        onSubmitted: widget.canEditPipeline
                            ? widget.onPipelineNameChanged
                            : null,
                        onEditingComplete: widget.canEditPipeline
                            ? () => widget.onPipelineNameChanged(
                                  _titleController.text,
                                )
                            : null,
                      ),
                    ),
                    const SizedBox(width: 8),
                    badge,
                  ],
                ),
                const SizedBox(height: 4),
                Wrap(
                  spacing: 8,
                  runSpacing: 6,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    if (widget.statusMessage != null)
                      SizedBox(
                        width: 320,
                        child: Text(
                          widget.statusMessage!,
                          style: Theme.of(context).textTheme.bodySmall,
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                      ),
                    if (widget.onExportJson != null)
                      TextButton.icon(
                        key: const Key('studio-export-json'),
                        onPressed: widget.isSaving ? null : widget.onExportJson,
                        icon: const Icon(Icons.download_outlined, size: 18),
                        label: const Text('Export Pipeline JSON'),
                      ),
                    if (widget.onImportJson != null)
                      TextButton.icon(
                        key: const Key('studio-import-json'),
                        onPressed: widget.isSaving ? null : widget.onImportJson,
                        icon: const Icon(Icons.upload_outlined, size: 18),
                        label: const Text('Import Pipeline JSON'),
                      ),
                    if (widget.onClearCanvas != null && widget.canEditPipeline)
                      TextButton.icon(
                        onPressed:
                            widget.isSaving ? null : widget.onClearCanvas,
                        icon: const Icon(Icons.delete_sweep_outlined, size: 18),
                        label: const Text('Clear Canvas'),
                      ),
                    FilledButton.icon(
                      onPressed: !widget.canRunDryTest ||
                              widget.isTesting ||
                              widget.isSaving
                          ? null
                          : () => widget.onDryRun(),
                      icon: widget.isTesting
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.play_arrow_outlined, size: 18),
                      label: const Text('Dry-Run Test'),
                    ),
                    const SizedBox(width: 8),
                    FilledButton.icon(
                      onPressed: !widget.canEditPipeline || widget.isSaving
                          ? null
                          : widget.onSave,
                      icon: widget.isSaving
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.cloud_upload_outlined, size: 18),
                      label: const Text('Save & Deploy Pipeline'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withOpacity(0.65)),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.4,
            ),
      ),
    );
  }
}

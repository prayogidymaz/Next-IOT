import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/permission_guard.dart';
import '../../../core/widgets/studio_layout_shell.dart';
import '../../../routing/navigation_config.dart';
import '../../auth/providers/permissions_provider.dart';
import '../../studio/screens/automation_studio_screen.dart';
import '../providers/automation_builder_provider.dart';
import '../providers/palette_placement_provider.dart';
import '../widgets/dry_run_log_panel.dart';
import '../widgets/node_palette.dart';
import '../widgets/pipeline_canvas.dart';
import '../widgets/pipeline_node_widget.dart';
import '../widgets/pipeline_selection_inspector.dart';

class CancelPlacementIntent extends Intent {
  const CancelPlacementIntent();
}

class DeleteSelectionIntent extends Intent {
  const DeleteSelectionIntent();
}

class AutomationBuilderScreen extends ConsumerStatefulWidget {
  const AutomationBuilderScreen({super.key});

  @override
  ConsumerState<AutomationBuilderScreen> createState() =>
      _AutomationBuilderScreenState();
}

class _AutomationBuilderScreenState extends ConsumerState<AutomationBuilderScreen>
    with AutomationStudioIoMixin {
  static const _sidebarWidth = 340.0;

  final _workspaceKey = GlobalKey();
  final _focusNode = FocusNode();
  bool _dryRunSidebarOpen = false;
  bool _dryRunSidebarMounted = false;

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  Offset _globalToWorkspaceLocal(Offset global) {
    final box = _workspaceKey.currentContext?.findRenderObject() as RenderBox?;
    if (box == null) return global;
    return box.globalToLocal(global);
  }

  void _openDryRunSidebar() {
    setState(() {
      _dryRunSidebarMounted = true;
      _dryRunSidebarOpen = true;
    });
  }

  void _closeDryRunSidebar() {
    setState(() => _dryRunSidebarOpen = false);
    Future<void>.delayed(const Duration(milliseconds: 280), () {
      if (!mounted || _dryRunSidebarOpen) return;
      setState(() => _dryRunSidebarMounted = false);
    });
  }

  Future<void> _runDryRunTest() async {
    _openDryRunSidebar();
    await ref.read(automationBuilderProvider.notifier).dryRunTest();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(automationBuilderProvider);
    final placement = ref.watch(palettePlacementProvider);
    final notifier = ref.read(automationBuilderProvider.notifier);
    final placementNotifier = ref.read(palettePlacementProvider.notifier);

    final deployBadge = state.pipelineId != null
        ? StudioDeployBadge.deployed
        : StudioDeployBadge.draft;
    final canManage =
        ref.watch(permissionsProvider.select((s) => s.can(AppPermissions.automationManage)));
    final canRun =
        ref.watch(permissionsProvider.select((s) => s.can(AppPermissions.automationRun)));

    return StudioLayoutShell(
      pipelineName: state.pipelineName,
      onPipelineNameChanged: notifier.updatePipelineName,
      deployBadge: deployBadge,
      isSaving: state.isSaving,
      isTesting: state.isTesting,
      statusMessage: state.statusMessage,
      onBack: () => context.go(AppRoutes.dashboard),
      onDryRun: _runDryRunTest,
      onSave: notifier.saveAndDeploy,
      onClearCanvas: notifier.clearCanvas,
      onExportJson: () => exportPipelineJson(context),
      onImportJson: () => importPipelineJson(context),
      canEditPipeline: canManage,
      canRunDryTest: canRun,
      body: Shortcuts(
        shortcuts: const {
          SingleActivator(LogicalKeyboardKey.escape): CancelPlacementIntent(),
          SingleActivator(LogicalKeyboardKey.delete): DeleteSelectionIntent(),
          SingleActivator(LogicalKeyboardKey.backspace): DeleteSelectionIntent(),
        },
        child: Actions(
          actions: {
            CancelPlacementIntent: CallbackAction<CancelPlacementIntent>(
              onInvoke: (_) {
                if (ref.read(automationBuilderProvider).isWiringActive) {
                  ref
                      .read(automationBuilderProvider.notifier)
                      .resetConnectingState();
                  return null;
                }
                if (_dryRunSidebarMounted) {
                  _closeDryRunSidebar();
                } else {
                  placementNotifier.cancelPlacement();
                }
                return null;
              },
            ),
            DeleteSelectionIntent: CallbackAction<DeleteSelectionIntent>(
              onInvoke: (_) {
                ref.read(automationBuilderProvider.notifier).deleteSelection();
                return null;
              },
            ),
          },
          child: Focus(
            autofocus: true,
            focusNode: _focusNode,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (placement.isActive)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    color: TacticalColors.cyan.withOpacity(0.1),
                    child: Text(
                      'Placement mode: ${placement.label} — click canvas to place, Esc or right-click to cancel',
                      style: Theme.of(context)
                          .textTheme
                          .bodySmall
                          ?.copyWith(color: TacticalColors.cyan),
                    ),
                  ),
                if (state.isWiringActive)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    color: TacticalColors.warning.withOpacity(0.12),
                    child: Text(
                      'Wiring: drag to target port or click destination port — Esc or click empty canvas to cancel',
                      style: Theme.of(context)
                          .textTheme
                          .bodySmall
                          ?.copyWith(color: TacticalColors.warning),
                    ),
                  ),
                if (state.error != null)
                  MaterialBanner(
                    content: Text(state.error!),
                    backgroundColor: TacticalColors.critical.withOpacity(0.15),
                    actions: [
                      TextButton(
                        onPressed: notifier.dismissError,
                        child: const Text('Dismiss'),
                      ),
                    ],
                  ),
                Expanded(
                  child: MouseRegion(
                    onHover: (event) =>
                        placementNotifier.updateCursor(event.position),
                    child: Stack(
                      key: _workspaceKey,
                      clipBehavior: Clip.none,
                      children: [
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            PermissionGuard(
                              permission: AppPermissions.automationManage,
                              fallback: Container(
                                width: 240,
                                padding: const EdgeInsets.all(16),
                                decoration: const BoxDecoration(
                                  color: TacticalColors.surface,
                                  border: Border(
                                    right: BorderSide(color: TacticalColors.border),
                                  ),
                                ),
                                child: Text(
                                  'Read-only: node palette requires Admin role.',
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                              ),
                              child: const NodePalette(),
                            ),
                            Expanded(
                              child: Stack(
                                clipBehavior: Clip.none,
                                children: [
                                  const PipelineCanvas(),
                                  Positioned(
                                    left: 12,
                                    right: 12,
                                    bottom: 12,
                                    child: PipelineSelectionInspector(),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        if (placement.isActive &&
                            placement.cursorGlobal != null)
                          Positioned(
                            left:
                                _globalToWorkspaceLocal(placement.cursorGlobal!)
                                        .dx -
                                    kPipelineNodeWidth / 2,
                            top:
                                _globalToWorkspaceLocal(placement.cursorGlobal!)
                                        .dy -
                                    kPipelineNodeHeight / 2,
                            child: IgnorePointer(
                              child: _PlacementGhost(
                                label: placement.label ?? 'Node',
                                overCanvas: placement.isOverCanvas,
                              ),
                            ),
                          ),
                        if (_dryRunSidebarMounted)
                          AnimatedPositioned(
                            duration: const Duration(milliseconds: 280),
                            curve: Curves.easeOutCubic,
                            top: 0,
                            bottom: 0,
                            right: _dryRunSidebarOpen ? 0 : -_sidebarWidth,
                            width: _sidebarWidth,
                            child: DryRunLogPanel(
                              sidebar: true,
                              result: state.testRunResult,
                              isTesting: state.isTesting,
                              onClose: _closeDryRunSidebar,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PlacementGhost extends StatelessWidget {
  const _PlacementGhost({required this.label, required this.overCanvas});

  final String label;
  final bool overCanvas;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      elevation: 8,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        width: kPipelineNodeWidth,
        height: kPipelineNodeHeight,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: TacticalColors.surfaceElevated.withOpacity(0.92),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: overCanvas ? TacticalColors.cyan : TacticalColors.warning,
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: (overCanvas ? TacticalColors.cyan : TacticalColors.warning)
                  .withOpacity(0.25),
              blurRadius: 14,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              label,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: TacticalColors.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              overCanvas ? 'Click to place' : 'Move over canvas',
              style:
                  Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }
}

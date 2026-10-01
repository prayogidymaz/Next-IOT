import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/permission_guard.dart';
import '../../../routing/navigation_config.dart';
import '../../../core/widgets/tactical_card.dart';
import '../../alerts/providers/alert_provider.dart';
import '../../dashboard/widgets/asymmetric_bento_dashboard_layout.dart';
import '../models/device_models.dart';
import '../providers/device_provider.dart';
import '../widgets/info_help_icon.dart';
import '../widgets/register_device_dialog.dart';

class DeviceListScreen extends ConsumerStatefulWidget {
  const DeviceListScreen({super.key, this.topBanner});

  /// Legacy hook — workflows are embedded in the bento grid.
  final Widget? topBanner;

  @override
  ConsumerState<DeviceListScreen> createState() => _DeviceListScreenState();
}

class _DeviceListScreenState extends ConsumerState<DeviceListScreen> {
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(deviceProvider.notifier).loadDevices();
      ref.read(alertProvider.notifier).loadSummary();
    });
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      ref.read(deviceProvider.notifier).loadDevices();
      ref.read(alertProvider.notifier).loadSummary();
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(deviceProvider);
    final devices = state.filteredDevices;
    final notifier = ref.read(deviceProvider.notifier);

    Widget buildBody(BoxConstraints constraints) {
      if (state.isLoading && state.devices.isEmpty) {
        return const Center(child: CircularProgressIndicator());
      }

      if (state.error != null && state.devices.isEmpty) {
        return Center(
          child: TacticalCard(
            accentColor: TacticalColors.critical,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(state.error!, textAlign: TextAlign.center),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () =>
                      ref.read(deviceProvider.notifier).loadDevices(),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        );
      }

      return AsymmetricBentoDashboardLayout(
        allDevices: state.devices,
        filteredDevices: devices,
        statusFilter: state.statusFilter,
        categoryFilter: state.categoryFilter,
        onStatusSelected: notifier.setStatusFilter,
        onCategorySelected: notifier.setCategoryFilter,
        header: _buildHeader(context, state, constraints.maxWidth),
        width: constraints.maxWidth,
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final wide = constraints.maxWidth >= 960;
        final boundedHeight = constraints.maxHeight.isFinite &&
            constraints.maxHeight > 0;

        return RefreshIndicator(
          onRefresh: () async {
            await ref.read(deviceProvider.notifier).loadDevices();
            await ref.read(alertProvider.notifier).loadSummary();
          },
          child: CustomScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            slivers: [
              if (wide && boundedHeight)
                SliverFillRemaining(
                  hasScrollBody: false,
                  child: buildBody(constraints),
                )
              else
                SliverToBoxAdapter(child: buildBody(constraints)),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeader(
    BuildContext context,
    DeviceListState state,
    double width,
  ) {
    final titleRow = Row(
      children: [
        Flexible(
          child: Text('Devices', style: Theme.of(context).textTheme.titleLarge),
        ),
        const SizedBox(width: 6),
        InfoHelpIcon(
          title: 'Device Management',
          message: 'Kelola semua perangkat IoT tenant — drone, '
              'sensor lapangan, gateway LoRa, robot, dan node industri.',
        ),
      ],
    );
    final registerButton = PermissionGuard(
      permission: AppPermissions.devicesRegister,
      child: FilledButton.icon(
        onPressed: state.isLoading
            ? null
            : () => showRegisterDeviceDialog(context, ref),
        icon: const Icon(Icons.add_link),
        label: const Text('Register New Device'),
      ),
    );
    final otaButton = PermissionGuard(
      permission: AppPermissions.otaUpload,
      child: OutlinedButton.icon(
        onPressed: () => context.push(AppRoutes.devicesOta),
        icon: const Icon(Icons.system_update_alt, size: 18),
        label: const Text('OTA Manager'),
      ),
    );

    if (width < 560) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          titleRow,
          const SizedBox(height: 12),
          registerButton,
        ],
      );
    }
        return Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Expanded(child: titleRow),
            otaButton,
            const SizedBox(width: 8),
            registerButton,
          ],
        );
  }
}

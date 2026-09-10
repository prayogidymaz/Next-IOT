import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/pill_tab_bar.dart';
import '../../../core/widgets/tactical_card.dart';
import '../models/device_models.dart';
import '../providers/device_provider.dart';
import '../widgets/device_status_badge.dart';
import '../widgets/register_device_dialog.dart';

class DeviceListScreen extends ConsumerStatefulWidget {
  const DeviceListScreen({super.key});

  @override
  ConsumerState<DeviceListScreen> createState() => _DeviceListScreenState();
}

class _DeviceListScreenState extends ConsumerState<DeviceListScreen> {
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(deviceProvider.notifier).loadDevices());
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      ref.read(deviceProvider.notifier).loadDevices();
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

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Text('DEVICES', style: Theme.of(context).textTheme.titleLarge),
            const Spacer(),
            FilledButton.icon(
              onPressed: state.isLoading ? null : () => showRegisterDeviceDialog(context, ref),
              icon: const Icon(Icons.add_link),
              label: const Text('Register New Device'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        PillTabBar<DeviceStatusFilter>(
          tabs: DeviceStatusFilter.values
              .map((f) => PillTab(value: f, label: f.label))
              .toList(),
          selected: state.statusFilter,
          onSelected: ref.read(deviceProvider.notifier).setStatusFilter,
        ),
        const SizedBox(height: 16),
        Expanded(child: _buildBody(state, devices)),
      ],
    );
  }

  Widget _buildBody(DeviceListState state, List<Device> devices) {
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
                onPressed: () => ref.read(deviceProvider.notifier).loadDevices(),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (devices.isEmpty) {
      return Center(
        child: Text(
          state.statusFilter == DeviceStatusFilter.all
              ? 'No devices yet. Register your first device.'
              : 'No ${state.statusFilter.label.toLowerCase()} devices.',
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(deviceProvider.notifier).loadDevices(),
      child: ListView.separated(
        physics: const AlwaysScrollableScrollPhysics(),
        itemCount: devices.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (context, index) => _DeviceTile(device: devices[index]),
      ),
    );
  }
}

class _DeviceTile extends StatelessWidget {
  const _DeviceTile({required this.device});

  final Device device;

  IconData get _typeIcon {
    switch (DeviceType.fromApiValue(device.deviceType)) {
      case DeviceType.drone:
        return Icons.flight;
      case DeviceType.robot:
        return Icons.smart_toy;
      case DeviceType.lorawan:
        return Icons.cell_tower;
      case DeviceType.cyberdeck:
        return Icons.terminal;
      case DeviceType.sensor:
      case null:
        return Icons.sensors;
    }
  }

  Color get _accentColor {
    switch (device.connectionStatus) {
      case DeviceConnectionStatus.online:
        return TacticalColors.success;
      case DeviceConnectionStatus.offline:
        return TacticalColors.critical;
      case DeviceConnectionStatus.pending:
        return TacticalColors.warning;
    }
  }

  @override
  Widget build(BuildContext context) {
    return TacticalCard(
      accentColor: _accentColor,
      onTap: () => context.push('/devices/${device.id}', extra: device),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: TacticalColors.background,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: TacticalColors.border),
            ),
            child: Icon(_typeIcon, color: TacticalColors.borderNeon),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  device.name,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  '${device.deviceTypeLabel} · Last seen: ${formatLastSeen(device.lastSeenAt)}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          DeviceStatusBadge(status: device.connectionStatus),
          const SizedBox(width: 8),
          Icon(Icons.chevron_right, color: TacticalColors.textSecondary.withOpacity(0.6)),
        ],
      ),
    );
  }
}

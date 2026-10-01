import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../automation/widgets/active_workflows_summary.dart';
import '../../devices/models/device_models.dart';
import '../../devices/widgets/device_category_filter_bar.dart';
import 'compact_device_table.dart';
import 'compact_smart_home_control_card.dart';
import 'dashboard_sidebar_panel.dart';
import 'device_summary_metrics_bento.dart';

/// 70% main bento grid + 30% sidebar (stacks on narrow widths).
class AsymmetricBentoDashboardLayout extends ConsumerWidget {
  const AsymmetricBentoDashboardLayout({
    super.key,
    required this.allDevices,
    required this.filteredDevices,
    required this.statusFilter,
    required this.categoryFilter,
    required this.onStatusSelected,
    required this.onCategorySelected,
    required this.header,
    required this.width,
  });

  final List<Device> allDevices;
  final List<Device> filteredDevices;
  final DeviceStatusFilter statusFilter;
  final DeviceCategoryFilter categoryFilter;
  final ValueChanged<DeviceStatusFilter> onStatusSelected;
  final ValueChanged<DeviceCategoryFilter> onCategorySelected;
  final Widget header;
  final double width;

  static const layoutKey = Key('asymmetric-bento-dashboard');

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wide = width >= 960;
    final mainWidth = wide ? width * 0.7 - 14 : width;

    final main = _MainBentoColumn(
      allDevices: allDevices,
      filteredDevices: filteredDevices,
      statusFilter: statusFilter,
      categoryFilter: categoryFilter,
      onStatusSelected: onStatusSelected,
      onCategorySelected: onCategorySelected,
      fillHeight: wide,
      maxWidth: mainWidth,
    );
    const sidebar = DashboardSidebarPanel();

    if (!wide) {
      return Column(
        key: layoutKey,
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          header,
          const SizedBox(height: 12),
          main,
          const SizedBox(height: 12),
          const SizedBox(height: 480, child: sidebar),
        ],
      );
    }

    return Column(
      key: layoutKey,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        header,
        const SizedBox(height: 12),
        Expanded(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(flex: 7, child: main),
              const SizedBox(width: 14),
              const Expanded(flex: 3, child: sidebar),
            ],
          ),
        ),
      ],
    );
  }
}

class _MainBentoColumn extends StatelessWidget {
  const _MainBentoColumn({
    required this.allDevices,
    required this.filteredDevices,
    required this.statusFilter,
    required this.categoryFilter,
    required this.onStatusSelected,
    required this.onCategorySelected,
    required this.fillHeight,
    required this.maxWidth,
  });

  final List<Device> allDevices;
  final List<Device> filteredDevices;
  final DeviceStatusFilter statusFilter;
  final DeviceCategoryFilter categoryFilter;
  final ValueChanged<DeviceStatusFilter> onStatusSelected;
  final ValueChanged<DeviceCategoryFilter> onCategorySelected;
  final bool fillHeight;
  final double maxWidth;

  @override
  Widget build(BuildContext context) {
    final Widget topRow;
    if (maxWidth < 640) {
      topRow = Column(
        children: [
          const CompactActiveWorkflowsBento(),
          const SizedBox(height: 10),
          DeviceSummaryMetricsBento(devices: allDevices),
        ],
      );
    } else {
      topRow = Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Expanded(
            flex: 3,
            child: CompactActiveWorkflowsBento(),
          ),
          const SizedBox(width: 10),
          Expanded(
            flex: 2,
            child: DeviceSummaryMetricsBento(devices: allDevices),
          ),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        topRow,
        const SizedBox(height: 10),
        CompactSmartHomeControlCard(devices: allDevices),
        const SizedBox(height: 12),
        DeviceStatusFilterBar(
          selected: statusFilter,
          onSelected: onStatusSelected,
        ),
        const SizedBox(height: 10),
        DeviceCategoryFilterBar(
          selected: categoryFilter,
          onSelected: onCategorySelected,
        ),
        const SizedBox(height: 12),
        if (fillHeight)
          Expanded(child: CompactDeviceTable(devices: filteredDevices))
        else
          CompactDeviceTable(devices: filteredDevices, maxHeight: 240),
      ],
    );
  }
}

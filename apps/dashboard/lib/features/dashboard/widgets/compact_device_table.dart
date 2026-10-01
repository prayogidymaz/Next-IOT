import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../devices/models/device_models.dart';
import '../../devices/widgets/device_status_badge.dart';
import 'bento_compact_surface.dart';

class CompactDeviceTable extends StatelessWidget {
  const CompactDeviceTable({
    super.key,
    required this.devices,
    this.maxHeight = 280,
    this.pageSize = 8,
  });

  final List<Device> devices;
  final double maxHeight;
  final int pageSize;

  static const tableKey = Key('compact-device-table');

  @override
  Widget build(BuildContext context) {
    final visible = devices.take(pageSize).toList();

    return BentoCompactSurface(
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Text('Devices', style: Theme.of(context).textTheme.titleSmall),
              const Spacer(),
              Text(
                '${devices.length} total',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: maxHeight,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: devices.isEmpty
                  ? Center(
                      child: Text(
                        'No devices match filters.',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    )
                  : SingleChildScrollView(
                      key: tableKey,
                      child: DataTable(
                        headingRowHeight: 36,
                        dataRowMinHeight: 40,
                        dataRowMaxHeight: 44,
                        horizontalMargin: 8,
                        columnSpacing: 16,
                        headingTextStyle:
                            Theme.of(context).textTheme.labelSmall?.copyWith(
                                  fontWeight: FontWeight.w700,
                                  color: TacticalColors.textSecondary,
                                ),
                        columns: const [
                          DataColumn(label: Text('Name')),
                          DataColumn(label: Text('Type')),
                          DataColumn(label: Text('Status')),
                          DataColumn(label: Text('Last seen')),
                        ],
                        rows: visible.map((device) {
                          return DataRow(
                            onSelectChanged: (_) => context.push(
                              '/devices/${device.id}',
                              extra: device,
                            ),
                            cells: [
                              DataCell(Text(
                                device.name,
                                overflow: TextOverflow.ellipsis,
                              )),
                              DataCell(Text(device.deviceTypeLabel)),
                              DataCell(DeviceStatusBadge(
                                  status: device.connectionStatus)),
                              DataCell(Text(
                                formatLastSeen(device.lastSeenAt),
                                style: Theme.of(context).textTheme.bodySmall,
                              )),
                            ],
                          );
                        }).toList(),
                      ),
                    ),
            ),
          ),
          if (devices.length > pageSize)
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Text(
                'Showing $pageSize of ${devices.length} — scroll table for more',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';

import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/pill_tab_bar.dart';
import '../models/device_models.dart';
import 'info_help_icon.dart';

class DeviceCategoryFilterBar extends StatelessWidget {
  const DeviceCategoryFilterBar({
    super.key,
    required this.selected,
    required this.onSelected,
  });

  final DeviceCategoryFilter selected;
  final ValueChanged<DeviceCategoryFilter> onSelected;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Text(
              'CATEGORY',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    letterSpacing: 0.6,
                  ),
            ),
            const SizedBox(width: 6),
            InfoHelpIcon(
              title: 'Filter Kategori Perangkat',
              message: 'Kelompokkan perangkat berdasarkan domain operasional — '
                  'drone, pertanian/tambak, sensor LoRa lapangan, industri, '
                  'atau armada aset bergerak.',
            ),
          ],
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: DeviceCategoryFilter.values.map((category) {
            final isSelected = category == selected;
            return Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () => onSelected(category),
                borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  padding:
                      const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? TacticalColors.success.withOpacity( 0.12)
                        : TacticalColors.surfaceElevated,
                    borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
                    border: Border.all(
                      color: isSelected
                          ? TacticalColors.success.withOpacity( 0.5)
                          : TacticalColors.border,
                      width: isSelected ? 2 : 1,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (category.chipIcon != null) ...[
                        Icon(
                          category.chipIcon,
                          size: 16,
                          color: isSelected
                              ? TacticalColors.success
                              : TacticalColors.textSecondary,
                        ),
                        const SizedBox(width: 6),
                      ],
                      Flexible(
                        child: Text(
                          category.chipIcon != null
                              ? category.label
                              : category.chipLabel,
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                          style: TextStyle(
                            color: isSelected
                                ? TacticalColors.success
                                : TacticalColors.textSecondary,
                            fontWeight:
                                isSelected ? FontWeight.w700 : FontWeight.w500,
                            fontSize: 13,
                          ),
                        ),
                      ),
                      if (category != DeviceCategoryFilter.all) ...[
                        const SizedBox(width: 4),
                        InfoHelpIcon(
                          size: 14,
                          title: category.label,
                          message: category.helpText,
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

/// Status filter row with optional RSSI/telemetry glossary hint.
class DeviceStatusFilterBar extends StatelessWidget {
  const DeviceStatusFilterBar({
    super.key,
    required this.selected,
    required this.onSelected,
  });

  static const filterBarKey = Key('device-status-filter-bar');

  final DeviceStatusFilter selected;
  final ValueChanged<DeviceStatusFilter> onSelected;

  @override
  Widget build(BuildContext context) {
    return Column(
      key: filterBarKey,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Text(
              'STATUS',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    letterSpacing: 0.6,
                  ),
            ),
            const SizedBox(width: 6),
            InfoHelpIcon(
              title: 'Status Koneksi',
              message:
                  'Online = perangkat aktif mengirim data. Offline = tidak '
                  'terdengar. Pending = terdaftar tapi belum selesai provisioning.',
            ),
          ],
        ),
        const SizedBox(height: 10),
        PillTabBar<DeviceStatusFilter>(
          tabs: DeviceStatusFilter.values
              .map((f) => PillTab(value: f, label: f.label))
              .toList(),
          selected: selected,
          onSelected: onSelected,
        ),
      ],
    );
  }
}

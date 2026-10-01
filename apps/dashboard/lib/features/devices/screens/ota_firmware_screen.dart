import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/rbac/app_permissions.dart';
import '../../../core/theme/tactical_theme.dart';
import '../../../core/widgets/permission_guard.dart';
import '../../../core/widgets/tactical_card.dart';
import '../models/device_models.dart';
import '../providers/ota_firmware_provider.dart';

class OtaFirmwareScreen extends ConsumerStatefulWidget {
  const OtaFirmwareScreen({super.key});

  @override
  ConsumerState<OtaFirmwareScreen> createState() => _OtaFirmwareScreenState();
}

class _OtaFirmwareScreenState extends ConsumerState<OtaFirmwareScreen> {
  final _versionController = TextEditingController(text: '1.0.0');
  DeviceCategoryFilter _category = DeviceCategoryFilter.smartHomeBuilding;
  List<int>? _firmwareBytes;
  String? _firmwareName;

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(otaFirmwareProvider.notifier).load());
  }

  @override
  void dispose() {
    _versionController.dispose();
    super.dispose();
  }

  Future<void> _pickFirmware() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['bin', 'elf'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;
    final file = result.files.first;
    if (file.bytes == null) return;
    setState(() {
      _firmwareBytes = file.bytes;
      _firmwareName = file.name;
    });
  }

  Future<void> _upload() async {
    final bytes = _firmwareBytes;
    if (bytes == null || _firmwareName == null) return;
    await ref.read(otaFirmwareProvider.notifier).uploadAndPublish(
          version: _versionController.text.trim(),
          targetCategory: _otaCategoryApi(_category),
          filename: _firmwareName!,
          bytes: bytes,
        );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(otaFirmwareProvider);
    final selectedId = state.selectedReleaseId;
    final rollouts =
        selectedId != null ? state.rolloutsByRelease[selectedId] ?? [] : [];

    return Scaffold(
      backgroundColor: TacticalColors.background,
      appBar: AppBar(title: const Text('OTA Firmware Manager')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          PermissionGuard(
            permission: AppPermissions.otaUpload,
            fallback: TacticalCard(
              child: Text(
                'Read-only: your role cannot upload OTA firmware.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: TacticalColors.textSecondary,
                    ),
              ),
            ),
            child: TacticalCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Upload firmware',
                      style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                TextField(
                  controller: _versionController,
                  decoration: const InputDecoration(labelText: 'Version string'),
                ),
                const SizedBox(height: 10),
                DropdownButtonFormField<DeviceCategoryFilter>(
                  value: _category,
                  decoration: const InputDecoration(labelText: 'Target category'),
                  items: DeviceCategoryFilter.values
                      .where((c) => c != DeviceCategoryFilter.all)
                      .map(
                        (c) => DropdownMenuItem(
                          value: c,
                          child: Text(c.label),
                        ),
                      )
                      .toList(),
                  onChanged: (v) {
                    if (v != null) setState(() => _category = v);
                  },
                ),
                const SizedBox(height: 10),
                OutlinedButton.icon(
                  onPressed: _pickFirmware,
                  icon: const Icon(Icons.memory_outlined),
                  label: Text(_firmwareName ?? 'Select .bin / .elf file'),
                ),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: state.isUploading || _firmwareBytes == null
                      ? null
                      : _upload,
                  child: state.isUploading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Upload & publish rollout'),
                ),
                if (state.error != null) ...[
                  const SizedBox(height: 8),
                  Text(state.error!, style: TextStyle(color: TacticalColors.critical)),
                ],
              ],
            ),
          ),
          ),
          const SizedBox(height: 16),
          TacticalCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Release history',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                if (state.isLoading)
                  const Center(child: CircularProgressIndicator())
                else if (state.releases.isEmpty)
                  Text('No firmware releases yet.',
                      style: Theme.of(context).textTheme.bodySmall)
                else
                  ...state.releases.map((r) {
                    return ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text('v${r.version} · ${r.targetDeviceCategory}'),
                      subtitle: Text(r.checksumSha256.substring(0, 12)),
                      trailing: _StatusBadge(status: r.status),
                      onTap: () => ref
                          .read(otaFirmwareProvider.notifier)
                          .loadRollouts(r.id),
                    );
                  }),
              ],
            ),
          ),
          if (selectedId != null) ...[
            const SizedBox(height: 16),
            TacticalCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Rollout status',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  if (rollouts.isEmpty)
                    Text('No rollout rows yet.',
                        style: Theme.of(context).textTheme.bodySmall)
                  else
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: DataTable(
                        columns: const [
                          DataColumn(label: Text('Device')),
                          DataColumn(label: Text('Status')),
                          DataColumn(label: Text('Reported')),
                        ],
                        rows: rollouts
                            .map(
                              (row) => DataRow(cells: [
                                DataCell(Text(row.deviceName)),
                                DataCell(_StatusBadge(status: row.status)),
                                DataCell(Text(
                                  row.reportedAt?.toLocal().toString().split('.').first ??
                                      '—',
                                )),
                              ]),
                            )
                            .toList(),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

String _otaCategoryApi(DeviceCategoryFilter filter) {
  return switch (filter) {
    DeviceCategoryFilter.droneUnmanned => DeviceCategoryApi.droneUnmanned,
    DeviceCategoryFilter.agricultureAquaculture =>
      DeviceCategoryApi.agricultureAquaculture,
    DeviceCategoryFilter.fieldSensorsLora => DeviceCategoryApi.fieldSensorsLora,
    DeviceCategoryFilter.industrialTelemetry =>
      DeviceCategoryApi.industrialTelemetry,
    DeviceCategoryFilter.smartAssetFleet => DeviceCategoryApi.smartAssetFleet,
    DeviceCategoryFilter.smartHomeBuilding => DeviceCategoryApi.smartHome,
    DeviceCategoryFilter.all => DeviceCategoryApi.fieldSensorsLora,
  };
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final color = switch (status) {
      'active' => TacticalColors.success,
      'archived' => TacticalColors.textSecondary,
      'applied' => TacticalColors.success,
      'failed' => TacticalColors.critical,
      'downloading' => BentoTokens.accentSoftBlue,
      _ => TacticalColors.warning,
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.14),
        borderRadius: BorderRadius.circular(BentoTokens.radiusPill),
        border: Border.all(color: color.withOpacity(0.35)),
      ),
      child: Text(
        status.toUpperCase(),
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}

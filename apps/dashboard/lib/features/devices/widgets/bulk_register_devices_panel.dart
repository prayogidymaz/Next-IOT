import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/ota_models.dart';
import '../providers/device_provider.dart';

const bulkImportTemplate = '''
{
  "devices": [
    { "name": "Lobby Relay", "device_type": "smart_home", "device_category": "SMART_HOME" },
    { "name": "Field Sensor 01", "device_type": "sensor" }
  ]
}
''';

const csvTemplate = 'name,device_type,device_category\nNode A,sensor,\nNode B,lorawan,FIELD_SENSORS_LORA\n';

class BulkRegisterDevicesPanel extends ConsumerStatefulWidget {
  const BulkRegisterDevicesPanel({super.key, required this.onCompleted});

  final VoidCallback onCompleted;

  @override
  ConsumerState<BulkRegisterDevicesPanel> createState() =>
      _BulkRegisterDevicesPanelState();
}

class _BulkRegisterDevicesPanelState extends ConsumerState<BulkRegisterDevicesPanel> {
  final _pasteController = TextEditingController();
  BulkImportResult? _result;
  String? _pickedFileName;

  @override
  void dispose() {
    _pasteController.dispose();
    super.dispose();
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['json', 'csv'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;
    final file = result.files.first;
    final bytes = file.bytes;
    if (bytes == null) return;
    setState(() {
      _pickedFileName = file.name;
      _pasteController.text = utf8.decode(bytes);
    });
  }

  Future<void> _submit({required bool fromPaste}) async {
    final notifier = ref.read(deviceProvider.notifier);
    BulkImportResult? result;
    if (_pickedFileName != null && !fromPaste) {
      result = await notifier.bulkImport(
        fileBytes: utf8.encode(_pasteController.text),
        filename: _pickedFileName!,
      );
    } else {
      final text = _pasteController.text.trim();
      if (text.contains('name,device_type')) {
        result = await notifier.bulkImport(
          fileBytes: utf8.encode(text),
          filename: 'paste.csv',
        );
      } else {
        result = await notifier.bulkImportFromJson(
          jsonDecode(text) as Map<String, dynamic>,
        );
      }
    }
    if (!mounted) return;
    if (result != null) {
      setState(() => _result = result);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isRegistering =
        ref.watch(deviceProvider.select((s) => s.isRegistering));
    final error = ref.watch(deviceProvider.select((s) => s.error));

    if (_result != null) {
      return _buildResult(context, _result!);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          'Drop or paste CSV/JSON to register up to 500 devices.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 12),
        DragTarget<List<int>>(
          onWillAcceptWithDetails: (_) => true,
          onAcceptWithDetails: (details) {
            setState(() {
              _pickedFileName = 'dropped.json';
              _pasteController.text = utf8.decode(details.data);
            });
          },
          builder: (context, candidate, rejected) {
            final active = candidate.isNotEmpty;
            return AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: active
                    ? BentoTokens.accentSoftBlue.withOpacity(0.12)
                    : TacticalColors.surface,
                borderRadius: BorderRadius.circular(BentoTokens.radius),
                border: Border.all(
                  color: active
                      ? BentoTokens.accentSoftBlue
                      : TacticalColors.border,
                  width: active ? 2 : 1,
                ),
              ),
              child: Column(
                children: [
                  Icon(Icons.upload_file,
                      color: active
                          ? BentoTokens.accentSoftBlue
                          : TacticalColors.textSecondary),
                  const SizedBox(height: 8),
                  Text(
                    'Drag file here or use picker',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: isRegistering ? null : _pickFile,
                    icon: const Icon(Icons.folder_open, size: 18),
                    label: const Text('Choose CSV / JSON'),
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 12),
        Text('Template preview', style: Theme.of(context).textTheme.labelLarge),
        const SizedBox(height: 6),
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: TacticalColors.surfaceElevated,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            csvTemplate.trim(),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontFamily: 'monospace',
                  fontSize: 11,
                ),
          ),
        ),
        const SizedBox(height: 10),
        TextField(
          controller: _pasteController,
          maxLines: 6,
          decoration: const InputDecoration(
            labelText: 'Paste JSON or CSV',
            alignLabelWithHint: true,
          ),
        ),
        if (error != null) ...[
          const SizedBox(height: 8),
          Text(error, style: TextStyle(color: TacticalColors.critical)),
        ],
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: isRegistering ? null : () => _submit(fromPaste: true),
          icon: isRegistering
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.cloud_upload_outlined),
          label: const Text('Bulk import'),
        ),
      ],
    );
  }

  Widget _buildResult(BuildContext context, BulkImportResult result) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          'Imported ${result.importedCount} · Failed ${result.failedCount}',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        if (result.errors.isNotEmpty)
          ...result.errors.take(3).map(
                (e) => Text(
                  'Row ${e.row}: ${e.detail}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: TacticalColors.warning,
                      ),
                ),
              ),
        const SizedBox(height: 12),
        FilledButton(
          onPressed: () {
            widget.onCompleted();
            Navigator.of(context).pop();
          },
          child: const Text('Done'),
        ),
      ],
    );
  }
}

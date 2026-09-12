import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/tactical_theme.dart';
import '../data/telemetry_repository.dart';
import '../models/telemetry_analytics_models.dart';
import '../providers/telemetry_provider.dart';
class TelemetryExportDialog extends ConsumerStatefulWidget {
  const TelemetryExportDialog({
    super.key,
    required this.deviceId,
    this.deviceName,
  });

  final String deviceId;
  final String? deviceName;

  static Future<void> show(
    BuildContext context, {
    required String deviceId,
    String? deviceName,
  }) {
    return showDialog<void>(
      context: context,
      builder: (_) => TelemetryExportDialog(deviceId: deviceId, deviceName: deviceName),
    );
  }

  @override
  ConsumerState<TelemetryExportDialog> createState() => _TelemetryExportDialogState();
}

class _TelemetryExportDialogState extends ConsumerState<TelemetryExportDialog> {
  int _hours = 24;
  TelemetryExportFormat _format = TelemetryExportFormat.csv;
  bool _isExporting = false;
  String? _savedPath;

  Future<void> _download() async {
    setState(() {
      _isExporting = true;
      _savedPath = null;
    });

    try {
      final path = await ref.read(telemetryRepositoryProvider).downloadExport(
            deviceId: widget.deviceId,
            format: _format,
            hours: _hours,
          );
      if (!mounted) return;
      setState(() {
        _isExporting = false;
        _savedPath = path;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _isExporting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Export failed. Check connection and try again.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final title = widget.deviceName ?? 'Device ${widget.deviceId.substring(0, 8)}';

    return AlertDialog(
      backgroundColor: TacticalColors.surface,
      title: const Text('EXPORT TELEMETRY DATA'),
      content: SizedBox(
        width: 360,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title.toUpperCase(),
              style: Theme.of(context).textTheme.labelMedium?.copyWith(color: TacticalColors.cyan),
            ),
            const SizedBox(height: 16),
            Text('Time Range', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 8),
            SegmentedButton<int>(
              segments: const [
                ButtonSegment(value: 1, label: Text('1 Hour')),
                ButtonSegment(value: 24, label: Text('24 Hours')),
              ],
              selected: {_hours},
              onSelectionChanged: _isExporting ? null : (value) => setState(() => _hours = value.first),
            ),
            const SizedBox(height: 16),
            Text('Export Format', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 8),
            DropdownButtonFormField<TelemetryExportFormat>(
              value: _format,
              decoration: const InputDecoration(isDense: true),
              dropdownColor: TacticalColors.surfaceElevated,
              items: TelemetryExportFormat.values
                  .map((f) => DropdownMenuItem(value: f, child: Text(f.label)))
                  .toList(),
              onChanged: _isExporting
                  ? null
                  : (value) {
                      if (value != null) setState(() => _format = value);
                    },
            ),
            if (_savedPath != null) ...[
              const SizedBox(height: 12),
              Text(
                'Saved to:\n$_savedPath',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(color: TacticalColors.success),
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isExporting ? null : () => Navigator.of(context).pop(),
          child: const Text('Close'),
        ),
        FilledButton.icon(
          onPressed: _isExporting ? null : _download,
          icon: _isExporting
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : const Icon(Icons.download, size: 18),
          label: Text(_isExporting ? 'Exporting...' : 'Download'),
        ),
      ],
    );
  }
}

import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/tactical_theme.dart';

class PipelineJsonIoDialog extends StatefulWidget {
  const PipelineJsonIoDialog({
    super.key,
    required this.onImport,
    this.readOnlyPreview = false,
  });

  final Future<void> Function(Map<String, dynamic> document) onImport;
  final bool readOnlyPreview;

  static Future<void> showImport(
    BuildContext context, {
    required Future<void> Function(Map<String, dynamic> document) onImport,
    bool readOnlyPreview = false,
  }) {
    return showDialog<void>(
      context: context,
      builder: (_) => PipelineJsonIoDialog(
        onImport: onImport,
        readOnlyPreview: readOnlyPreview,
      ),
    );
  }

  @override
  State<PipelineJsonIoDialog> createState() => _PipelineJsonIoDialogState();
}

class _PipelineJsonIoDialogState extends State<PipelineJsonIoDialog> {
  String? _fileName;
  Map<String, dynamic>? _document;
  String? _error;
  bool _busy = false;

  Future<void> _pickFile() async {
    setState(() {
      _error = null;
      _document = null;
      _fileName = null;
    });
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['json'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;
    final file = result.files.first;
    final bytes = file.bytes;
    if (bytes == null) {
      setState(() => _error = 'Could not read file bytes');
      return;
    }
    try {
      final decoded = jsonDecode(utf8.decode(bytes));
      if (decoded is! Map<String, dynamic>) {
        setState(() => _error = 'JSON root must be an object');
        return;
      }
      setState(() {
        _document = decoded;
        _fileName = file.name;
      });
    } catch (e) {
      setState(() => _error = 'Invalid JSON: $e');
    }
  }

  Future<void> _submit() async {
    final doc = _document;
    if (doc == null) return;
    setState(() => _busy = true);
    try {
      await widget.onImport(doc);
      if (mounted) Navigator.pop(context);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: TacticalColors.surface,
      title: const Text('Import Pipeline JSON'),
      content: SizedBox(
        width: 480,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              widget.readOnlyPreview
                  ? 'Validate and load pipeline locally (read-only mode).'
                  : 'Drop or pick a pipeline export file (.json).',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: _busy ? null : _pickFile,
              icon: const Icon(Icons.upload_file),
              label: Text(_fileName ?? 'Choose JSON file'),
            ),
            if (_error != null) ...[
              const SizedBox(height: 8),
              Text(_error!, style: const TextStyle(color: TacticalColors.critical)),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: _document == null || _busy ? null : _submit,
          child: _busy
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Import'),
        ),
      ],
    );
  }
}

Future<void> copyPipelineJsonToClipboard(Map<String, dynamic> document) async {
  final encoded = const JsonEncoder.withIndent('  ').convert(document);
  await Clipboard.setData(ClipboardData(text: encoded));
}

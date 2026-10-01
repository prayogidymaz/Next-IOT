import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/tactical_theme.dart';
import '../models/automation_pipeline_models.dart';

class NodeConfigDialog extends StatefulWidget {
  const NodeConfigDialog({
    super.key,
    required this.node,
    required this.onSave,
  });

  final PipelineNodeModel node;
  final ValueChanged<Map<String, dynamic>> onSave;

  static Future<void> show(
    BuildContext context, {
    required PipelineNodeModel node,
    required ValueChanged<Map<String, dynamic>> onSave,
  }) {
    return showDialog<void>(
      context: context,
      builder: (_) => NodeConfigDialog(node: node, onSave: onSave),
    );
  }

  @override
  State<NodeConfigDialog> createState() => _NodeConfigDialogState();
}

class _NodeConfigDialogState extends State<NodeConfigDialog> {
  late final Map<String, dynamic> _config;

  @override
  void initState() {
    super.initState();
    _config = Map<String, dynamic>.from(widget.node.config);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: TacticalColors.surface,
      title: Text('Configure ${widget.node.label}'),
      content: SizedBox(
        width: 420,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                '${widget.node.type.name.toUpperCase()} · ${widget.node.subtype}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 16),
              ..._fieldsForSubtype(widget.node.subtype),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel')),
        FilledButton(
          onPressed: () {
            widget.onSave(_config);
            Navigator.pop(context);
          },
          child: const Text('Save'),
        ),
      ],
    );
  }

  List<Widget> _fieldsForSubtype(String subtype) {
    return switch (subtype) {
      'AI_DETECTION' => [
          _textField('target_class', 'Target AI class', defaultValue: 'person'),
          _numberField('min_confidence', 'Min confidence (0-1)',
              defaultValue: 0.7),
        ],
      'WIND_SPEED_LESS_THAN' => [
          _numberField('max_wind_mps', 'Max wind speed (m/s)',
              defaultValue: 12),
        ],
      'BATTERY_ABOVE' => [
          _numberField('min_percent', 'Minimum battery %', defaultValue: 30),
        ],
      'TIME_WINDOW' => [
          _numberField('start_hour', 'Start hour (0-23)',
              defaultValue: 6, isInt: true),
          _numberField('end_hour', 'End hour (0-23)',
              defaultValue: 18, isInt: true),
        ],
      'DISPATCH_SAR_GRID' => [
          _numberField('radius_m', 'Search radius (m)',
              defaultValue: 500, isInt: true),
        ],
      'WEBSOCKET_ALERT' => [
          _textField('channel', 'Alert channel',
              defaultValue: 'tactical-alerts'),
          _textField('message', 'Alert message',
              defaultValue: 'Automation triggered'),
        ],
      'MAVLINK_ARM' || 'MAVLINK_RTL' || 'MAVLINK_LAND' => [
          _textField('device_id', 'Target device ID', defaultValue: ''),
        ],
      'TRIGGER_ALARM' || 'TRIGGER_ALERT' => [
          _textField('alarm_code', 'Alarm code', defaultValue: 'AUTO-001'),
          _textField('message', 'Alert message', defaultValue: 'Automation alert'),
        ],
      'TELEMETRY_THRESHOLD' => [
          _textField('metric', 'Metric key', defaultValue: 'temperature'),
          _textField('operator', 'Operator (>, <, >=, <=, ==)', defaultValue: '>'),
          _numberField('threshold', 'Threshold', defaultValue: 30),
        ],
      'LOGIC_AND' || 'LOGIC_OR' => [
          const Text(
            'Uses conditions array in JSON import; default demo clause applied on save.',
            style: TextStyle(color: TacticalColors.textSecondary),
          ),
        ],
      'DEVICE_COMMAND' => [
          _textField('device_id', 'Device ID', defaultValue: 'relay-1'),
          _textField('command', 'Command (relay_on / relay_off)', defaultValue: 'relay_on'),
        ],
      'SEND_WEBHOOK' => [
          _textField('url', 'Webhook URL', defaultValue: 'https://example.com/hook'),
          _textField('method', 'HTTP method', defaultValue: 'POST'),
        ],
      _ => [
          const Text(
            'No extra parameters for this block.',
            style: TextStyle(color: TacticalColors.textSecondary),
          ),
        ],
    };
  }

  Widget _textField(String key, String label, {required String defaultValue}) {
    _config.putIfAbsent(key, () => defaultValue);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        initialValue: _config[key]?.toString() ?? defaultValue,
        decoration: InputDecoration(labelText: label),
        onChanged: (v) => _config[key] = v,
      ),
    );
  }

  Widget _numberField(
    String key,
    String label, {
    required num defaultValue,
    bool isInt = false,
  }) {
    _config.putIfAbsent(key, () => defaultValue);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        initialValue: (_config[key] ?? defaultValue).toString(),
        decoration: InputDecoration(labelText: label),
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        inputFormatters: [
          FilteringTextInputFormatter.allow(
              RegExp(isInt ? r'[0-9]' : r'[0-9.]'))
        ],
        onChanged: (v) {
          _config[key] = isInt
              ? int.tryParse(v) ?? defaultValue
              : double.tryParse(v) ?? defaultValue;
        },
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/device_models.dart';
import '../providers/device_provider.dart';

Future<void> showRegisterDeviceDialog(BuildContext context, WidgetRef ref) async {
  await showDialog<void>(
    context: context,
    builder: (context) => const RegisterDeviceDialog(),
  );
}

class RegisterDeviceDialog extends ConsumerStatefulWidget {
  const RegisterDeviceDialog({super.key});

  @override
  ConsumerState<RegisterDeviceDialog> createState() => _RegisterDeviceDialogState();
}

class _RegisterDeviceDialogState extends ConsumerState<RegisterDeviceDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  DeviceType _selectedType = DeviceType.sensor;
  RegisterDeviceResult? _result;

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final result = await ref.read(deviceProvider.notifier).registerDevice(
          name: _nameController.text,
          deviceType: _selectedType,
        );

    if (!mounted) return;
    if (result != null) {
      setState(() => _result = result);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isRegistering = ref.watch(deviceProvider.select((s) => s.isRegistering));
    final error = ref.watch(deviceProvider.select((s) => s.error));

    return AlertDialog(
      title: Text(_result == null ? 'Register New Device' : 'Device Registered'),
      content: SizedBox(
        width: 420,
        child: _result == null ? _buildForm(isRegistering, error) : _buildSuccess(_result!),
      ),
      actions: [
        if (_result == null) ...[
          TextButton(
            onPressed: isRegistering ? null : () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: isRegistering ? null : _submit,
            child: isRegistering
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Register'),
          ),
        ] else
          FilledButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Done'),
          ),
      ],
    );
  }

  Widget _buildForm(bool isRegistering, String? error) {
    return Form(
      key: _formKey,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextFormField(
            controller: _nameController,
            decoration: const InputDecoration(
              labelText: 'Device name',
              border: OutlineInputBorder(),
            ),
            enabled: !isRegistering,
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Name required';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<DeviceType>(
            value: _selectedType,
            decoration: const InputDecoration(
              labelText: 'Device type',
              border: OutlineInputBorder(),
            ),
            items: DeviceType.values
                .map(
                  (type) => DropdownMenuItem(
                    value: type,
                    child: Text(type.label),
                  ),
                )
                .toList(),
            onChanged: isRegistering
                ? null
                : (value) {
                    if (value != null) setState(() => _selectedType = value);
                  },
          ),
          if (error != null) ...[
            const SizedBox(height: 12),
            Text(error, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ],
        ],
      ),
    );
  }

  Widget _buildSuccess(RegisterDeviceResult result) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('${result.device.name} (${result.device.deviceTypeLabel}) is ready to provision.'),
        const SizedBox(height: 12),
        const Text('Provisioning token (copy now — shown once):',
            style: TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        SelectableText(
          result.provisioningToken,
          style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
        ),
        const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerRight,
          child: TextButton.icon(
            onPressed: () {
              Clipboard.setData(ClipboardData(text: result.provisioningToken));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Token copied to clipboard')),
              );
            },
            icon: const Icon(Icons.copy, size: 18),
            label: const Text('Copy token'),
          ),
        ),
        Text(
          'Expires in ${result.provisioningExpiresInHours} hours.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}

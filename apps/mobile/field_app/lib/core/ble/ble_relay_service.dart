import 'dart:convert';

import 'package:flutter_blue_plus/flutter_blue_plus.dart';

import 'field_ble_uuids.dart';

class BleRelayService {
  Future<void> writeRelayCommand({
    required String remoteId,
    required bool on,
    String channel = 'ch1',
  }) async {
    final device = BluetoothDevice.fromId(remoteId);
    await device.connect(timeout: const Duration(seconds: 12));
    try {
      final services = await device.discoverServices();
      BluetoothCharacteristic? commandChar;
      for (final service in services) {
        if (service.uuid.toString().toLowerCase() != FieldBleUuids.relayService) continue;
        for (final c in service.characteristics) {
          if (c.uuid.toString().toLowerCase() == FieldBleUuids.relayCommandChar && c.properties.write) {
            commandChar = c;
            break;
          }
        }
      }
      commandChar ??= _findFirstWritableChar(services);
      if (commandChar == null) {
        throw StateError('Relay command characteristic not found on $remoteId');
      }
      final payload = utf8.encode(
        jsonEncode({'channel': channel, 'state': on ? 'ON' : 'OFF'}),
      );
      await commandChar.write(payload, withoutResponse: false);
    } finally {
      await device.disconnect();
    }
  }

  BluetoothCharacteristic? _findFirstWritableChar(List<BluetoothService> services) {
    for (final service in services) {
      for (final c in service.characteristics) {
        if (c.properties.write || c.properties.writeWithoutResponse) return c;
      }
    }
    return null;
  }
}

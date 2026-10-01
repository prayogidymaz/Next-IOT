# Next-IoT Field Execution App

Tactical Clean / Warm Cream Flutter package for field operators (ESP32-S3, Orange Pi edge nodes).

## Layout

```
lib/
  main.dart                 # MaterialApp + Riverpod
  app_router.dart           # go_router: login → scanner → HUD
  core/
    api/field_api_client.dart
    storage/token_storage.dart
    storage/offline_telemetry_store.dart   # SQLite queue (sqflite)
    theme/field_theme.dart
  features/
    auth/                     # Login + secure JWT storage
    scanner/                  # flutter_blue_plus LE scan + Wi-Fi stub
    hud/                      # Relay REST/BLE GATT, telemetry, bulk sync
    ble/                      # GATT relay write (NUS UUIDs)
    sync/telemetry_sync_service.dart
test/
  widget_test.dart
```

## Run

```bash
cd apps/mobile/field_app
flutter pub get
flutter analyze
flutter test
flutter run
```

Set **API base URL** on the login screen (`http://10.0.2.2:8000` for Android emulator → host API).

## API integration

| Action | Endpoint | Auth |
| --- | --- | --- |
| Login | `POST /auth/login` | — |
| Relay on/off | `POST /api/v1/devices/{uuid}/commands` | Operator JWT |
| Offline queue flush | `POST /api/v1/telemetry/bulk` | Operator JWT |
| Single telemetry | `POST /api/v1/telemetry` | Device Basic (when provisioned) |

Command body example:

```json
{ "command_type": "RELAY_ON", "params": { "channel": "ch1" } }
```

**Auto-pairing:** register device metadata in PostgreSQL (`ble_mac`, `field_slug`, `mdns_name`). Scanner loads `GET /api/v1/devices` and sets `apiDeviceId` on each BLE/mDNS hit.

**mDNS service types:** `_next-iot._tcp.local`, `_nextiot._tcp.local`, `_next-iot-edge._tcp.local` (LAN, no internet required).

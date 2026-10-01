# Next-IoT Mobile Apps

| Package | Role |
| --- | --- |
| [`apps/dashboard`](../dashboard) | Operator tablet / domain shell (onboarding, tactical map, segments) |
| [`apps/mobile/field_app`](field_app) | **Field Execution** — BLE/Wi-Fi discovery, relay HUD, offline telemetry queue |

## Field Execution (`field_app`)

Tactical Clean / Warm Cream Flutter app for edge operators.

```bash
cd apps/mobile/field_app
flutter pub get
flutter test
flutter run
```

- **API base:** Android emulator default `http://10.0.2.2:8000` (set on login).
- **Relay commands:** `POST /api/v1/devices/{id}/commands` with operator JWT (`RELAY_ON` / `RELAY_OFF`).
- **Telemetry ingest:** `POST /api/v1/telemetry` (device Basic auth — queue flush when credentials are provisioned).

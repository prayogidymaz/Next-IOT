# Next-IOT Dashboard (Flutter)

Multi-tenant tactical UI for Next-IOT platform.

## Stack

- **Flutter** 3.3+
- **Riverpod** — state management
- **go_router** — navigation + auth redirect
- **Dio** — HTTP client to FastAPI backend

## Setup

```bash
cd apps/dashboard
flutter pub get
```

## Run

```bash
# Desktop / web (default API: http://localhost:8000)
flutter run -d chrome

# Android emulator (API on host machine)
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Ensure backend is running: `docker compose up -d api`

### Default login (dev)

| Email | Password |
|-------|----------|
| `admin@nextiot.com` | `admin123` |

Credentials are auto-seeded on API startup. See [../../docs/DEFAULT-CREDENTIALS.md](../../docs/DEFAULT-CREDENTIALS.md).

## Test & Build

```bash
flutter test
flutter build web
```

## Alerts & rule builder

Home screen tabs:
- **Devices** — device list + detail with telemetry charts
- **Map View** — tactical OSM map with GPS markers, fleet overlay, Center on Device
- **Alerts** — active alerts, rules, Telegram test button

Device detail includes **MAP TRACKING** section with live GPS + telemetry overlay.

## Device detail & telemetry

Click a device in the list to open **DeviceDetailScreen** with live gauges, tactical GPS indicator, and `fl_chart` time-series (1H / 24H / 7D).

Demo data: login as admin, open **Demo Sensor Node** (auto-seeded telemetry).

## Structure

```
lib/
├── main.dart              # Bootstrap + session restore
├── app.dart               # MaterialApp + theme
├── core/
│   ├── config/            # API base URL
│   ├── network/           # Dio client + JWT refresh interceptor
│   └── auth/              # Token storage (SharedPreferences)
├── features/auth/         # Login, home, repository, providers
└── routing/               # go_router config
```

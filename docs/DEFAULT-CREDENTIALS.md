# Default Login Credentials (Dev)

Auto-seeded when the API starts (`SEED_DEFAULT_ADMIN=true`, default).

| Field | Value |
|-------|-------|
| Email | `admin@nextiot.com` |
| Password | `admin123` |
| Role | `super_admin` |
| Tenant slug | `nextiot` |

## Manual re-seed

```bash
docker compose exec api python -m app.seed
```

> Pytest uses isolated DB `next_iot_test` (dev data is not wiped). API auto re-seeds missing admin on `/health` in development.

## Flutter Web

1. Start backend: `docker compose up -d api`
2. Run dashboard: `cd apps/dashboard && flutter run -d chrome`
3. Login with credentials above (API: `http://localhost:8000`)

Override seed via `.env`: `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD`.

## Demo telemetry (charts)

On API startup, a **Demo Sensor Node** is seeded with 7 days of mock telemetry (temperature, humidity, battery, orientation, GPS).

Manual re-seed:

```bash
docker compose exec api python -m app.seed_telemetry
```

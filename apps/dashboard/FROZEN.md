# apps/dashboard — FROZEN (reference only)

**Status:** Frozen — no new features, no refactors, no dependency upgrades unless the user explicitly requests a change.

**Purpose:** Legacy Flutter **HQ dashboard** kept as a porting reference until every screen below exists in **`apps/web`** (Next.js). Official clients: **Web HQ = `apps/web`**, **Mobile = `apps/mobile/field_app`**.

**After porting:** delete this app from the monorepo.

---

## Feature areas → API endpoints (porting backlog)

| Feature folder | Screens / entry points | Primary API usage |
| --- | --- | --- |
| `auth` | `login_screen`, `home_screen` | `POST /auth/login`, `POST /auth/logout`, `GET /api/v1/auth/me` |
| `onboarding` | `domain_onboarding_screen` | Domain profile / navigation (local + tenant context) |
| `dashboard` | Bento layout widgets (smart home, indoor location, sidebar) | Telemetry latest/history, device list |
| `devices` | `device_list_screen`, `device_detail_screen`, `ota_firmware_screen` | `GET/POST /api/v1/devices`, `POST /api/v1/devices/bulk-import`, OTA below |
| `devices` (OTA) | `ota_firmware_screen` | `GET/POST /api/v1/ota/releases`, publish, rollouts |
| `map` | `tactical_map_screen`, overlays (SAR grid, swarm, signal heatmap, weather) | `GET /api/v1/telemetry/weather-vector`, `GET /api/v1/telemetry/signal-heatmap`, tile proxy |
| `telemetry` | `telemetry_analytics_screen`, anomaly badges | `GET .../telemetry/latest`, `.../history`, `GET /api/v1/telemetry/analytics`, `GET /api/v1/telemetry/export`, `GET /api/v1/telemetry/anomalies`, `GET /api/v1/telemetry/flight-replay` |
| `video` | Tactical video HUD (WS) | `WS /api/v1/telemetry/video-feed/{deviceId}?token=` |
| `alerts` | `alerts_screen`, `alert_engine_screen`, rule dialogs | `GET /api/v1/alerts`, `GET /api/v1/alerts/summary`, `GET/POST/PUT/DELETE /api/v1/rules` |
| `rules` | (shared with alerts) | `GET/POST/PUT/DELETE /api/v1/rules` |
| `automation` | `automation_builder_screen`, studio widgets | `GET/POST/PUT/DELETE /api/v1/automation/pipelines`, dry-run, test-run, `GET /api/v1/rules/{id}/export`, `POST /api/v1/rules/import`, `POST /api/v1/rules/validate` |
| `studio` | `automation_studio_screen` | Same as automation + `/studio` routing |
| `mission` | Mission overlay, waypoints, SAR panels | `POST /api/v1/devices/{id}/commands`, `GET/POST /api/v1/mission/geofence`, `GET/POST/PATCH/DELETE /api/v1/mission/sar-incidents`, `GET/POST /api/v1/mission/sar-grid` |
| `mavlink` | Status badge, attitude horizon | `GET /api/v1/hardware/mavlink/status` |
| `hardware` | Gateway status | `GET /api/v1/hardware/gateway-status` |
| `cyberdeck` | `cyberdeck_console_screen`, PTT panels | `GET /api/v1/hardware/cyberdeck/mesh`, `.../health`, `POST .../ptt/text`, `POST .../ptt/beacon` |
| `audit` | `audit_log_screen` | `GET /api/v1/audit-logs`, `GET /api/v1/audit-logs/export` |
| `system` | Health indicator | `GET /api/v1/system/health` |
| `settings` | `organization_members_screen` | `GET/POST /api/v1/tenants`, `POST /api/v1/tenants/switch`, members CRUD |
| `tenants` | (providers + repo) | `GET/POST /api/v1/tenants`, switch, members |
| `notifications` | Test channel | `POST /api/v1/notifications/test` |

---

## Engineering notes

- Do **not** run `scripts/check-all.ps1` against this package; CI targets `apps/web` and `apps/mobile/field_app` only.
- When porting a row, tick it in Notion / `NOTION_UPDATE.md` and implement the equivalent route under `apps/web`.

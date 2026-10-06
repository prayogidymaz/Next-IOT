# Next-IOT — Notion Update Log (Master Changelog)

**Last updated:** 2026-10-06 (UTC+7)  

### Step 3A — EMQX overlay + ACL manual finding (synced)

- **Menu:** Device Credentials + EMQX → **In progress**; **`infra/emqx/overlay/`** → `emqx.conf.d` merge (not single `emqx.conf` override). Manual test: missing overlay caused crash loop + ACL bypass (publish as another device); API `/mqtt/acl` logic covered by integration pytest.

### Step 3A — EMQX HOCON webhook headers (synced)

- Superseded by overlay directory mount (see above).

### Step 3A — Credential conflict fix (synced)

- **Menu:** Device Credentials + EMQX → **In progress**; **API behavior:** `POST …/credentials` → **201** first time, **409** if active credential exists (message directs to `/rotate`); rotate = new token + new `dev_*` client_id, old token denied for MQTT auth.
- **Migration:** Alembic **017** partial unique on active `client_id` / `access_token`.
- **Commit:** amend `b7f767d` — Step 3A fixes + ~275 pytest.

### Step 3 — MQTT / EMQX (synced)

- **Menus:** Device Credentials + EMQX, QR Device Claim → **In progress**.
- **Commit:** (pending) — EMQX compose, migration 016, webhooks, claim flow, 20 pytest.

### Step 2B — Thing model at ingest (synced)

- **Menu:** Telemetry Bulk Ingest (≤200) → **In progress** + notes.
- **Commit:** (pending) — bulk partial-success 200, command 400, `/metrics` counters.

### Step 2A — TimescaleDB (synced)

- **Menu:** TimescaleDB Hypertable + Retention per Tier → **In progress** + Implementation Notes appended.
- **Commit:** `50e962c` — hypertable 015, retention sweep, compose preload fix.

**Sync target:** Notion database **Next-IOT Development Tasks**  
**Companion backlog:** `NOTION_TASKS_BACKLOG.md`

---

## Document purpose

Structured, chronological record of **Milestones 1–9** (enterprise platform → web marketing → cyberdeck PTT → **field hardware**). Each milestone lists **backend API**, **Flutter dashboard (`apps/dashboard`)**, **Web (`apps/web`)**, **docs/hardware** where applicable, and **verification** at last audit.

### Latest verification snapshot (2026-09-20)

| Suite | Command | Result |
| --- | --- | --- |
| Backend API | `docker compose run --rm api pytest -q` | **204 passed** |
| Flutter dashboard | `cd apps/dashboard && flutter test` | **133 passed** |
| Next.js marketing web | `cd apps/web && npm run build` | **Pass** (`/`, `/dashboard`, `/cyberdeck`) |

---

## Table of contents

1. [MILESTONE 1 — OTA Firmware Management & Dynamic Rollouts](#milestone-1--ota-firmware-management--dynamic-rollouts)
2. [MILESTONE 2 — Multi-Tenancy Architecture & Fine-Grained RBAC UI Guard](#milestone-2--multi-tenancy-architecture--fine-grained-rbac-ui-guard)
3. [MILESTONE 3 — Automation Studio (Visual Drag & Drop JSON Pipeline Engine)](#milestone-3--automation-studio-visual-drag--drop-json-pipeline-engine)
4. [MILESTONE 4 — Time-Series Data Analytics, Aggregation, & CSV Export Pipeline](#milestone-4--time-series-data-analytics-aggregation--csv-export-pipeline)
5. [MILESTONE 5 — Enterprise Operations, System Health, & Audit Logging](#milestone-5--enterprise-operations-system-health--audit-logging)
6. [MILESTONE 6 — Tuya OS UI Component (`TuyaSmartDashboard`)](#milestone-6--tuya-os-ui-component-tuyasmartdashboard)
7. [MILESTONE 7 — Public Marketing Landing Page & Route Restructuring](#milestone-7--public-marketing-landing-page--route-restructuring)
8. [MILESTONE 8 — Cyberdeck Tactical Console & LoRa PTT Voice/Text Bridge](#milestone-8--cyberdeck-tactical-console--lora-ptt-voicetext-bridge)
9. [MILESTONE 9 — Real Hardware Flashing & LoRa PTT Field Test Protocol](#milestone-9--real-hardware-flashing--lora-ptt-field-test-protocol)
10. [MILESTONE 10 — Production Docker Compose Hardening & Colocation Deployment](#milestone-10--production-docker-compose-hardening--colocation-deployment)
11. [MILESTONE 11 — Real Authentication Flow & Route RBAC Guard](#milestone-11--real-authentication-flow--route-rbac-guard)
12. [MILESTONE 12 — Master Platform Restructuring (Segments & Dynamic Mobile/Web HQ)](#milestone-12--master-platform-restructuring-segments--dynamic-mobileweb-hq)
13. [MILESTONE 13 — Web HQ Core & Warm Cream UI Redesign](#milestone-13--web-hq-core--warm-cream-ui-redesign)
14. [MILESTONE 14 — Web HQ Left Sidebar Refactor](#milestone-14--web-hq-left-sidebar-refactor)
15. [MILESTONE 17 — Field Execution Flutter App & Hardware Command Bridge](#milestone-17--field-execution-flutter-app--hardware-command-bridge)
16. [MILESTONE 18 — Hardware Pairing & Local mDNS Discovery](#milestone-18--hardware-pairing--local-mdns-discovery)
17. [P0 Step 0 — Engineering Guardrails (Strict Typing, CI Checks)](#p0-step-0--engineering-guardrails-strict-typing-ci-checks)
18. [Appendix — Additional platform work (post-milestone)](#appendix--additional-platform-work-post-milestone)

---

## MILESTONE 1 — OTA Firmware Management & Dynamic Rollouts

**Status:** ✅ Complete  
**Theme:** Device fleet onboarding at scale + firmware release lifecycle.

### Backend API (`apps/api`)

| Method | Endpoint | Notes |
| --- | --- | --- |
| `POST` | `/api/v1/devices/bulk-import` | JSON body or multipart CSV/JSON; batch up to 500 devices / tenant |
| `GET` | `/api/v1/ota/releases` | List firmware releases |
| `POST` | `/api/v1/ota/releases` | Upload `.bin` / `.elf` firmware artifact |
| `POST` | `/api/v1/ota/releases/{release_id}/publish` | Publish release for rollout |
| `GET` | `/api/v1/ota/releases/{release_id}/rollouts` | Rollout status per device |
| `GET` | `/api/v1/ota/releases/{release_id}/download` | Operator download |
| `GET` | `/api/v1/ota/device/releases/{release_id}/download` | Device-scoped download |
| `GET` | `/api/v1/ota/check` | Device Basic-auth OTA update check |
| `POST` | `/api/v1/ota/releases/{release_id}/rollouts/status` | Device reports rollout progress |

**Schema / migrations**

- `011_firmware_releases_ota` — `firmware_releases`, `ota_device_rollouts`

**Key modules**

```
apps/api/app/devices/bulk_import.py
apps/api/app/devices/router.py          # bulk-import route
apps/api/app/ota/router.py
apps/api/app/ota/service.py
apps/api/app/ota/storage.py
apps/api/app/models/firmware_release.py
```

### Flutter dashboard (`apps/dashboard`)

| Area | Path |
| --- | --- |
| OTA Firmware Manager screen | `lib/features/devices/screens/ota_firmware_screen.dart` |
| OTA repository & models | `lib/features/devices/data/ota_repository.dart`, `models/ota_models.dart` |
| OTA state | `lib/features/devices/providers/ota_firmware_provider.dart` |
| Bulk register panel | `lib/features/devices/widgets/bulk_register_devices_panel.dart` |

**Routes:** `/devices/ota`, bulk tab on device registration dialog.

### Verification (at milestone sync → current suite green)

| Check | Result |
| --- | --- |
| `pytest` (includes `test_fleet_bulk_ota.py`) | **202/202** (latest audit) |
| `flutter test` | **132/132** (latest audit) |

---

## MILESTONE 2 — Multi-Tenancy Architecture & Fine-Grained RBAC UI Guard

**Status:** ✅ Complete  
**Theme:** Tenant isolation, role tiers, permission-gated UI.

### Backend API (`apps/api`)

| Method | Endpoint | Notes |
| --- | --- | --- |
| `GET` | `/api/v1/tenants` | List tenants for user |
| `POST` | `/api/v1/tenants` | Create tenant (super admin) |
| `POST` | `/api/v1/tenants/switch` | Switch active tenant → new JWT |
| `GET` | `/api/v1/tenants/{tenant_id}/members` | Member list |
| `POST` | `/api/v1/tenants/{tenant_id}/members` | Invite / add member |
| `GET` | `/api/v1/users/me/permissions` | Effective permissions for session |

**Roles:** `super_admin`, `tenant_admin`, `operator`, `viewer`

**Key modules**

```
apps/api/app/tenants/router.py
apps/api/app/tenants/service.py
apps/api/app/auth/permissions.py
apps/api/app/auth/session_context.py
apps/api/app/models/tenant_membership.py
apps/api/alembic/versions/012_tenant_memberships.py
```

### Flutter dashboard (`apps/dashboard`)

| Area | Path |
| --- | --- |
| Tenant switcher | `lib/core/widgets/tenant_switcher.dart` |
| Permission guard | `lib/core/widgets/permission_guard.dart` |
| RBAC maps | `lib/core/rbac/app_permissions.dart`, `role_permissions.dart` |
| Permissions API | `lib/features/auth/data/permissions_repository.dart` |
| Settings / org | `lib/features/settings/` (organization & members) |

**Guards applied:** device register, OTA, alert rule CRUD, automation manage vs run.

### Verification

| Check | Result |
| --- | --- |
| `pytest` (`test_tenant_rbac_api.py`, etc.) | **202/202** |
| `flutter test` | **132/132** |

---

## MILESTONE 3 — Automation Studio (Visual Drag & Drop JSON Pipeline Engine)

**Status:** ✅ Complete  
**Theme:** Visual pipeline builder + JSON import/export + dry-run interpreter.

### Backend API (`apps/api`)

| Method | Endpoint | Notes |
| --- | --- | --- |
| `GET` | `/api/v1/automation/pipelines` | List pipelines |
| `GET` | `/api/v1/automation/pipelines/{pipeline_id}` | Get pipeline |
| `POST` | `/api/v1/automation/pipelines` | Create pipeline |
| `PUT` | `/api/v1/automation/pipelines/{pipeline_id}` | Update pipeline |
| `DELETE` | `/api/v1/automation/pipelines/{pipeline_id}` | Delete pipeline |
| `POST` | `/api/v1/automation/pipelines/dry-run` | Simulate run (no side effects) |
| `POST` | `/api/v1/automation/pipelines/{pipeline_id}/test-run` | Test run bound to pipeline |
| `POST` | `/api/v1/rules/import` | Import pipeline JSON |
| `GET` | `/api/v1/rules/{rule_id}/export` | Export pipeline JSON |
| `POST` | `/api/v1/rules/validate` | Cycle + config validation |

**Engine nodes:** `TELEMETRY_THRESHOLD`, `LOGIC_AND` / `LOGIC_OR`, `DEVICE_COMMAND`, `SEND_WEBHOOK`, `TRIGGER_ALERT`

**Key modules**

```
apps/api/app/automation/router.py
apps/api/app/automation/pipeline_interpreter.py
apps/api/app/automation/pipeline_service.py
apps/api/app/rules/pipeline_io.py
apps/api/app/rules/pipeline_validation.py
apps/api/alembic/versions/009_automation_pipelines.py
```

### Flutter dashboard (`apps/dashboard`)

| Area | Path |
| --- | --- |
| Automation Studio screen | `lib/features/studio/screens/automation_studio_screen.dart` |
| JSON I/O dialog | `lib/features/studio/widgets/pipeline_json_io_dialog.dart` |
| Canvas / nodes / ports | `lib/features/automation/widgets/pipeline_canvas.dart`, `pipeline_node_widget.dart`, `pipeline_port_widget.dart` |
| Builder state | `lib/features/automation/providers/automation_builder_provider.dart` |
| Selection inspector + disconnect | `lib/features/automation/widgets/pipeline_selection_inspector.dart` |

**Route:** `/studio` — 2-step click port wiring, edge disconnect, canvas deselect.

### Verification

| Check | Result |
| --- | --- |
| `pytest` (`test_automation_pipeline_*`, `test_rules_pipeline_io.py`) | **202/202** |
| `flutter test` (canvas / studio widgets) | **132/132** |

---

## MILESTONE 4 — Time-Series Data Analytics, Aggregation, & CSV Export Pipeline

**Status:** ✅ Complete  
**Theme:** Bucketed analytics + streaming CSV export + analytics UI.

### Backend API (`apps/api`)

| Method | Endpoint | Notes |
| --- | --- | --- |
| `GET` | `/api/v1/telemetry/analytics` | Query params: `metrics`, `start_time`, `end_time`, `interval` (`1m\|5m\|1h\|1d`); stats + bucketed series |
| `GET` | `/api/v1/telemetry/export?format=csv` | Tenant-scoped CSV stream with time filters |
| `GET` | `/{device_id}/telemetry/latest` | Latest snapshot (devices router) |
| `GET` | `/{device_id}/telemetry/history` | Paginated history (devices router) |

**Key modules**

```
apps/api/app/telemetry/analytics.py
apps/api/app/telemetry/export_service.py
apps/api/app/telemetry/export_generator.py
apps/api/app/telemetry/timeseries.py
apps/api/app/telemetry/router.py
```

### Flutter dashboard (`apps/dashboard`)

| Area | Path |
| --- | --- |
| Analytics screen | `lib/features/telemetry/screens/telemetry_analytics_screen.dart` |
| Provider & models | `lib/features/telemetry/providers/telemetry_analytics_provider.dart`, `models/telemetry_analytics_models.dart` |
| Charts & summary cards | `lib/features/telemetry/widgets/telemetry_timeseries_chart.dart`, `telemetry_metric_summary_cards.dart` |
| Export dialog | `lib/features/telemetry/widgets/telemetry_export_dialog.dart` |

**Route:** `/analytics`

### Verification

| Check | Result |
| --- | --- |
| `pytest` (`test_telemetry_timeseries_api.py`, export tests) | **202/202** |
| `flutter test` (`telemetry_export_widgets_test.dart`, etc.) | **132/132** |

---

## MILESTONE 5 — Enterprise Operations, System Health, & Audit Logging

**Status:** ✅ Complete  
**Theme:** Compliance audit trail + platform readiness health.

### Backend API (`apps/api`)

| Method | Endpoint | Notes |
| --- | --- | --- |
| `GET` | `/api/v1/audit-logs` | Pagination + filters (tenant scoped) |
| `GET` | `/api/v1/audit-logs/export` | CSV export |
| `GET` | `/api/v1/system/health` | PostgreSQL, Redis, MQTT/broker standby, CPU/RAM |

**Audit actions (examples):** `LOGIN`, `DEVICE_REGISTER`, `DEVICE_COMMAND`, `OTA_UPLOAD`, `RULE_MUTATION`, `TENANT_UPDATE`

**Key modules**

```
apps/api/app/audit/router.py
apps/api/app/audit/service.py
apps/api/app/audit/middleware.py
apps/api/app/system/router.py
apps/api/app/system/health.py
apps/api/alembic/versions/013_audit_logs.py
```

### Flutter dashboard (`apps/dashboard`)

| Area | Path |
| --- | --- |
| Audit log screen | `lib/features/audit/screens/audit_log_screen.dart` |
| Audit repository | `lib/features/audit/data/audit_repository.dart` |
| System health chip | `lib/core/widgets/hardware_gateway_indicator.dart` / system feature widgets under `lib/features/system/` |

**Route:** `/audit` — RBAC `audit.read`

### Verification

| Check | Result |
| --- | --- |
| `pytest` (`test_audit_logs_api.py`, `test_system_health_api.py`) | **202/202** |
| `flutter test` | **132/132** |

---

## MILESTONE 6 — Tuya OS UI Component (`TuyaSmartDashboard`)

**Status:** ✅ Complete  
**Theme:** Smart-home glassmorphism demo UI (Framer Motion + Tailwind) — reference UX for operator-facing control surfaces.

### Web (`apps/web`)

| Path | Role |
| --- | --- |
| `components/TuyaSmartDashboard.tsx` | Main dashboard: device cards, spring toggles, sliders, dark/light mode |
| Stack | Next.js 15, React 19, Tailwind CSS, `framer-motion`, `lucide-react` |

**Interaction spec**

- Glass cards: `rounded-[28px]`, `backdrop-blur-xl`, RSSI-style glow bands
- Hover `scale-[1.02]`, tap `scale-95`, staggered page entrance
- Device demos: AC, lighting, power meter, lock, humidity sensor, usage tile

### Flutter dashboard

- Not primary target for M6; Flutter retains **Tactical / Bento** operator UI in `apps/dashboard`.

### Verification

| Check | Result |
| --- | --- |
| `npm run build` (`apps/web`) | **Pass** |
| `pytest` / `flutter test` | N/A for M6 component (no regression — full suite **202 / 132**) |

---

## MILESTONE 7 — Public Marketing Landing Page & Route Restructuring

**Status:** ✅ Complete  
**Theme:** Tuya.com-style public marketing vs internal app control center.

### Routing (`apps/web`)

| Route | Purpose |
| --- | --- |
| `/` | Public marketing landing |
| `/dashboard` | App Control Center (`TuyaSmartDashboard`) |

### Web components (`apps/web`)

| Path | Role |
| --- | --- |
| `app/page.tsx` | Landing entry → `PublicLandingPage` |
| `app/dashboard/page.tsx` | Control Center entry |
| `components/marketing/PublicLandingPage.tsx` | Navbar, hero, metrics, pricing CTA, footer |
| `components/marketing/DashboardShowcase.tsx` | Browser chrome + `<TuyaSmartDashboard embedded />` |
| `components/marketing/MarketingFeaturesBento.tsx` | 5-module enterprise bento (Automation, OTA, RBAC, Analytics, Audit) |
| `components/TuyaSmartDashboard.tsx` | `embedded` prop for in-frame demo |

**Navbar CTAs:** Sign In / Launch App → `/dashboard`  
**Hero CTAs:** Start Free Trial, View Live Demo (anchor to showcase)

### Verification

| Check | Result |
| --- | --- |
| `npm run build` | **Pass** — static routes `/`, `/dashboard` |
| `pytest` / `flutter test` | **202 / 132** (platform unchanged) |

---

## MILESTONE 8 — Cyberdeck Tactical Console & LoRa PTT Voice/Text Bridge

**Status:** ✅ Complete  
**Theme:** Dedicated low-power tactical operator console + LoRa PTT mesh APIs + Codec2 firmware template.

### Backend API (`apps/api`)

| Method | Endpoint | Notes |
| --- | --- | --- |
| `GET` | `/api/v1/hardware/cyberdeck/mesh` | Active mesh nodes (RSSI/SNR/battery/GPS) |
| `GET` | `/api/v1/hardware/cyberdeck/health` | SBC health (CPU temp, RAM, battery, uptime) |
| `POST` | `/api/v1/hardware/cyberdeck/ptt/text` | Encrypted short text dispatch |
| `POST` | `/api/v1/hardware/cyberdeck/ptt/beacon` | Emergency beacon |

**Key modules**

```
apps/api/app/hardware/cyberdeck_ptt.py
apps/api/app/hardware/cyberdeck_schemas.py
apps/api/app/hardware/router.py
apps/api/tests/test_cyberdeck_ptt_api.py
```

### Flutter dashboard (`apps/dashboard`)

| Route / area | Path |
| --- | --- |
| `/cyberdeck` console | `lib/features/cyberdeck/screens/cyberdeck_console_screen.dart` |
| PTT + waveform | `widgets/cyberdeck_ptt_panel.dart` |
| Mesh tracker | `widgets/cyberdeck_mesh_panel.dart` |
| Text / beacon | `widgets/cyberdeck_text_dispatch_panel.dart` |
| SBC health | `widgets/cyberdeck_health_panel.dart` |
| Theme (pitch black + amber/green) | `theme/cyberdeck_theme.dart` |
| Sidebar nav | `lib/core/widgets/app_sidebar.dart` → **Cyberdeck** |

### Web (`apps/web`)

| Route | Component |
| --- | --- |
| `/cyberdeck` | `components/cyberdeck/CyberdeckConsole.tsx` |

Landing footer link: **Cyberdeck PTT** → `/cyberdeck`.

### Firmware (`docs/firmware/lora-ptt`)

| File | Purpose |
| --- | --- |
| `README.md` | Codec2 + I2S hardware overview |
| `PACKET_STRUCTURE.md` | LoRa PTT header + voice/text/beacon payloads |
| `codec2_ptt_template.ino` | ESP32-S3 Arduino skeleton (INMP441 + MAX98357A + LoRa) |

### Notion

Task **[P1] Dedicated Cyberdeck Tactical UI Console & LoRa PTT Voice Bridge** → **Done** (synced 2026-09-20).

### Verification

| Check | Result |
| --- | --- |
| `pytest` (`test_cyberdeck_ptt_api.py` + full suite) | **204/204** |
| `flutter test` (incl. `cyberdeck_console_test.dart`) | **133/133** |
| `npm run build` | **Pass** — `/cyberdeck` static route |

---

## MILESTONE 9 — Real Hardware Flashing & LoRa PTT Field Test Protocol

**Status:** ✅ Complete  
**Theme:** Option 3 — **ESP32-S3** edge node + **Orange Pi 5 Pro** gateway field test guidance (wiring, flash, validation).

### Documentation (`docs/hardware`)

| Asset | Purpose |
| --- | --- |
| [`field_test_guide.md`](docs/hardware/field_test_guide.md) | Master guide: pinout tables, PlatformIO/esptool, Orange Pi bridge, field protocol |
| [`platformio_esp32s3_ptt.ini`](docs/hardware/platformio_esp32s3_ptt.ini) | Reference PlatformIO env for Codec2 PTT firmware |
| [`scripts/flash_esp32_s3.ps1`](docs/hardware/scripts/flash_esp32_s3.ps1) | Windows esptool flash helper |
| [`scripts/flash_esp32_s3.sh`](docs/hardware/scripts/flash_esp32_s3.sh) | Linux / Orange Pi esptool flash helper |
| [`scripts/measure_ptt_latency.py`](docs/hardware/scripts/measure_ptt_latency.py) | Serial inter-arrival / latency sampling |
| [`scripts/orangepi_bridge_setup.sh`](docs/hardware/scripts/orangepi_bridge_setup.sh) | dialout + Python deps for `lora_bridge` |
| [`scripts/field_test_checklist.sh`](docs/hardware/scripts/field_test_checklist.sh) | Pre-field pass/fail gate |

### Wiring summary (ESP32-S3 edge)

| Subsystem | Signals |
| --- | --- |
| INMP441 | WS→GPIO5, SCK→GPIO4, SD→GPIO6 |
| MAX98357A | LRC→GPIO16, BCLK→GPIO15, DIN→GPIO7 |
| SX1262 SPI | NSS→10, DIO1→11, RST→12, BUSY→13 |
| PTT | GPIO0 → GND (active LOW) |

Cross-reference: [`docs/firmware/lora-ptt/codec2_ptt_template.ino`](docs/firmware/lora-ptt/codec2_ptt_template.ino)

### Orange Pi 5 Pro / Cyberdeck SBC

- Serial: `/dev/ttyUSB0`, group `dialout`, env `LORA_BRIDGE_SERIAL_PORT`
- Service: `python -m app.hardware.lora_bridge` (see `apps/api/app/hardware/lora_bridge.py`)
- Validation: `GET /api/v1/hardware/gateway-status`, Cyberdeck `/cyberdeck` mesh RSSI/SNR

### Field test protocol (high level)

1. **Bench:** flash → PTT serial → bridge connected → Cyberdeck text dispatch  
2. **RF short range:** Codec2 **1200 bit/s** intelligibility + latency budget  
3. **Field LOS:** RSSI/SNR vs distance via Cyberdeck mesh panel + API `.../cyberdeck/mesh`

### Notion

Task **[P1] Real Hardware Flashing Guide & LoRa PTT Field Test Protocol (ESP32-S3 & Orange Pi)** → **Done** (synced 2026-09-20).

### Verification

| Check | Result |
| --- | --- |
| Guide completeness | `docs/hardware/field_test_guide.md` — structured sections 1–8 + scripts |
| Software regression | `pytest` **204**, `flutter test` **133**, `npm run build` **Pass** (unchanged) |

---

## MILESTONE 10 — Production Docker Compose Hardening & Colocation Deployment

**Status:** Done (2026-09-20)

### Scope

Production-grade Docker Compose stack with reverse proxy TLS/WSS, persistent data services, and colocation deployment runbook (Ubuntu + Tailscale / Cloudflare Tunnel).

### Artifacts

| Path | Purpose |
| --- | --- |
| [`docker-compose.prod.yml`](docker-compose.prod.yml) | `db`, `cache`, `mqtt`, `api`, `web`, `dashboard`, `proxy` |
| [`apps/api/Dockerfile.prod`](apps/api/Dockerfile.prod) | Multi-stage API + Gunicorn/Uvicorn workers; mounts `packages/shared` |
| [`apps/web/Dockerfile.prod`](apps/web/Dockerfile.prod) | Next.js standalone production image |
| [`apps/dashboard/Dockerfile.prod`](apps/dashboard/Dockerfile.prod) | Flutter Web `/dashboard/` + `API_BASE_URL` dart-define |
| [`nginx/nginx.conf`](nginx/nginx.conf) | `/api`, `/`, `/dashboard/`, `/ws/mqtt`, rate limits, TLS block |
| [`nginx/snippets/security_headers.conf`](nginx/snippets/security_headers.conf) | HSTS, CSP, X-Frame-Options |
| [`.env.production.example`](.env.production.example) | DB, Redis, JWT, MQTT, tunnel/Tailscale placeholders |
| [`scripts/deploy_prod.sh`](scripts/deploy_prod.sh) | Bootstrap MQTT passwords + self-signed TLS, build, migrate, health |
| [`docs/deployment/production_setup_guide.md`](docs/deployment/production_setup_guide.md) | AMD EPYC / Ubuntu colocation guide |

### Notion

Task **[P1] Production Docker Compose Hardening & Colocation Deployment Setup** → **Done** (synced 2026-09-20).

### Verification

| Check | Command / note |
| --- | --- |
| Compose valid | `docker compose -f docker-compose.prod.yml config` |
| Backend | `pytest` (see re-verify section) |
| Flutter | `flutter test` |
| Web | `npm run build` |

---

## MILESTONE 11 — Real Authentication Flow & Route RBAC Guard

**Status:** Done (2026-09-20)

### Backend API

| Method | Endpoint | Notes |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | Default tenant slug/name from email when omitted |
| `POST` | `/api/v1/auth/login` | JWT access + refresh + `role` / `user_id` / `email` |
| `POST` | `/api/v1/auth/refresh` | Rotating refresh token (Redis-backed) |
| `GET` | `/api/v1/auth/me` | Profile + RBAC `permissions[]` |

Legacy aliases remain at `/auth/*`. Tests: `apps/api/tests/test_auth_v1_api.py`.

### Next.js (`apps/web`)

| Path | Purpose |
| --- | --- |
| `app/login/page.tsx`, `app/register/page.tsx` | Glassmorphic Tuya OS auth UI |
| `middleware.ts` | Cookie JWT guard for `/dashboard`, `/cyberdeck` → redirect `/login` |
| `lib/auth/*` | API client, session cookies, token expiry check |
| `components/marketing/PublicLandingPage.tsx` | Sign In / Launch App → `/login`; trial → `/register` |

### Flutter (`apps/dashboard`)

| Area | Path |
| --- | --- |
| Secure JWT storage | `lib/core/auth/token_storage.dart` (`flutter_secure_storage`) |
| Auto-login bootstrap | `lib/main.dart`, `auth_provider.dart` (`isLoading` gate) |
| Login screen + router guard | `login_screen.dart`, `app_router.dart` |
| Profile + permissions | `/api/v1/auth/me` via `auth_repository` + `permissions_repository` |

### Notion

Task **[P1] End-to-End Real Authentication Flow & Route RBAC Guard Integration** → **Done**.

### Verification

| Suite | Result |
| --- | --- |
| `npm run build` | Pass (`/login`, `/register`, middleware) |
| `flutter test` | Pass after login widget test override |
| `pytest` | Run `docker compose run --rm api pytest -q` when Postgres credentials match compose |

---

## MILESTONE 12 — Master Platform Restructuring (Segments & Dynamic Mobile/Web HQ)

**Status:** Done (2026-09-23)

### Product segments (Master Roadmap)

| Segment | Surface |
| --- | --- |
| B2C | Smart Home domain preset |
| B2B Enterprise | Multi-tenant operator shell |
| B2B White Label | Web HQ tenant branding placeholder |
| API Developer | Developer keys / webhooks placeholder |

### Flutter mobile (`apps/dashboard`, doc: `apps/mobile/README.md`)

| Component | Path |
| --- | --- |
| Domain onboarding (5 domains + enterprise preset) | `lib/features/onboarding/screens/domain_onboarding_screen.dart` |
| Secure domain persistence | `lib/features/onboarding/data/domain_storage.dart` |
| Contextual nav engine | `domain_navigation_profile.dart` → `TacticalShell` / `AppSidebar` / `HomeScreen` |
| Router gate | `/onboarding` after login when no domain selected |

### Web HQ Studio (`apps/web`)

| Route | Purpose |
| --- | --- |
| `/settings/tenant-branding` | White-label configurator placeholder |
| `/developer/api-keys` | API keys & webhooks manager placeholder |
| `/studio/firmware` | Low-code firmware studio placeholder |
| `/studio/missions` | Mission / logistics studio placeholder |
| `components/hq/HqStudioShell.tsx` | Shared HQ chrome + nav |

### Notion

- **[P0] Master Roadmap & Architecture Definition…** → Done  
- **[P1] Flutter Mobile Dynamic Domain Onboarding…** → Done  
- **[P1] Next.js Web HQ Studio…** → Done  

### Verification

| Suite | Result |
| --- | --- |
| `flutter test` | Domain onboarding + nav profile tests |
| `npm run build` | HQ + studio routes |

---

## MILESTONE 13 — Web HQ Core & Warm Cream UI Redesign

**Status:** Done (2026-09-23)

### Design system (`apps/web`)

| Token | Value |
| --- | --- |
| Page background | `#F9F8F6` (`cream-page`) |
| Cards | `#FFFFFF`, border `#ECECE8`, `shadow-card` |
| Primary text | `#1A1A1A` |
| Secondary text | `#666666` |
| Accents | Emerald / Indigo / Cobalt / Amber / Violet pastel chips |

Files: `tailwind.config.ts`, `app/globals.css`, `components/ui/CreamCard.tsx`.

### Web HQ dashboard

| Component | Path |
| --- | --- |
| HQ shell | `components/hq/HqDashboard.tsx` |
| Header (tenant, domain, profile, notifications) | `components/hq/HqHeaderBar.tsx` |
| Route | `app/dashboard/page.tsx` |

### Studio & developer (cream theme)

| Route | Content |
| --- | --- |
| `/studio/firmware` | ESP32-S3 / Orange Pi, pin map, Codec2, LoRa toggles |
| `/studio/missions` | GIS waypoint planner placeholder |
| `/developer/api-keys` | Keys table, webhooks, rate-limit cards |
| `/settings/tenant-branding` | Logo upload, domain, color picker preview |

### Notion

**[P0] Web HQ Dashboard Refactoring & Warm Cream Modern Clean UI Redesign** → Done.

### Verification

| Suite | Result |
| --- | --- |
| `npm run build` | Pass |
| `flutter test` | Unchanged (no Flutter diff) |

---

## MILESTONE 14 — Web HQ Left Sidebar Refactor

**Status:** Done (2026-09-23)

### Layout

| Piece | Path |
| --- | --- |
| Route group `(hq)` layout | `app/(hq)/layout.tsx` |
| Studio segment layout | `app/(hq)/studio/layout.tsx` |
| Collapsible sidebar | `components/hq/HqSidebar.tsx` |
| Compact header (breadcrumb, domain, health, alerts) | `components/hq/HqContentHeader.tsx` |
| Shell + context | `components/hq/HqAppShell.tsx`, `lib/hq/hq-shell-context.tsx` |
| Nav config | `lib/hq/nav-config.ts` |

### Routes under sidebar

`/dashboard`, `/control-center` (→ dashboard), `/studio/*`, `/developer/*`, `/settings/*`

### Notion

**[P1] Web HQ Left Sidebar Refactoring & Layout Polish** → Done.

### Verification

`npm run build` — pass.

---

## MILESTONE 16 — Automation Studio Visual Node Engine (React Flow)

**Status:** In progress (2026-09-29)

| Piece | Path |
| --- | --- |
| React Flow canvas | `components/studio/automation/AutomationStudioCanvas.tsx` |
| Custom nodes | `components/studio/automation/AutomationFlowNode.tsx` |
| Property panel | `components/studio/automation/AutomationPropertyPanel.tsx` |
| Workflow model / JSON | `lib/studio/automation-flow.ts` |
| Route | `app/(hq)/studio/automation/page.tsx` |

**Notion:** [P0] Automation Studio Visual Node-Based Editor → **In progress**  
**Backlog:** P1 Tactical Control Center Real-Time Widgets, P2 Flutter Telemetry & BLE Sync → **Not started**

**Verification:** `cd apps/web && npm run build` — pass.

---

## MILESTONE 15 — Automation Studio, Control Center & Nav Performance

**Status:** Done (2026-09-23)

### Features

| Area | Path / component |
| --- | --- |
| Automation Studio (drag-and-drop flow) | `app/(hq)/studio/automation/page.tsx`, `components/studio/AutomationStudioBuilder.tsx` |
| Tactical Control Center (no dashboard redirect) | `app/(hq)/control-center/page.tsx`, `components/hq/HqControlCenter.tsx` |
| Sidebar Studio group + Workflow icon | `lib/hq/nav-config.ts`, `components/hq/HqSidebar.tsx` (`prefetch` on links) |
| Route skeleton loaders | `app/(hq)/*/loading.tsx` (studio, dashboard, control-center, developer, settings) |
| Studio Suspense meta strip | `lib/hq/studio-meta.ts`, `components/studio/StudioMetaStrip.tsx`, `StudioRouteShell.tsx` |

### Routes

- `/studio/automation` — Trigger → Condition → Action canvas (Biofloc sample flow)
- `/control-center` — E-STOP, manual relays, multi-device PWM, stream monitor
- `/dashboard` — high-level metrics & activity only

### Notion

**[P1] Add Automation Studio & Navigation Performance Optimization** → Done.

### Verification

`cd apps/web && npm run build` — pass.

---

## MILESTONE 17 — Field Execution Flutter App & Hardware Command Bridge

**Status:** ✅ Complete  
**Theme:** Mobile field ops — secure login, device discovery, relay HUD, offline telemetry queue, API → Redis/MQTT command bridge.

### Notion backlog

| Task | Status |
| --- | --- |
| [P1] Tactical Control Center Real-Time Widgets | **Done** |
| [P2] Flutter Mobile App Telemetry & BLE Sync | **Done** |

### Backend API (`apps/api`)

| Method | Endpoint | Notes |
| --- | --- | --- |
| `POST` | `/api/v1/devices/{device_id}/commands` | Operator JWT — `RELAY_ON`, `RELAY_OFF`, `SET_ACTUATOR`; Redis fan-out + `hardware:mqtt:commands` bridge |
| `POST` | `/api/v1/telemetry/bulk` | Operator JWT — offline queue flush from field app |
| `POST` | `/api/v1/telemetry` | Device Basic auth — single sensor ingest |

**Key modules:** `apps/api/app/commands/service.py`, `apps/api/app/commands/events.py`, `apps/api/app/devices/router.py`

### Flutter field app (`apps/mobile/field_app`)

| Area | Path |
| --- | --- |
| Theme | `lib/core/theme/field_theme.dart` |
| Auth + secure storage | `lib/features/auth/`, `lib/core/storage/token_storage.dart` |
| Scanner (`flutter_blue_plus`) | `lib/features/scanner/` |
| BLE GATT relay | `lib/core/ble/ble_relay_service.dart` |
| Bulk sync worker | `lib/core/sync/telemetry_sync_service.dart` |
| Tactical HUD + offline SQLite | `lib/features/hud/`, `lib/core/storage/offline_telemetry_store.dart` |
| REST client | `lib/core/api/field_api_client.dart` |

### Verification (2026-09-29)

```bash
docker compose run --rm api pytest tests/test_commands.py -q
cd apps/mobile/field_app && flutter pub get && flutter analyze && flutter test
```

**Docs:** `apps/mobile/field_app/README.md`, `apps/mobile/README.md`

---

## MILESTONE 18 — Hardware Pairing & Local mDNS Discovery

**Status:** ✅ Complete  
**Theme:** Field scanner binds BLE MAC / slug / mDNS host to PostgreSQL device UUID; native LAN service discovery without internet.

### Flutter field app (`apps/mobile/field_app`)

| Area | Path |
| --- | --- |
| Fleet pairing registry | `lib/core/pairing/device_pairing_registry.dart` |
| mDNS discovery | `lib/core/discovery/mdns_discovery_service.dart` (`_next-iot._tcp.local`) |
| Scanner orchestration | `lib/features/scanner/scanner_service.dart` |
| Fleet list API | `FieldApiClient.listDevices()` → `GET /api/v1/devices` |

**Device metadata keys for auto-pair:** `ble_mac`, `field_slug`, `mdns_name`, `lan_host` (and aliases documented in registry).

### Verification (2026-09-29)

```bash
cd apps/mobile/field_app && flutter analyze && flutter test
```

---

## P0 Step 0 — Engineering Guardrails (Strict Typing, CI Checks)

**Status:** In progress (Senior Architect verification pending)  
**Notion task:** [P0] Step 0 — Engineering Guardrails (Strict Typing, No Any, CI Checks)

### Implementation notes

| Item | Detail |
| --- | --- |
| Permanent rules | `.cursorrules` (root) |
| Unified verify | `scripts/check-all.ps1` |
| API tooling | `apps/api/pyproject.toml`, `requirements.txt` (+ ruff, mypy) |
| API typing | `app/types/json_types.py`; `Any` → `JsonValue` across `app/**` |
| Web | `tsconfig.json`, `eslint.config.mjs`, `npm run typecheck` |
| Mobile | `analysis_options.yaml` strict; `lib/core/models/field_api_models.dart` |
| Debt register | `docs/TECH_DEBT.md` |
| Project resume | `docs/PROJECT_RESUME.md` |

### Violation audit (initial → after Step 0)

| Area | Initial | After |
| --- | ---: | ---: |
| API `Any` in `app/` | ~220 | 0 |
| Web forbidden TS patterns (source) | 2 | 0 |
| Flutter `dynamic` in `lib/` | 4 | 0 |
| ruff (`app/`) | 317 | 317 (ANN/import — see TECH_DEBT) |
| mypy strict | — | 632 errors (111 files) |
| pytest | — | 211+ pass (Redis test DB 15, gateway isolation) |

**Menu & Feature Map (impacted):** Engineering Guardrails (strict typing, check-all).

**Latest (2026-09-30):** Redis pytest isolation (`REDIS_URL_TEST`, guarded `FLUSHDB`), ruff E402 allowlist for `tests/conftest.py`, `scripts/check-all.ps1` green target.

**Do not set Notion Status → Done** until Senior Architect approves.

---

## Appendix — Additional platform work (post-milestone)

Delivered alongside enterprise milestones; tracked in backlog / canvas notes.

| Area | Summary | Key paths |
| --- | --- | --- |
| Smart Home domain | `SMART_HOME` category, migration `010`, relay/HVAC/PIR metrics | `apps/api/app/telemetry/smart_home_metrics.py`, Flutter device filters |
| Bento dashboard layout | 70/30 asymmetric grid, compact tiles | `apps/dashboard/lib/features/dashboard/widgets/asymmetric_bento_dashboard_layout.dart` |
| Alert Engine UI | `/alerts`, rules table, notification channels, live feed | `apps/dashboard/lib/features/alerts/` |
| Tactical map & P6 hardware | Signal heatmap, anomaly detection, offline tiles, LoRa | `apps/api/app/telemetry/signal_heatmap.py`, `anomaly_detector.py`; Flutter `features/map/` |
| Canvas bugfixes | Multi-chain edges, deselect, disconnect UI | `NOTION_TASKS_CANVAS_BUGS.md` |

---

## How to re-verify locally

```bash
# Backend
docker compose run --rm api pytest -q

# Flutter operator dashboard
cd apps/dashboard && flutter test

# Marketing web
cd apps/web && npm run build
```

---

## Related files

- `NOTION_TASKS_BACKLOG.md` — task checklist M1–M15 + future roadmap
- `NOTION_TASKS_CANVAS_BUGS.md` — Automation Studio canvas interaction notes

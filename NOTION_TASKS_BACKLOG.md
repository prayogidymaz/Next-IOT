# Next-IOT Development Tasks — Backlog Sync

**Last updated:** 2026-09-30 (UTC+7)  
**Master changelog:** `NOTION_UPDATE.md`  
**Notion target:** database **Next-IOT Development Tasks**

---

## IN PROGRESS — [P0] Step 0 — Engineering Guardrails (Strict Typing, CI Checks)

| Field | Value |
| --- | --- |
| **Status** | **In progress** (awaiting Senior Architect) |
| **Scope** | `.cursorrules`, ruff/mypy/pytest, web typecheck/eslint, flutter strict analyze, `scripts/check-all.ps1` |

### Checklist

- [x] `.cursorrules` + `docs/PROJECT_RESUME.md` + `docs/TECH_DEBT.md`
- [x] API: `pyproject.toml`, eliminate `typing.Any` in `app/**`
- [x] Web: strict TS + `typecheck` script; remove `as unknown as`
- [x] Mobile: strict analyzer + typed API models
- [ ] `scripts/check-all.ps1` fully green (ruff ANN + mypy strict + pytest lora)

---

## IN PROGRESS — [P0] Automation Studio Visual Node-Based Editor

| Field | Value |
| --- | --- |
| **Status** | **In progress** |
| **Scope** | Web HQ `/studio/automation` — React Flow canvas, palette, property panel, JSON I/O |
| **Notion** | [P0 Automation Studio Visual Node-Based Editor](https://app.notion.com/p/P0-Automation-Studio-Visual-Node-Based-Editor-3eaed0e404a781d09ad6ce82b75d17c3) |

### Checklist

- [x] `@xyflow/react` installed in `apps/web`
- [x] Custom Trigger / Condition / Action nodes (Warm Cream theme)
- [x] Palette drag-drop, pan/zoom, grid background, minimap
- [x] Property configurator panel (sensor, threshold, relay, notification)
- [x] Save / Export / Import / Deploy action bar
- [ ] Wire Deploy to `/api/v1/automation/pipelines` (backend follow-up)

---

## DONE — [P1] Tactical Control Center Real-Time Widgets

| Field | Value |
| --- | --- |
| **Status** | **Done** |
| **Scope** | `/control-center` command grid, Recharts live stream, WS `/api/v1/ws/telemetry` |
| **Notion** | [P1 Tactical Control Center Real-Time Widgets](https://app.notion.com/p/P1-Tactical-Control-Center-Real-Time-Widgets-3eaed0e404a7819b9316fad3589697d9) |

### Checklist

- [x] Domain filter bar + global E-STOP banner
- [x] Relay toggles, live telemetry charts (Recharts), fleet map preview, audit feed
- [x] `lib/api/websocket.ts` + Redis-backed WS fan-out on API
- [x] Relay dispatch path via `POST /api/v1/devices/{id}/commands` (Web HQ + API)

---

## DONE — [P2] Flutter Mobile App Telemetry & BLE Sync

| Field | Value |
| --- | --- |
| **Status** | **Done** |
| **Scope** | `apps/mobile/field_app` — auth, BLE/mDNS scanner, UUID pairing, tactical HUD, SQLite bulk sync |
| **Notion** | [P2 Flutter Mobile App Telemetry & BLE Sync](https://app.notion.com/p/P2-Flutter-Mobile-App-Telemetry-BLE-Sync-3eaed0e404a781ef8f41c1f6dfba200c) |

### Checklist

- [x] Warm Cream theme + secure token storage
- [x] Login screen + Riverpod auth + go_router shell
- [x] Device scanner screen (BLE/Wi-Fi discovery facade)
- [x] Tactical HUD — relay switch, live metrics, offline SQLite queue
- [x] Native BLE (`flutter_blue_plus`) scan + GATT relay write fallback
- [x] Offline flush → `POST /api/v1/telemetry/bulk` (auto on connectivity + manual sync)
- [x] mDNS LAN discovery (`multicast_dns`) + fleet UUID pairing (`ble_mac` / `field_slug` metadata)

---

## Verification snapshot (2026-09-29)

| Suite | Result |
| --- | --- |
| `docker compose run --rm api pytest tests/test_commands.py -q` | **5 passed** (incl. RELAY → MQTT bridge) |
| `cd apps/mobile/field_app && flutter analyze && flutter test` | **Pass** (analyze clean, pairing + widget tests) |
| `cd apps/dashboard && flutter test` | Operator dashboard |
| `cd apps/web && npm run build` | Web HQ |

---

## DONE — [P1] Real Hardware Flashing Guide & LoRa PTT Field Test Protocol (ESP32-S3 & Orange Pi)

| Field | Value |
| --- | --- |
| **Status** | **[x] COMPLETED / DONE** |
| **Module** | P1 — Field Hardware / Option 3 |
| **Scope** | Wiring pinouts, PlatformIO + esptool, Orange Pi 5 Pro LoRa bridge, field validation protocol |

### Checklist

- [x] `docs/hardware/field_test_guide.md` (INMP441, MAX98357A, SX1262, PTT)
- [x] PlatformIO reference + esptool flash commands (Windows + Linux)
- [x] Orange Pi serial permissions + `lora_bridge` env setup
- [x] Codec2 1200 latency & audio QA protocol
- [x] RSSI/SNR validation via Cyberdeck UI + API mesh endpoint
- [x] Test scripts under `docs/hardware/scripts/`
- [x] Notion task synced → **Done**

**Key paths:** `docs/hardware/field_test_guide.md`, `docs/hardware/scripts/`, `docs/firmware/lora-ptt/`

**Notion:** [P1 Real Hardware Flashing Guide](https://app.notion.com/p/P1-Real-Hardware-Flashing-Guide-LoRa-PTT-Field-Test-Protocol-ESP32-S3-Orange-Pi-3e0ed0e404a781538289f0cb7afe820b)

---

## DONE — [P1] Cyberdeck Tactical UI Console & LoRa PTT Voice Bridge

| Field | Value |
| --- | --- |
| **Status** | **[x] COMPLETED / DONE** |
| **Module** | P1 — Hardware Ops / Cyberdeck |
| **Scope** | Flutter `/cyberdeck`, web `/cyberdeck`, LoRa PTT APIs, Codec2 firmware docs |

### Checklist

- [x] LoRa PTT voice UI (hold-to-transmit + waveform + CH 1–8)
- [x] Node mesh tracker (Cyberdeck units + ESP32-S3 smartwatch, RSSI/SNR/battery)
- [x] Text & emergency beacon dispatcher (encrypted LoRa path via API)
- [x] Hardware health monitor (CPU/RAM/battery/uptime)
- [x] Backend `/api/v1/hardware/cyberdeck/*`
- [x] Firmware template `docs/firmware/lora-ptt/`
- [x] Notion task synced → **Done**

**Key paths:** `apps/dashboard/lib/features/cyberdeck/`, `apps/web/components/cyberdeck/`, `apps/api/app/hardware/cyberdeck_ptt.py`

---

## Milestone task checklist (1 → 7)

All items below are **completed** unless noted.

### MILESTONE 1 — OTA Firmware Management & Dynamic Rollouts

- [x] **COMPLETED** — `POST /api/v1/devices/bulk-import` (JSON + CSV multipart, tenant batch limits)
- [x] **COMPLETED** — OTA releases CRUD + publish + rollout tracking (`/api/v1/ota/*`)
- [x] **COMPLETED** — Device OTA check endpoint (`GET /api/v1/ota/check`, Basic auth)
- [x] **COMPLETED** — Migration `011_firmware_releases_ota`
- [x] **COMPLETED** — Flutter OTA Firmware Manager (`/devices/ota`)
- [x] **COMPLETED** — Flutter bulk register devices panel + template dropzone
- [x] **COMPLETED** — Tests: `test_fleet_bulk_ota.py` + device UI tests (suite **202 / 132**)

**Key paths:** `apps/api/app/ota/`, `apps/api/app/devices/bulk_import.py`, `apps/dashboard/lib/features/devices/screens/ota_firmware_screen.dart`

---

### MILESTONE 2 — Multi-Tenancy Architecture & Fine-Grained RBAC UI Guard

- [x] **COMPLETED** — Tenant APIs (`GET/POST /api/v1/tenants`, switch, members)
- [x] **COMPLETED** — Permissions API (`GET /api/v1/users/me/permissions`)
- [x] **COMPLETED** — RBAC roles + middleware (`super_admin` … `viewer`)
- [x] **COMPLETED** — Migration `012_tenant_memberships`
- [x] **COMPLETED** — Flutter `TenantSwitcher` + session tenant sync
- [x] **COMPLETED** — Flutter `PermissionGuard` on sensitive actions (register, OTA, rules, automation)
- [x] **COMPLETED** — Settings: organization & members UI
- [x] **COMPLETED** — Tests: `test_tenant_rbac_api.py` (suite **202 / 132**)

**Key paths:** `apps/api/app/tenants/`, `apps/api/app/auth/permissions.py`, `apps/dashboard/lib/core/widgets/tenant_switcher.dart`

---

### MILESTONE 3 — Automation Studio (Visual Drag & Drop JSON Pipeline Engine)

- [x] **COMPLETED** — Automation pipeline CRUD API (`/api/v1/automation/pipelines`)
- [x] **COMPLETED** — Dry-run + test-run endpoints (no hardware side effects on dry-run)
- [x] **COMPLETED** — Rules JSON import / export / validate (`/api/v1/rules/import`, `export`, `validate`)
- [x] **COMPLETED** — Pipeline interpreter + validation (`pipeline_interpreter.py`, `pipeline_validation.py`)
- [x] **COMPLETED** — Migration `009_automation_pipelines`
- [x] **COMPLETED** — Flutter Automation Studio canvas (`/studio`) — nodes, ports, edges
- [x] **COMPLETED** — 2-step click port wiring + edge disconnect + canvas deselect
- [x] **COMPLETED** — Studio JSON import/export dialog
- [x] **COMPLETED** — Tests: automation pipeline API + interpreter unit tests (suite **202 / 132**)

**Key paths:** `apps/api/app/automation/`, `apps/dashboard/lib/features/automation/`, `apps/dashboard/lib/features/studio/`

---

### MILESTONE 4 — Time-Series Data Analytics, Aggregation, & CSV Export Pipeline

- [x] **COMPLETED** — `GET /api/v1/telemetry/analytics` (interval buckets + per-metric stats)
- [x] **COMPLETED** — `GET /api/v1/telemetry/export?format=csv` (streaming export)
- [x] **COMPLETED** — Timeseries aggregation modules (`analytics.py`, `timeseries.py`, `export_service.py`)
- [x] **COMPLETED** — Flutter `/analytics` screen + multi-metric charts
- [x] **COMPLETED** — Flutter telemetry export dialog + progress UX
- [x] **COMPLETED** — Tests: telemetry analytics/export API + widget tests (suite **202 / 132**)

**Key paths:** `apps/api/app/telemetry/`, `apps/dashboard/lib/features/telemetry/screens/telemetry_analytics_screen.dart`

---

### MILESTONE 5 — Enterprise Operations, System Health, & Audit Logging

- [x] **COMPLETED** — Audit log model + middleware (`audit_logs`, migration `013`)
- [x] **COMPLETED** — `GET /api/v1/audit-logs` + CSV export
- [x] **COMPLETED** — `GET /api/v1/system/health` (DB, Redis, broker/MQTT standby, CPU/RAM)
- [x] **COMPLETED** — Flutter `/audit` viewer (filters + export)
- [x] **COMPLETED** — Flutter system health indicator in shell / status bar
- [x] **COMPLETED** — RBAC `audit.read` enforcement
- [x] **COMPLETED** — Tests: `test_audit_logs_api.py`, `test_system_health_api.py` (suite **202 / 132**)

**Key paths:** `apps/api/app/audit/`, `apps/api/app/system/`, `apps/dashboard/lib/features/audit/`

---

### MILESTONE 6 — Tuya OS UI Component (`TuyaSmartDashboard`)

- [x] **COMPLETED** — Next.js app scaffold `apps/web` (Tailwind + Framer Motion + Lucide)
- [x] **COMPLETED** — `TuyaSmartDashboard.tsx` — glassmorphism cards, spring toggles, sliders
- [x] **COMPLETED** — Dark / light mode + staggered entrance animations
- [x] **COMPLETED** — Smart device demos (AC, lights, power, lock, humidity, usage)
- [x] **COMPLETED** — `npm run build` verification

**Key paths:** `apps/web/components/TuyaSmartDashboard.tsx`, `apps/web/package.json`

---

### MILESTONE 7 — Public Marketing Landing Page & Route Restructuring

- [x] **COMPLETED** — Route `/` → public marketing landing (`PublicLandingPage`)
- [x] **COMPLETED** — Route `/dashboard` → Control Center (`TuyaSmartDashboard`)
- [x] **COMPLETED** — Navbar (Next-IoT, Platform, Solutions, Automation, Pricing, Sign In, Launch App)
- [x] **COMPLETED** — Hero + CTAs (Start Free Trial, View Live Demo)
- [x] **COMPLETED** — Interactive showcase (`DashboardShowcase` + embedded dashboard)
- [x] **COMPLETED** — Marketing bento — 5 modules (`MarketingFeaturesBento`)
- [x] **COMPLETED** — Enterprise metrics strip + footer
- [x] **COMPLETED** — `TuyaSmartDashboard` `embedded` mode for landing frame
- [x] **COMPLETED** — `npm run build` — `/` + `/dashboard` static routes

**Key paths:** `apps/web/app/page.tsx`, `apps/web/app/dashboard/page.tsx`, `apps/web/components/marketing/`

**Notion log entry:** `NOTION_UPDATE.md` → *MILESTONE 7 — Public Marketing Landing Page & Route Restructuring*

---

## Additional completed work (outside M1–7 numbering)

| Task | Status |
| --- | --- |
| Smart Home & Building domain (migration `010`, category filter) | [x] **DONE** |
| Compact asymmetric Bento dashboard layout (Flutter home) | [x] **DONE** |
| UI/UX Bento design system (`tactical_theme`, smart home tiles) | [x] **DONE** |
| Alert & Notification Engine UI (`/alerts`) | [x] **DONE** |
| Automation Studio canvas bugfixes (multi-chain, disconnect) | [x] **DONE** |
| P6: Signal heatmap, anomaly detection, LoRa/tiles (tactical stack) | [x] **DONE** (see `NOTION_UPDATE.md` appendix) |

---

## NEXT ROADMAP OPTIONS (future backlog)

Items **not started** — candidates for next sprint / Notion **Not started** tasks.

### MILESTONE 10 — Production Docker Compose Hardening

- [x] **COMPLETED** — `docker-compose.prod.yml` (api, web, dashboard, db, cache, mqtt, proxy)
- [x] **COMPLETED** — Multi-stage `Dockerfile.prod` for API / web / dashboard
- [x] **COMPLETED** — Nginx reverse proxy (TLS, WSS `/ws/mqtt`, rate limits, security headers)
- [x] **COMPLETED** — `.env.production.example` + `scripts/deploy_prod.sh`
- [x] **COMPLETED** — `docs/deployment/production_setup_guide.md` (colocation + Tailscale / Cloudflare)
- [ ] CI pipeline: build → test → push → staged deploy *(future)*
- [ ] Observability: structured logs, metrics export, backup/restore runbook *(future)*

**Notion log entry:** `NOTION_UPDATE.md` → *MILESTONE 10 — Production Docker Compose Hardening*

### 1. Docker Production Deployment (follow-ups)

- [ ] Registry tags + staged rollout automation
- [ ] PostgreSQL backup/restore runbook in CI

### MILESTONE 14 — Web HQ Left Sidebar Refactor

- [x] **COMPLETED** — Collapsible Warm Cream left sidebar + tenant switcher
- [x] **COMPLETED** — Compact header (breadcrumb, domain pills, health, notifications)
- [x] **COMPLETED** — `(hq)` route group wraps dashboard, studio, developer, settings
- [x] **COMPLETED** — Removed legacy top nav `HqStudioShell`

**Notion log entry:** `NOTION_UPDATE.md` → *MILESTONE 14 — Web HQ Left Sidebar Refactor*

### MILESTONE 15 — Automation Studio, Control Center & Nav Performance

- [x] **COMPLETED** — `/studio/automation` visual drag-and-drop flow builder (Trigger → Condition → Action)
- [x] **COMPLETED** — Sidebar **Automation Studio** (Workflow icon) under Studio group
- [x] **COMPLETED** — `/control-center` tactical fleet UI (E-STOP, relays, PWM, stream monitor) — no dashboard redirect
- [x] **COMPLETED** — `loading.tsx` skeletons (studio, dashboard, control-center, developer, settings)
- [x] **COMPLETED** — Sidebar `prefetch` + studio Suspense meta (`StudioMetaStrip`, `useOptimistic` on flow reorder)

**Notion log entry:** `NOTION_UPDATE.md` → *MILESTONE 15 — Automation Studio, Control Center & Nav Performance*

### MILESTONE 13 — Web HQ Core & Warm Cream UI Redesign

- [x] **COMPLETED** — Tailwind + globals Warm Cream design tokens
- [x] **COMPLETED** — HQ dashboard (tenant switcher, domain selector, metrics, activity feed)
- [x] **COMPLETED** — Studio / developer / white-label routes with cream UI
- [x] **COMPLETED** — Auth + marketing landing aligned to cream system

**Notion log entry:** `NOTION_UPDATE.md` → *MILESTONE 13 — Web HQ Core & Warm Cream UI Redesign*

### MILESTONE 12 — Master Platform Restructuring

- [x] **COMPLETED** — Master roadmap segments (B2C, B2B Enterprise, White Label, API Developer)
- [x] **COMPLETED** — Flutter domain onboarding + contextual navigation engine
- [x] **COMPLETED** — Web HQ routes (tenant branding, API keys, firmware/mission studio placeholders)
- [x] **COMPLETED** — `apps/mobile/README.md` mobile shell pointer

**Notion log entry:** `NOTION_UPDATE.md` → *MILESTONE 12 — Master Platform Restructuring*

### MILESTONE 11 — Real Authentication Flow & Route RBAC Guard

- [x] **COMPLETED** — `/api/v1/auth/*` (register w/ default tenant, login+role, refresh, `/me`+permissions)
- [x] **COMPLETED** — Next.js `/login`, `/register`, middleware guard (`/dashboard`, `/cyberdeck`)
- [x] **COMPLETED** — Landing CTAs → `/login` & `/register`
- [x] **COMPLETED** — Flutter Riverpod auth + `flutter_secure_storage` + auto-login bootstrap

**Notion log entry:** `NOTION_UPDATE.md` → *MILESTONE 11 — Real Authentication Flow & Route RBAC Guard*

### 2. Real Auth / OAuth2 Flow (follow-ups)

- [ ] OAuth2 / OIDC provider integration (e.g. Google Workspace, Azure AD) alongside existing JWT
- [ ] Refresh token rotation hardening, PKCE for SPA
- [ ] Map IdP groups → Next-IoT RBAC roles (`tenant_admin`, `operator`, `viewer`)

### 3. Edge Hardware SDK & Reference Firmware

- [ ] Published SDK package for device telemetry ingest + OTA check client
- [ ] ESP32 / LoRa reference templates aligned with `lora_bridge` + encryption (`LORA_ENCRYPTION_KEY`)
- [ ] Device provisioning UX: QR / claim codes, certificate pinning option
- [ ] Field diagnostics: offline buffer, batch upload, signal quality metrics

---

## Quick reference — verify before Notion sync

```bash
docker compose run --rm api pytest -q
cd apps/dashboard && flutter test
cd apps/web && npm run build
```

---

## Related documentation

| File | Purpose |
| --- | --- |
| `NOTION_UPDATE.md` | Detailed milestone changelog (API + file paths + verification) |
| `NOTION_TASKS_CANVAS_BUGS.md` | Automation Studio canvas interaction audit |
| `apps/web/README.md` | Web routes `/` vs `/dashboard` |

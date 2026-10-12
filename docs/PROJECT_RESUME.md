# NEXT-IOT ENTERPRISE PLATFORM — Project Resume

Multi-tenant IoT operations platform: **FastAPI** backend, **Next.js 15** Web HQ, **Flutter** field & dashboard clients, **PostgreSQL**, **Redis**, **MQTT** hardware bridge, **Docker Compose** local stack.

## Repository layout

```
Next-IOT/
├── apps/api/                 # FastAPI + Alembic + pytest
├── apps/web/                 # Next.js 15 + React 19 + Tailwind (Web HQ)
├── apps/mobile/field_app/    # Flutter Field Execution
├── apps/dashboard/           # Flutter legacy HQ (FROZEN — see FROZEN.md)
├── scripts/check-all.ps1     # Unified guardrails verification
├── docs/TECH_DEBT.md         # Remaining strict typing / lint debt
└── docker-compose.yml
```

## Platform capabilities (summary)

- **Auth & RBAC:** JWT, multi-tenant isolation, role tiers (`viewer` → `super_admin`).
- **Devices:** Provisioning, heartbeat, commands (`POST /api/v1/devices/{id}/commands`), OTA, bulk import.
- **Telemetry:** Ingest, analytics, export, anomaly detection, bulk field sync (`POST /api/v1/telemetry/bulk`).
- **Automation:** Visual pipelines (Web HQ + API interpreter).
- **Web HQ:** Control Center (WS telemetry), Automation Studio, Cyberdeck.
- **Field app:** BLE + mDNS discovery, UUID pairing, offline SQLite queue, relay REST/BLE.

Default dev API: `http://localhost:8000` · Swagger `/docs`.

## Architecture Decisions

| Decision | Choice |
| --- | --- |
| Web HQ (official) | `apps/web` (Next.js) |
| Mobile (official) | `apps/mobile/field_app` (Flutter) |
| `apps/dashboard` (Flutter) | **FROZEN** — reference for porting to Web HQ only; delete after parity (`apps/dashboard/FROZEN.md`) |
| Quality gate | `scripts/check-all.ps1` + RATCHET baseline (`scripts/ratchet-baseline.txt`) |
| Docker Compose project name | `next-iot` (`docker-compose.yml` top-level `name`) |

## Thing Model (Device Profile)

- **Purpose:** Tenant-scoped device type definitions (telemetry keys, attributes, commands) with versioning (`draft` → `published` → `archived`).
- **API:** `/api/v1/device-profiles` (CRUD + publish / new-version / archive); assign via `PATCH /api/v1/devices/{id}/profile`.
- **Validator:** `app/device_profiles/validator.py` (pure functions; not wired to telemetry ingest until Step 2).
- **Seed:** `smart_switch`, `env_sensor`, `smart_lock` published profiles on demo tenant (`app/seed_device_profiles.py`).

## Device Profiles UI (Web HQ)

- **Routes:** list/create/detail editor; device assign on `/devices/[id]`.
- **Client:** `lib/api/deviceProfiles.ts` + zod schemas (`device-profiles-schemas.ts`); RBAC via `/api/v1/me` role.
- **UX:** Tactical Warm Cream; toast errors (ID); viewer/operator read-only.

## TimescaleDB (telemetry)

- **Why:** `telemetry_readings` time-series at scale; chunking + compression on `recorded_at`.
- **Infra:** Dev Postgres → `timescale/timescaledb:latest-pg16` (PG16-compatible volume); compose sets `shared_preload_libraries=timescaledb` so existing data dirs work without hand-editing `postgresql.conf`.
- **Migration 015:** hypertable on `recorded_at`, compression after 7 days (`device_id, tenant_id` segmentby). `telemetry_anomalies.reading_id` FK dropped at DB level (Timescale cannot enforce id-only FK); ORM column unchanged; FK restored on downgrade to plain Postgres.
- **Retention trade-off:** Global Timescale retention policy at **enterprise max (730d)** as safety net; daily sweep **DELETE** per tenant by `security_tier` (free 7d / pro 90d / enterprise 730d). Per-tenant Timescale retention policies deferred (would need continuous aggregates or manual chunk drops).
- **Step 2B (next):** device-profile validator on ingest — **not wired yet**.

## MQTT Broker & Device Credentials

- **Broker:** EMQX 5.8 (`next-iot-emqx`) with HTTP auth/ACL webhooks to API. Auth/ACL HOCON in **`infra/emqx/cluster-override.conf`** mounted at **`/opt/emqx/data/configs/cluster-override.conf`** (merges with image defaults).
- **EMQX 5 config loading (gotcha):** (1) bundled `emqx.conf`, (2) `EMQX_*` env, (3) **`cluster-override.conf`** merge, (4) runtime Dashboard/API. **`/opt/emqx/etc/emqx.conf.d/` is not loaded.** Replacing **`/opt/emqx/etc/emqx.conf`** overrides **everything**. HOCON **`${VAR}` does not read OS env** (only internal config refs) — dev secret is **literal** in `cluster-override.conf`; keep in sync with API `MQTT_WEBHOOK_SHARED_SECRET`. **Prod TODO:** envsubst entrypoint, init-generated config, or EMQX API. **Step 6+ idea:** push auth/ACL via EMQX HTTP API at API startup instead of static files.
- **Credentials:** `device_credentials` stores MQTT `access_token` (plaintext for EMQX match) + `client_id`; HTTP Basic provisioning unchanged for legacy devices.
- **Ingest (Option A):** EMQX rule → `POST /api/v1/mqtt/ingest/telemetry` reuses `ingest_pipeline.py` (Step 2B). Option B (API MQTT subscriber) deferred for latency work later.
- **QR claim:** `device_claim_tokens` + `POST .../claim` returns one-time token + `mqtt_broker_url`.
- **Dashboard (dev):** http://localhost:18083 (default admin/public — change in prod).

## Thing Model enforcement (ingest)

- **Telemetry bulk (`POST /api/v1/telemetry/bulk`):** If `device.profile_id` is set, metrics are validated against the published spec. Valid keys plus **unknown** keys (not in spec) are persisted; invalid keys are listed in `rejected` with `out_of_range` / `wrong_type` / `enum_not_allowed`. Response stays **HTTP 200** so firmware gets per-key feedback on partial bulk success (422 would drop the whole batch for one bad key). Optional `telemetry_validation_strict_mode` (default off) can return 422 when any key is rejected.
- **Commands (`POST /api/v1/devices/{id}/commands`):** With a profile, commands must exist in the thing model; unknown or invalid params → **400** (single user action, fail fast). Devices **without** a profile keep legacy command validation unchanged.
- **Step 2C (planned):** per-tenant `strict_validation` column.

## Engineering Standards

Permanent rules live in **`.cursorrules`** (root):

1. **Python:** No `Any` / bare `# type: ignore` / untyped `dict`; use `JsonValue`, Pydantic, TypedDict, Protocol; full function annotations.
2. **TypeScript:** No `any`, `as any`, `as unknown as`, ts-ignore; validate API payloads (zod / OpenAPI types).
3. **Dart:** No reckless `dynamic` / unsafe casts; JSON → typed models.
4. **Secrets:** Environment/config only.
5. **Alembic:** Every migration must downgrade cleanly.
6. **New endpoints:** pytest happy path + tenant isolation + unauthorized.
7. **Never weaken lint/type rules** to pass CI — fix code.
8. **Task done:** Run `scripts/check-all.ps1`, update Notion / `NOTION_UPDATE.md`, update this file.

**Tooling:**

| Stack | Config |
| --- | --- |
| API | `apps/api/pyproject.toml` — ruff (E,F,I,B,UP,ANN,PGH), mypy strict + pydantic plugin |
| Web | `tsconfig.json` strict + `npm run typecheck`; `eslint.config.mjs` |
| Mobile | `analysis_options.yaml` strict-casts/inference |

## Changelog

### Step 11 — Smart Agriculture vertical (2026-10-13)

- **Migration 033:** LoRa agriculture schema (8 tables + irrigation logs + battery history); demo farms (kopi, sawit, padi).
- **API:** `app/agriculture/` — farms/plots/sensors/gateways/irrigation/disease/yield/analytics under `/api/agriculture`.
- **Jobs:** Disease predictor (coffee rust, berry borer, rice blast, ganoderma); irrigation scheduler + BMKG forecast cache.
- **Firmware Studio:** `agri_soil_sensor`, `agri_weather_station`, `agri_irrigation_controller`, `agri_npk_sensor`.
- **UI:** `apps/web` agriculture hub; `apps/admin` platform agri stats.
- **Seeder:** `python scripts/seed_agriculture_demo.py` (in API container).
- **Tests:** 40+ in `tests/agriculture/`.

### Step 9C — Placeholder features complete (2026-10-12)

- **Migration 032:** email templates, support tickets, partners/referrals/commissions, backups, impersonation sessions.
- **API:** super-admin routes for templates, tickets, partners, backups, impersonation audit; tenant `/api/v1/support/tickets`.
- **Admin UI:** functional list/editor pages for email templates, support, partners, backup, impersonation audit.
- **Tests:** 51 passing under `tests/super_admin/`.

### Step 9B — Super admin enterprise console (2026-10-12)

- **`apps/admin`:** Six-group sidebar (~22 routes), ⌘K command palette (G T / G B / N A), dense tables, audit/analytics/MQTT/logs/timeline/announcements/promo/settings/feature flags/finance pages; dashboard 6 KPIs + watch list; tenant impersonate (1h JWT); settings 404 fixed.
- **API:** Migration `031` (`platform_announcements`, `promo_codes`, `platform_settings`, `feature_flags`); super-admin endpoints for audit log, analytics, health scores, MQTT proxy, rate limits, log tail, announcements, promo codes, platform settings, feature flags, finance CSV export.
- **Tests:** `tests/super_admin/test_super_admin_console.py` (+16 cases).

### Step 9A — Landing page + admin white theme (2026-10-12)

- **`apps/landing`:** Public pre-sales site on port 3002; pricing, features, use-case pages, OG metadata.
- **`apps/admin`:** Redesign to white/navy enterprise console; `@next-iot/ui` shared package.
- **`apps/web`:** Unchanged (Tactical Warm Cream tenant HQ).

### Step 8C — Admin console split + tenant dashboard (2026-10-12)

- **`apps/admin`:** Standalone super-admin Next.js app (port 3001, dark command-center UI); docker service `admin`.
- **`apps/web`:** Super-admin routes removed (404); tenant dashboard KPIs, live SSE metrics, device heatmap, Cmd+K palette; nav grouped by Command/Fleet/Intelligence/Integration/Settings.
- **API:** SSE `/api/v1/realtime/stream` (tenant JWT, multi-channel, rate-limited).

### Step 8 — Billing + Super Admin (2026-10-11)

- **Subscriptions:** Plans catalog, tenant trial/active lifecycle, usage snapshots, quota enforcement (devices + messages).
- **Payments:** Invoices (PPN 11%), Midtrans/Xendit provider stubs + webhooks; manual billing cycle endpoint.
- **Super Admin:** Platform stats, tenant suspend/trial/plan, revenue MRR, system health, audited actions.
- **Web:** `/billing`, `/pricing` (super-admin UI moved to `apps/admin` in Step 8C).
- **Migrations:** 025–030.

### Step 7 — ESP32 SDK + Firmware Studio (2026-10-11)

- **SDK:** `firmware/next-iot-esp32-sdk` (PlatformIO library — MQTT telemetry, attributes, RPC, OTA).
- **Firmware Studio API:** `/api/v1/firmware-studio` — sensor driver catalog, Jinja2 ZIP generator from Device Profile.
- **OTA:** MQTT `ota/update` publish on firmware release rollout; migration **024** (`device_profile_id`, `release_notes` on releases).
- **Web HQ:** `/firmware-studio` wizard (profile → config → preview → download ZIP).

### Step 6 — Rule engine executor (2026-10-11)

- **Audit:** Legacy `rules` table (004) + `automation_pipelines` (009); Automation Studio canvas at `apps/web/app/(hq)/studio/automation/` (xyflow JSON, separate from DB rules).
- **Executor:** `RuleExecutor` loads enabled rules at startup; triggers telemetry / attribute change / alarm / schedule (cron) / manual; actions: create_alarm, send_command (fire-and-forget RPC), set_attribute, send_notification, log_event, webhook; Jinja2 StrictUndefined; `rule_execution_log`.
- **API:** Extended `/api/v1/rules` (PUT, execute, test, enable/disable, execution-log); CRUD tenant_admin; canvas adapter `app/rules/canvas_adapter.py`.
- **Migration:** `023_rules_executor` (+ nullable `notification_log.alarm_id` for direct sends).

### Step 5 — Alarms + notification gateway (2026-10-11)

- **Alarms:** PostgreSQL lifecycle (`alarms`, `alarm_history`), dedup fingerprint, state machine (ack before resolve), REST `/api/v1/alarms`, validator hook `validation_failed`, maintenance auto-clear.
- **Notifications:** Channels (WA/Telegram/FCM/email/SMS providers), rules + throttle (Redis), `notification_log`, dispatcher on alarm create/escalate.
- **Web HQ:** `/alarms`, `/notification-settings`, sidebar entries.
- **Migrations:** `021_alarms`, `022_notification_channels_rules_log`.

### Step 4 — Device attributes + RPC (2026-10-10)

- **Attributes:** `device_attributes` table with scopes `server` | `shared` | `client`; REST under `/api/v1/devices/{id}/attributes`; client scope via MQTT `.../attributes` (subscriber shared group `nextiot-attributes`); shared updates broadcast on `.../attributes/shared/update` via internal **MQTT publisher**.
- **RPC:** `device_rpc_requests` + sync POST `/api/v1/devices/{id}/rpc` (wait on in-memory event registry); command topic `.../commands/{request_id}/request`, response `.../response` (subscriber group `nextiot-rpc`); rate limit per device/minute.
- **Web HQ:** Device detail — Attributes panel (3 tabs) + Remote Command (RPC) panel.
- **Migrations:** `019_device_attributes`, `020_device_rpc_requests`.

### Step 3C — asyncio-mqtt telemetry subscriber (2026-10-10)

- **Replaces:** EMQX Rule Engine HTTP forward (parked — see `docs/TECH_DEBT.md`).
- **Implementation:** `MqttSubscriberService` connects to EMQX with platform credentials, subscribes `tenants/+/devices/+/telemetry`, parses raw MQTT JSON, calls `persist_telemetry_from_mqtt` (shared with HTTP ingest webhook). **`_handle` commits/rolls back per message** (same transaction ownership as HTTP `get_db`); integration tests verify rows via a **new DB session**.
- **Auth:** `MQTT_SUBSCRIBER_INTERNAL_*` env; EMQX HTTP auth/ACL allow subscribe-only on telemetry topics.
- **Default:** `MQTT_SUBSCRIBER_ENABLED=true`, `EMQX_TELEMETRY_RULE_SETUP_ENABLED=false`.

### Step 3B — Windows MQTT port conflict (2026-10-09)

- **Bug:** Eclipse Mosquitto Windows service (winget) binds `127.0.0.1:1883`; `mosquitto_pub -h localhost -p 1883` hits **Windows Mosquitto**, not EMQX Docker → fake PUBACK, rule `matched: 0`, no DB rows.
- **Fix:** Default **host** MQTT port `11883` → container `1883` (`MQTT_PORT` in `.env`); `NEXT_PUBLIC_MQTT_BROKER_URL` / credentials UI use same port. Linux dev can set `MQTT_PORT=1883`.
- **API:** `/health` returns **503** with `status: starting` until lifespan finishes (migrations run in entrypoint; EMQX rule setup + workers before `API fully ready` log).

### Step 3B — EMQX integration lessons (attempts 1–9)

| # | Topic | Lesson |
| --- | --- | --- |
| 1–4 | Config files | Prefer `cluster-override.conf` merge; avoid broken `emqx.conf.d`; HOCON `${VAR}` is literal — hardcode dev webhook secret |
| 5 | Dashboard REST | Admin password ≠ `/api/v5` auth; use Bearer login or **API key** Basic (`key:secret`) |
| 6–7 | API key bootstrap | `api-keys.conf` = `key:secret` lines only (**no `#` comments**); compose must pass `EMQX_API_KEY`/`SECRET` to **api** |
| 8 | Rule engine API | HTTP **connector** = base URL only; **action** = path + headers; rule `actions: ["http:name"]`; `GET /rules` → `{data:[]}` |
| 9 | Dev environment | Windows **1883** often taken by Mosquitto service — publish to EMQX mapped port (`11883`) |
| 10–11 | Action body | `${.}` forwards full rule event → API **400**; use explicit `topic`/`payload`/`clientid`/`username` template; **PUT** action when body drifts |
| 12 | Auth cache | After **rotate**, `commit` then invalidate Redis `mqtt:auth:{old}` + `mqtt:auth:{new}`; never cache auth **deny** |
| 13 | Ingest schema | Action `${.}` sends full EMQX event — `MqttTelemetryIngestRequest` uses `extra="ignore"` + `payload` str \| dict |
| 14 | Ingest parse | Manual `json.loads` on raw body + **MQTT INGEST RAW BODY** log; avoid `"${payload}"` string embed (broken JSON); action `${.}` |

### Step 3B — EMQX REST API key bootstrap (2026-10-06)

- **Bug:** Dashboard **admin password** does not authenticate `/api/v5/*` (401); login returns Bearer JWT only. Rule setup must use **API key** Basic Auth (`api_key:secret` from bootstrap file).
- **Fix:** `infra/emqx/api-keys.conf` + `EMQX_API_KEY__BOOTSTRAP_FILE`; API uses `EMQX_API_KEY` / `EMQX_API_SECRET`. Dashboard env kept for **UI login only**.
- **Attempt 8:** EMQX 5.8 HTTP connector = base `url` only (no `method`/`headers` on connector); path + secret on **action**; rule `actions` = `http:<action_name>`; `GET /rules` returns `{data:[]}` (parse before idempotent skip).
- **Attempt 7:** Bootstrap file must be **only** `key:secret` lines — `#` comment lines are parsed and break load (`invalid_role` on `SECRET[:ROLE]` in comment text). No `:administrator` suffix required on CE. Compose must pass `${EMQX_API_KEY}` / `${EMQX_API_SECRET}` into **api** (recreate containers after compose changes).

**EMQX integration best practice (6 attempts):** cluster-override merge → HOCON literal webhook secret → dashboard password sync → **API key bootstrap** for automation; avoid assuming dashboard credentials work for REST.

### Step 3B — EMQX dashboard password sync (2026-10-06)

- **Bug:** Rule setup **401** — EMQX 5.8 force-changes default `admin:public`; API used stale password → empty rules, no telemetry forward.
- **Fix:** Fixed dev credentials `admin` / `nextiot-dev-admin` on **emqx** for **Dashboard UI** only; REST rule setup uses **API key bootstrap** (`EMQX_API_KEY` / `EMQX_API_SECRET`).

### Step 3B — Web MQTT credentials, claim tokens UI, EMQX rule forwarding (2026-10-06)

- **Web HQ:** MQTT Credentials panel on `/devices/[id]`; `/claim-tokens` with QR (qrcode.react). Env `NEXT_PUBLIC_MQTT_BROKER_URL`.
- **API startup:** `emqx_rule_setup` uses **EMQX API key** Basic Auth (`EMQX_API_KEY` / `EMQX_API_SECRET` ↔ `infra/emqx/api-keys.conf` bootstrap). Dashboard password is for UI only.
- **Ingest:** Webhook validates access_token matches topic tenant/device before `ingest_pipeline`.
- **Flow:** Device MQTT publish → EMQX rule → API ingest → TimescaleDB.

### Step 3A — EMQX HOCON secret literal (2026-10-06)

- **Bug (attempt 4):** `${MQTT_WEBHOOK_SHARED_SECRET}` in cluster-override stayed literal in runtime → API **403** on webhooks. EMQX HOCON does not expand OS env in `${…}`.
- **Fix:** Hardcode dev secret in `cluster-override.conf`; remove unused secret env from **emqx** service; `test_webhook_secret_consistency.py` guards API settings vs file.

### Step 3A — EMQX cluster-override.conf (2026-10-06)

- **Bug (attempt 3):** `emqx.conf.d` overlay directory is **never loaded** in 5.8 — runtime `authentication = []`, `authorization.no_match = allow`, HTTP ACL absent; cross-device publish allowed. Verified via `emqx ctl conf show`.
- **Fix:** `infra/emqx/cluster-override.conf` → `/opt/emqx/data/configs/cluster-override.conf`. Runtime integration tests (`test_emqx_runtime_config.py`) call `docker compose exec emqx emqx ctl conf show` when Docker CLI available.

### Step 3A — EMQX config overlay directory (2026-10-06)

- **Failed:** `conf.d` mount did not merge config (see cluster-override fix above). Single-file `emqx.conf` override caused crash loop (attempt 1).

### Step 3A — Credential generate conflict + partial unique index (2026-10-06)

- **Bug:** `POST /api/v1/devices/{id}/credentials` returned **500** (`UniqueViolationError` on `ix_device_credentials_client_id`) when the device already had a credential (seed / prior generate) because `client_id` was reused and the DB enforced global uniqueness on inactive rows.
- **Fix:** Generate returns **409** with `"Device already has active credential. Use /rotate to replace."` when an active row exists; **rotate** deactivates the old row (`rotated_at`), inserts a new row with fresh `access_token` + random `dev_{8hex}` `client_id`, and invalidates Redis `mqtt:auth:*` for the old token. **Migration 017:** partial unique indexes on `client_id` and `access_token` where `is_active = true`. Demo LoRa seed no longer auto-creates MQTT credentials (generate on demand).
- **Notion:** Device Credentials — document 409 on duplicate generate vs explicit `/rotate`.

### Step 3 — MQTT / EMQX / credentials / QR claim (2026-10-06)

- EMQX compose service, migration 016, MQTT webhooks + ingest Option A, credential & claim APIs, 20 pytest.
- **Notion:** Step 3, MQTT Broker + EMQX, Device Credentials & QR Claim → **In progress**.

### Step 2B — Thing model at ingest (2026-10-06)

- Validator wired to telemetry bulk (partial-success 200 + `rejected` / `unknown_keys`) and device commands (400 when profiled). Prometheus counters on `/metrics`.
- **Menu & Feature Map:** Telemetry validator at ingest → **In progress**.

### Step 2A — TimescaleDB telemetry (2026-10-06)

- **Infra + Alembic 015:** Timescale hypertable on `telemetry_readings`, compression policy; `app/telemetry/retention.py` daily tier sweep + global retention policy.
- **Menu & Feature Map:** Telemetry Pipeline + TimescaleDB → **In progress**.
- **Note:** Ingest profile validator remains **Step 2B**.

### Step 1B — Device Profiles UI (2026-10-02)

- **Web HQ:** routes `/device-profiles`, `/device-profiles/new`, `/device-profiles/[id]`; sidebar **Device Profiles**; zod client + spec editor; assign panel on `/devices/[id]`.
- **Menu & Feature Map:** Device Profiles / Thing Model Editor → **In progress**.

### Step 1A — Thing Model / Device Profile (2026-10-02)

- **Backend:** `device_profiles` table + `devices.profile_id`; Pydantic `ThingModelSpec`; versioning rules; tenant-scoped API; pure validator; demo seed profiles; 16 pytest cases (spec, validator, API).
- **Menu & Feature Map:** Thing Model / Device Profile API + Validator.

### Step 0 — Engineering Guardrails (2026-09-30 → 2026-10-01)

- **Test DB isolation:** pytest → `next_iot_test` (`DATABASE_URL_TEST` optional), session Alembic migrate, `assert_test_database_name` before TRUNCATE; `RUN_BACKGROUND_WORKERS=false` in tests; `db_echo` via `DB_ECHO` only.
- **Dev image:** `requirements-dev.txt` (pinned ruff/mypy/pytest + stubs) installed when `Dockerfile` `INSTALL_DEV=true` (dev compose); prod `Dockerfile.prod` stays runtime-only.
- **Final:** RATCHET legacy lists in `apps/api/pyproject.toml` (126-entry baseline), CORE modules strict; `check-all.ps1` shows output per step + ratchet guard; `apps/dashboard` frozen.
- Pytest Redis isolation: `REDIS_URL_TEST` / `redis_test_db_index` (default DB 15), `test_redis` fixture with guarded `FLUSHDB` (`assert_test_redis_isolated`), FastAPI `get_redis` override on `client`.
- Ruff: `tests/conftest.py` E402 ignored in `pyproject.toml` (test DB env must load before `app` imports).
- `Settings.assert_test_redis_isolated()` guard before pytest `FLUSHDB`.
- **Menu & Feature Map:** Engineering Guardrails (strict typing, check-all).
- Added `.cursorrules`, `scripts/check-all.ps1`, `docs/TECH_DEBT.md`.
- API: `pyproject.toml`, ruff/mypy deps, migrated `app/**` off `typing.Any` → `pydantic.JsonValue`.
- Web: stricter TS config, ESLint flat config, removed `as unknown as` in automation deploy client.
- Mobile: strict analyzer + typed `FieldApiClient` / DTO models.
- **Status:** P0 Step 0 **In progress** — Architect sign-off; burn down RATCHET per `docs/TECH_DEBT.md`.

See also: `NOTION_UPDATE.md`, `NOTION_TASKS_BACKLOG.md`.

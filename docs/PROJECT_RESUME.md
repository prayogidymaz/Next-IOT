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

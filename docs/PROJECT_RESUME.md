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

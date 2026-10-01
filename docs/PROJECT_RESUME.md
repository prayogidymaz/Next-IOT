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

### Step 0 — Engineering Guardrails (2026-09-30 → 2026-10-01)

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

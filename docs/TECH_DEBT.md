# Next-IoT — Technical Debt (Engineering Guardrails Step 0)

**Audit date:** 2026-10-01 (UTC+7)  
**Scope:** RATCHET legacy modules + incremental burn-down. Step 0 **In progress** (Architect sign-off pending).

## Architecture (official clients)

| Surface | Path | Status |
| --- | --- | --- |
| Web HQ | `apps/web` (Next.js) | Active |
| Mobile | `apps/mobile/field_app` (Flutter) | Active |
| Legacy dashboard | `apps/dashboard` | **FROZEN** — see `apps/dashboard/FROZEN.md` |

## Guardrails snapshot

| Check | Status |
| --- | --- |
| `scripts/check-all.ps1` | Green when RATCHET baseline honored |
| API `ruff` (`app`, `tests`) | Pass (CORE strict; legacy ANN/B008 in `pyproject.toml`) |
| API `mypy` (`app`) | Pass (CORE strict; legacy overrides in `pyproject.toml`) |
| API `pytest` | Pass (Redis test DB + `assert_test_redis_isolated`) |
| Web `npm run lint` / `typecheck` | Pass |
| Flutter `field_app` analyze | Pass |
| Forbidden `Any` / `any` / `dynamic` (scoped scans) | 0 |

## RATCHET (legacy API modules)

- **Baseline:** `scripts/ratchet-baseline.txt` → **126** entries (ruff legacy globs + mypy module names).
- **Source of truth:** `apps/api/pyproject.toml` blocks marked `LEGACY RATCHET — list only shrinks`.
- **Policy:** Each future Step removes ≥1 legacy module from overrides and lowers the baseline.
- **CORE (strict):** `app/config.py`, `app/main.py`, `app/database.py`, `app/types/*`, `app/auth/*`, `app/devices/*`, `app/telemetry/*` except `app/telemetry/video_feed/*`, `app/commands/*`, `app/tenants/*`, `app/users/*`, `tests/conftest.py`.

Legacy lists (107 mypy modules, 19 ruff globs) live only in `pyproject.toml` — keep identical when editing debt.

## Web — JSON boundaries (zod)

| Location | Status |
| --- | --- |
| `lib/auth/api.ts` | zod via `lib/auth/schemas.ts` |
| `lib/api/automation.ts` | zod via `lib/api/automation-schemas.ts` |
| `lib/hq/hq-shell-context.tsx:67` | TODO: zod for `/health` payload |

Do not disable ESLint rules to clear debt.

## MQTT telemetry forwarding (Step 3B → 3C)

| Item | Status |
| --- | --- |
| EMQX Rule Engine HTTP action (`${payload}` / `json_encode` → invalid JSON for ingest) | **Parked** — `emqx_rule_setup.py` kept; disabled via `EMQX_TELEMETRY_RULE_SETUP_ENABLED=false` |
| **Step 3C** asyncio-mqtt platform subscriber (`app/mqtt_subscriber`) | **RESOLVED** — subscribe `tenants/+/devices/+/telemetry`, ingest via shared pipeline |

Internal broker credentials: `MQTT_SUBSCRIBER_INTERNAL_USER` / `MQTT_SUBSCRIBER_INTERNAL_PASSWORD` (HTTP auth + ACL in `subscriber_auth.py`).

**Transaction vs side effects:** `ingest_telemetry()` publishes Redis/WebSocket events after `flush()` but before the caller commits (HTTP `get_db` and MQTT subscriber both commit afterward). A rollback after publish can leave subscribers seeing events without a persisted row — acceptable for dev; tighten ordering if we need exactly-once semantics.

## Next actions

1. Port rows from `apps/dashboard/FROZEN.md` into `apps/web`.
2. Remove one RATCHET legacy module per milestone; update `ratchet-baseline.txt`.
3. Add zod for remaining fetch sites under `apps/web/lib/**`.

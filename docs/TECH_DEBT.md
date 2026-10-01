# Next-IoT — Technical Debt (Engineering Guardrails Step 0)

**Audit date:** 2026-09-30 (UTC+7)  
**Scope:** Post–Step 0 tooling rollout; Senior Architect verification pending.

## Initial violation counts (before fixes)

| Area | Category | Initial | After Step 0 |
| --- | --- | ---: | ---: |
| `apps/api/app` | `typing.Any` / `: Any` | ~220 | **0** (forbidden scan) |
| `apps/api` | `# type: ignore` | 0 | 0 |
| `apps/web` (app/components/lib/hooks) | `any` / `as unknown as` / `@ts-ignore` | 2 | **0** |
| `apps/mobile/field_app/lib` | explicit `dynamic` | 4 | **0** |
| `apps/api` | **ruff** (E,F,I,B,UP,ANN,PGH) | 317 | 317 (see below) |
| `apps/api` | **mypy** strict | blocked (syntax) | **632** errors / 111 files |
| `apps/api` | **pytest** | — | 208 passed, **1 failed** (`test_lora_bridge.py::test_gateway_status_endpoint`) |

## Ruff — representative debt (fix incrementally)

Run: `docker compose exec -T api ruff check app`

Primary buckets:

- **ANN*** — missing / incomplete return type annotations across routers, services, workers.
- **I*** — import order (84 auto-fixable via `ruff check app --fix`).

Core modules already migrated off `Any` to `pydantic.JsonValue` (`app/types/json_types.py`).

## Mypy strict — follow-up by package

Run: `docker compose exec -T api mypy app`

| Package | Notes |
| --- | --- |
| `app/main.py` | Untyped lifespan handlers; Redis generic params |
| `app/devices/router.py` | Redis type parameters |
| `app/mission/*`, `app/hardware/*`, `app/mavlink/*` | Strict inference on JSON helpers |
| `app/automation/pipeline_interpreter.py` | Complex graph interpreter — needs Protocol/TypedDict node shapes |

**Policy:** Do not add `# type: ignore` or disable strict flags; fix types or introduce narrow TypedDict/Protocol models.

## Pytest

- `tests/test_lora_bridge.py::test_gateway_status_endpoint` — investigate gateway status fixture vs Redis key (pre-existing / environmental).

## Web

- `npm run typecheck` — **pass** after `noUncheckedIndexedAccess` fixes in `lib/auth/session.ts`, `lib/hq/domains.ts`, `lib/hq/hq-shell-context.tsx`.
- ESLint strict `@typescript-eslint/no-unsafe-*` — run `npm run lint` after `eslint.config.mjs`; resolve any remaining unsafe JSON boundaries with zod (future Step 1).

## Mobile

- `flutter analyze` — **pass** (strict-casts / strict-inference enabled).

## Next actions (recommended)

1. `ruff check app --fix` then manual ANN pass on **auth, devices, telemetry, commands, automation**.
2. Mypy: fix `app/main.py` + Redis typing pattern once, replicate across routers.
3. Repair `test_lora_bridge.py` gateway status assertion.
4. Re-run `scripts/check-all.ps1` before marking P0 Step 0 **Done** in Notion.

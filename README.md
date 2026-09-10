# Next-IOT Platform

Multi-tenant IoT platform — monorepo bootstrap.

## Structure

```
Next-IOT/
├── apps/api/          # FastAPI backend
├── apps/dashboard/    # Flutter multi-tenant dashboard (P2)
├── packages/shared/   # Shared constants & types
├── infra/docker/      # Docker init scripts
└── docker-compose.yml # Local dev stack
```

## Quickstart

### Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.12+ for local dev without Docker

### 1. Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local dev)
```

### 2. Start stack

```bash
docker compose up --build
```

Services:

| Service  | URL / Port        |
|----------|-------------------|
| API      | http://localhost:8000 |
| Swagger  | http://localhost:8000/docs |
| Health   | http://localhost:8000/health |
| Postgres | localhost:5432    |
| Redis    | localhost:6379    |

### 3. Verify

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "Next-IOT",
  "environment": "development",
  "checks": { "database": "ok", "redis": "ok" }
}
```

### Local dev (without Docker for API)

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

> Postgres & Redis must still be running (via `docker compose up postgres redis`).

## Migrations

```bash
cd apps/api
alembic upgrade head          # apply
alembic revision --autogenerate -m "description"  # new migration
```

## Auth API (Task #2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Buat tenant + admin user, return JWT |
| POST | `/auth/login` | Login, return access + refresh token |
| POST | `/auth/refresh` | Rotate tokens (refresh token rotation) |
| POST | `/auth/logout` | Revoke refresh token |

### Default dev login (auto-seeded)

After `docker compose up -d api`, a super-admin is created automatically:

| Email | Password | Role |
|-------|----------|------|
| `admin@nextiot.com` | `admin123` | `super_admin` |

See [docs/DEFAULT-CREDENTIALS.md](docs/DEFAULT-CREDENTIALS.md). Manual re-seed: `docker compose exec api python -m app.seed`

CORS is enabled for Flutter Web (`CORS_ALLOW_ORIGINS=*` by default).

### Quick test

```bash
# Login (seeded admin)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nextiot.com","password":"admin123"}'

# Or register a new tenant
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"tenant_name":"Acme","tenant_slug":"acme","email":"admin@acme.com","password":"SecurePass123!"}'
```

### Run tests

```bash
docker compose run --rm api pytest tests/ -v
```

## RBAC & Security Tiering (Task #3)

Protected routes under `/api/v1/*` require `Authorization: Bearer <access_token>`.

| Role | Access |
|------|--------|
| `super_admin` | Cross-tenant + `/api/v1/super/*` |
| `tenant_admin` | Tenant admin endpoints |
| `operator` | Read + device commands |
| `viewer` | Read-only (403 on write/admin) |

**Security tiers:** Tier 1 (`free` 60 req/min) · Tier 2 (`pro` 300) · Tier 3 (`enterprise` 1000)

| Method | Endpoint | Required role |
|--------|----------|---------------|
| GET | `/api/v1/me` | any authenticated |
| GET | `/api/v1/tenants/{id}` | own tenant or super_admin |
| GET | `/api/v1/admin/users` | tenant_admin, super_admin |
| POST | `/api/v1/devices/command` | operator+, tenant_admin, super_admin |
| GET | `/api/v1/super/tenants` | super_admin only |

## Device Lifecycle (Task #4)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/devices` | tenant_admin+ | Register device → returns provisioning token |
| GET | `/api/v1/devices` | viewer+ | List devices (tenant-scoped) |
| GET | `/api/v1/devices/{id}` | viewer+ | Device detail (tenant isolation) |
| POST | `/api/v1/devices/{id}/provision` | provisioning token | Exchange token → client_id + secret |
| GET | `/api/v1/devices/{id}/auth-check` | HTTP Basic (device) | Verify device credentials |

Device status flow: `pending` → `provisioned` → `online` ↔ `offline` | `deactivated`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/devices/{id}/heartbeat` | HTTP Basic (device) | Update `last_seen_at`, set `online` |
| PATCH | `/api/v1/devices/{id}/status` | tenant_admin+ | Deactivate / reactivate device |

Offline detection: Redis liveness key (TTL 5 min) + background worker every 60s. Events stub: `device:events` queue (`device.online`, `device.offline`).

## Roadmap (P0)

1. ~~Bootstrap monorepo & infra~~
2. ~~Core Auth — Multi-tenant JWT~~
3. ~~RBAC & Security Tiering~~
4. ~~Device Lifecycle — Provisioning~~
5. ~~Device Lifecycle — Heartbeat & state machine~~ ← P0 complete!

## Telemetry Engine (P1)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/telemetry` | HTTP Basic (device, must be `online`) | Ingest sensor metrics |

**Payload example:**
```json
{
  "timestamp": "2026-09-09T15:00:00Z",
  "metrics": {"temperature": 26.5, "humidity": 61.2, "ph": 7.1, "flow_rate": 12.3}
}
```

- Time-series stored in PostgreSQL (`telemetry_readings`)
- Latest values cached at Redis `device:telemetry:latest:{device_id}`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/devices/{id}/telemetry/latest` | JWT (viewer+) | Latest from Redis cache |
| GET | `/api/v1/devices/{id}/telemetry/history` | JWT (viewer+) | Time-series from PostgreSQL (`start_time`, `end_time`, `limit`) |

**Rule Engine:** table `rules` — on each telemetry ingest, active rules are evaluated; triggered alerts pushed to Redis `device:alerts`.

**Notification Dispatcher:** background worker consumes `device:alerts` and dispatches via Telegram Bot API and/or signed webhooks.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/notifications/test` | tenant_admin+ | Test Telegram/Webhook dispatch |
| GET | `/api/v1/alerts` | viewer+ | List active/history alerts (Redis) |
| GET | `/api/v1/alerts/summary` | viewer+ | Active alert count + recent items |
| GET | `/api/v1/rules` | operator+ | List tenant rules |
| POST | `/api/v1/rules` | operator+ | Create rule |
| GET | `/api/v1/devices/{id}/rules` | operator+ | List device rules |
| PATCH | `/api/v1/rules/{id}` | operator+ | Update rule |
| DELETE | `/api/v1/rules/{id}` | operator+ | Delete rule |

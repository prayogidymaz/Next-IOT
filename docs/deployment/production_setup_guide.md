# Production Setup Guide — Colocation & Docker Hardening

Deploy Next-IOT on bare metal (e.g. **AMD EPYC**, Ubuntu Server 22.04/24.04) with **Docker Compose production stack** and optional **Tailscale** or **Cloudflare Tunnel** edge access.

## Stack overview

| Service | Role |
| --- | --- |
| `proxy` | Nginx TLS termination, rate limits, security headers, WebSocket upgrade |
| `web` | Next.js marketing + `/cyberdeck` (`apps/web`) |
| `dashboard` | Flutter Web operator UI at `/dashboard/` |
| `api` | FastAPI + Gunicorn/Uvicorn workers |
| `db` | PostgreSQL 16 (persistent volume) |
| `cache` | Redis 7 AOF + password |
| `mqtt` | Eclipse Mosquitto (1883 MQTT + 9001 WebSocket) |

Files:

- `docker-compose.prod.yml`
- `.env.production.example` → copy to `.env.production`
- `nginx/nginx.conf`
- `scripts/deploy_prod.sh`

## 1. Server preparation (Ubuntu)

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git curl openssl
sudo usermod -aG docker $USER
```

Clone repo, configure env:

```bash
cp .env.production.example .env.production
# Edit secrets: POSTGRES_PASSWORD, REDIS_PASSWORD, JWT_SECRET_KEY, MQTT_PASSWORD
```

## 2. Deploy

```bash
chmod +x scripts/deploy_prod.sh
./scripts/deploy_prod.sh
```

Manual equivalent:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production config
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
curl -sf http://127.0.0.1/health
```

## 3. Routing (via `proxy`)

| Path | Backend |
| --- | --- |
| `/` | Next.js `web:3000` |
| `/dashboard/` | Flutter Web `dashboard:80` |
| `/api/` | FastAPI `api:8000` (includes WebSocket upgrade for API routes) |
| `/ws/mqtt` | Mosquitto WebSocket `mqtt:9001` |
| `/health` | API health |

## 4. Tailscale (private mesh)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Publish MagicDNS name (e.g. `next-iot-edge`) and point team clients to `https://next-iot-edge/dashboard/`.

Set in `.env.production`:

```env
TAILSCALE_HOST=next-iot-edge
PUBLIC_HOST=next-iot-edge.tailnet-name.ts.net
```

## 5. Cloudflare Tunnel (public edge without open ports)

```bash
cloudflared tunnel create next-iot
cloudflared tunnel route dns next-iot iot.example.com
```

`config.yml` ingress example:

```yaml
ingress:
  - hostname: iot.example.com
    service: http://127.0.0.1:80
  - service: http_status:404
```

Run tunnel with token from `.env.production` `CLOUDFLARE_TUNNEL_TOKEN`.

## 6. Hardening checklist

- [ ] Replace self-signed certs in `infra/certs/` with Let's Encrypt or Cloudflare origin certs
- [ ] Set `SEED_DEFAULT_ADMIN=false` after first admin bootstrap
- [ ] Restrict `proxy` ports via firewall (only 443 public; SSH via Tailscale)
- [ ] Rotate `JWT_SECRET_KEY`, DB/Redis/MQTT passwords quarterly
- [ ] Enable Mosquitto ACLs for topic namespaces (`next-iot/telemetry/#`)
- [ ] Backup volumes: `postgres_prod_data`, `redis_prod_data`, `mqtt_prod_data`

## 7. Migrations & rollback

Migrations run on API container start (`alembic upgrade head`).

Rollback image:

```bash
docker compose -f docker-compose.prod.yml pull  # if using registry tags
docker compose -f docker-compose.prod.yml up -d api
```

## 8. Monitoring

- API: `GET /health`, `GET /api/v1/system/health` (authenticated)
- Container health: `docker compose -f docker-compose.prod.yml ps`
- Logs: `docker compose -f docker-compose.prod.yml logs -f api proxy`

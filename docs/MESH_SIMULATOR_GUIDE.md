# Mesh Device Simulator Guide

Zero-hardware testing for Universal Mesh workflows (Week 7–8).

## Bootstrap devices

```bash
docker compose exec -T api python scripts/bootstrap_mesh_simulator_devices.py --tenant-slug kopi-toraja-mitra
```

Copy `device_id`, `client_id`, and `client_secret` into simulator env vars (`TENANT_ID`, `DEVICE_ID`, `MQTT_USERNAME`, `MQTT_PASSWORD`).

## Start simulators (opt-in profile)

```bash
docker compose --profile simulators up -d cctv-simulator sprayer-simulator gate-simulator cyberdeck-simulator weather-simulator smartwatch-simulator
```

Simulators publish to MQTT topic `tenants/{tenant_id}/mesh/events/{domain}/{event_type}`. The API MQTT subscriber ingests them into `mesh_events` and Redis fan-out for the workflow engine.

## Manual CLI (inside API container)

```bash
docker compose exec -T api env TENANT_ID=... DEVICE_ID=... MQTT_USERNAME=... MQTT_PASSWORD=... \
  python -m app.mesh_simulators.cli cctv
```

## Trigger mesh events via API (no simulator)

```bash
curl -X POST http://localhost:8000/api/v1/mesh/events -H "Authorization: Bearer $TOKEN" \
  -d '{"device_id":"...","domain":"vision","event_type":"motion_detected","payload":{"confidence":0.9}}'
```

## Debug pest-response workflow

1. Seed presets: `python scripts/seed_mesh_preset_workflows.py --tenant-slug kopi-toraja-mitra`
2. Publish `vision/motion_detected` (simulator or API)
3. Query executions: `GET /api/v1/mesh/workflows/{id}/executions`
4. Dry-run: `POST /api/v1/mesh/workflows/{id}/test`

## Drone simulator

Existing service `drone-simulator` now emits `motion/*` mesh events over MQTT when flights run. MAVLink/Redis command flow unchanged.

## CCTV HTTP trigger (playground)

With simulators profile, CCTV exposes `POST http://localhost:9100/simulate-motion` (`{"confidence":0.9}`).

## FCM tokens (mobile / edge clients)

1. Enable API: `NOTIFICATION_FCM_ENABLED=true` (+ `FCM_PROJECT_ID`, `FCM_PRIVATE_KEY_JSON` base64)
2. Clients register: `POST /api/v1/notifications/fcm/register` with Bearer JWT
3. Mesh workflow `notification` action with `"fcm"` in `channels` pushes to tenant tokens

## E2E demo script

```bash
python scripts/demo_farm_pest_response.py --skip-compose
```

See `docs/MESH_PHASE1_COMPLETE.md` for full Phase 1 overview.

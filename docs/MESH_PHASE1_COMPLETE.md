# Smart Farming Universal Mesh — Phase 1 Complete

Phase 1 spans Weeks 1–12: thing model, event bus, workflows, simulators, HQ mesh graph, Wear companion, FCM + scheduler + E2E demo.

## Architecture (Mermaid)

```mermaid
flowchart LR
  Devices[Simulators / Devices] --> MQTT[EMQX]
  MQTT --> Ingest[MQTT Ingest]
  Ingest --> Bus[Mesh Event Bus]
  Bus --> API[FastAPI /mesh]
  Bus --> WF[Workflow Executor]
  WF --> FCM[FCM Push]
  WF --> Actuators[Device Commands]
  API --> Web[HQ Mesh Graph SSE]
  API --> Wear[Wear OS SSE]
```

## Capability matrix (summary)

| Domain | Example capabilities | Simulator |
| --- | --- | --- |
| vision | motion_detected | cctv |
| motion | dispatch, waypoint | drone |
| actuator | valve, spray | sprayer, gate |
| sensor | reading, forecast | weather |
| ui | alert, ack | cyberdeck, smartwatch |
| security | intrusion | alarms hook |

## Preset workflows

1. Smart Irrigation Extended  
2. Farm Pest Response  
3. Security Patrol Night  
4. Harvest Coordination  

Seed: `python scripts/seed_mesh_preset_workflows.py --tenant-slug <slug>`

## FCM + SSE setup

- API env: `NOTIFICATION_FCM_ENABLED`, `FCM_PROJECT_ID`, `FCM_PRIVATE_KEY_JSON` (base64 service account JSON)
- Register token: `POST /api/v1/notifications/fcm/register`
- Wear: pair JWT → SSE `/api/v1/mesh/events/stream` + FCM register on start

## E2E demo

```bash
docker compose --profile simulators up -d
python scripts/demo_farm_pest_response.py --skip-compose
```

Report: `/tmp/demo-pest-response-*.md`

## Phase 2 hardware roadmap

- LILYGO T-Watch S3 + Next-OS Wear v1 firmware replacing smartwatch simulator
- Physical CCTV / sprayer MQTT devices on tenant bus
- Production FCM project + Play Console Wear release

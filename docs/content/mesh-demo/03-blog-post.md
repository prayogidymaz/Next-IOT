# How We Built Indonesia's First Universal IoT Mesh (Simulator-First, pytest-Gated)

**Subtitle:** Satu session besar, puluhan commit atomik, ratusan automated tests — tanpa menunggu semua hardware di meja.

**Audience:** Developer Indonesia + founder yang mau tahu *how* bukan cuma *what*.  
**Length:** ~1,800 kata · cocok Medium / dev.to / blog NextGrow

---

## Hook

Alembic head **040**. Mesh event bus **6 domain**. **584** test case terkumpul di pytest API (Docker, Okt 2026). Step 8C menambah AI Copilot, Camera Gateway stub, dan Analytics — **14 test** baru lulus di batch pertama. Firmware NextWatch jalan di SDL2 (Windows + WSLg).

Bukan angka marketing. Itu angka yang kami lihat saat `docker compose exec api pytest` — sebelum LILYGO sampai.

---

## Context: Visi Next-IOT & gap pasar

Next-IOT bukan “dashboard telemetry cantik” saja. Visinya: **operating system for physical operations** — kebun, gudang, patrol — di mana sensor, kamera, drone, actuator, dan manusia (UI domain) berbicara lewat **event vocabulary** yang sama.

Gap di Indonesia:

- Integrasi WhatsApp / ops lapangan jarang first-class di platform global.
- Pilot hardware-heavy sering mati di minggu 3 karena belum ada end-to-end story.
- Tim kecil tidak punya bandwidth maintain N integrasi one-off.

Jawaban kami: **Universal Mesh** di `apps/api/app/mesh/` + **simulator-first** + **strict pytest**.

---

## Technical challenge #1: Cross-domain event standardization

Problem: string event bebas (`"alert"`, `"motion"`) tidak scalable.

Solusi: enum `MeshDomain` + whitelist `DOMAIN_EVENT_TYPES` per domain (`event_bus.py`). Publish path menolak pasangan domain/type yang tidak valid.

Setiap event membawa `MeshContext`: farm, plot, zone, geo, capabilities — di-resolve dari device profile saat ingest.

**Lesson:** Invest di schema dulu; workflow matching jadi deterministic, bukan regex di 40 tempat.

---

## Technical challenge #2: Device resolver & haversine

Workflow action `dispatch_device` tidak hard-code UUID. Spec resolver:

```text
capability + zone + nearest_to(geo) + optional device_id
```

Implementasi: SQL + filter capability di profile, haversine untuk jarak (`device_resolver.py`). Test: `test_device_resolver_by_capability_and_zone`, haversine sanity.

**Lesson:** Template `{{trigger.context.geo_location}}` di DSL memungkinkan satu workflow untuk banyak plot — asalkan metadata device benar.

---

## Technical challenge #3: Workflow executor & correlation chain

Executor menjalankan actions sequential / wait-for-event, log ke `mesh_workflow_executions`, publish `workflow_completed` ke domain `ui` bila sukses.

`correlation_id` dan `parent_event_id` di MeshEvent memungkinkan trace: motion CCTV → dispatch drone → spray → notification.

Preset seed: `smart_irrigation_extended`, `farm_pest_response`, `security_patrol_night`, `harvest_coordination` (`seed_preset_workflows.py`).

**Lesson:** Audit log JSON action results worth it saat demo ke investor — mereka tanya “what actually happened?”.

---

## Technical challenge #4: Six simulators, zero hardware

In-process simulators (`apps/api/app/mesh_simulators/`):

- `cctv`, `sprayer`, `cyberdeck`, `gate`, `weather`, `smartwatch`

Mereka publish event lewat publisher abstraction yang sama dengan device nyata. E2E test `test_e2e_farm_pest_response_full_chain` membuktikan matching + dry-run API tanpa MQTT broker fisik di CI.

Firmware parallel: `next-os-wear` simulator mock MQTT → `mesh_ui_sync` refresh KPI watch face.

**Lesson:** Simulator-first bukan “nice to have” — itu **risk reducer** untuk tim 2–3 engineer.

---

## Prompt-driven development pattern (Cursor + review gates)

Kami tidak claim “4 jam total platform”. Yang jujur: **incremental sessions** dengan template prompt:

1. Scope satu commit atomik (contoh Step 8C → 3 commit: `5f9ef89`, `aea4be1`, `6b3938f`).
2. Implement + Alembic `downgrade()` wajib.
3. pytest happy path + tenant isolation.
4. Register ORM di `app/models/__init__.py` (FK audit lesson).
5. `scripts/check-all.ps1` sebelum merge lokal.

**Contoh 1 prompt → 1 commit berjalan:**  
“AI Copilot mock mode + POST `/api/v1/mesh/copilot/generate` + 4 pytest” → commit `5f9ef89`, mock LLM tanpa `ANTHROPIC_API_KEY`.

Verification strategy per step:

```bash
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest tests/mesh/ai_copilot/ -v
docker compose exec -T api pytest tests/test_model_registration.py -v
```

---

## Lessons learned (applicable beyond Next-IOT)

1. **Simulator-first validates end-to-end** — preset workflow + simulators > slide deck.
2. **Fixture isolation** — test DB `*_test`, Redis DB index terpisah; TRUNCATE guard. FK audit regression (`test_foreign_key_targets_exist_in_metadata`).
3. **Ratchet baseline** — typing/lint debt tidak naik sembarangan (`.cursorrules`).
4. **Universal event bus** — pay schema tax early; domains × event types × context.
5. **Mock mode for expensive deps** — AI Copilot, placeholder RTSP snapshot: dev tanpa budget API/cloud.
6. **Firmware stale pointer class** — timer + LVGL delete guards; crash WSL repro → dispose pattern (commit `48fa31b`).

---

## What shipped in Step 8C (concrete)

| Feature | Endpoint / artifact |
| --- | --- |
| AI Copilot | `POST /api/v1/mesh/copilot/generate`, `/explain`, `/examples` |
| Camera GW stub | `POST /api/v1/cameras`, ingest-motion → `vision/motion_detected` |
| Analytics | CSV export telemetry/alerts/yield, scheduled reports, energy kWh |

Semua backward compatible — tidak break API v1 existing.

---

## What's next

- Hardware LILYGO integration path (MQTT real, bukan mock).
- go2rtc untuk snapshot RTSP nyata (stub URL today).
- Open source **planned Q1 2027** — follow NextGrow untuk announcement resmi.

---

## Call to action

Lo developer yang mau contribute atau founder yang mau pilot?

- Baca arsitektur: `docs/content/mesh-demo/01-architecture.md`
- Resume teknis: `docs/PROJECT_RESUME.md`
- Follow **NextGrow** / **@prayogidymaz** untuk update pilot (ganti handle jika berbeda saat publish)

**Disclaimer:** Blog ini behind-the-scenes engineering narrative. Bukan janji SLA produksi; pilot subject to capacity.

---

*Written from the actual Next-IOT monorepo state, October 2026.*

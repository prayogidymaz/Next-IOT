# Social Media Pack — Universal Mesh Demo Launch

**Brand palette hint (Instagram):** Tactical Warm Cream background, olive accent, dark text — selaras Web HQ.  
**Stats to verify before publish:** Alembic **040**, pytest **584** collected (API), Step 8C **14 passed**, commits `5f9ef89` / `aea4be1` / `6b3938f`.

---

## LinkedIn — Carousel (10 slides) + Caption

### Slide copy

| # | Judul slide | Body (max ~40 kata/slide) |
| --- | --- | --- |
| 1 | Platform IoT Indonesia baru launch | Next-IOT Universal Mesh: satu event bus untuk sensor, CCTV, drone, sprayer, gate, wearable. Pilot smart farming 2026. |
| 2 | Masalah: silo IoT | Tuya = smart home. ThingsBoard = telemetry berat. AWS = mahal. Petani butuh orchestration lintas device. |
| 3 | Universal Mesh | 6 domain: sensor · vision · motion · actuator · security · ui. Event tervalidasi, multi-tenant. |
| 4 | Workflow Engine | DSL declarative: trigger → condition → actions. Preset Farm Pest Response & irigasi pintar. |
| 5 | Device Resolver | Pilih device by capability + zone + nearest geo — bukan hard-code UUID. |
| 6 | 6 Simulators | CCTV, sprayer, cyberdeck, gate, weather, smartwatch — demo tanpa hardware lengkap. |
| 7 | AI Copilot (8C) | Prompt Bahasa Indonesia → workflow JSON. Mock mode untuk dev tanpa API key. |
| 8 | Camera + Analytics | RTSP registry stub, motion → mesh. CSV export, energy kWh, scheduled reports. |
| 9 | NextWatch | Firmware LVGL simulator: mock MQTT, mesh graph, farming hub — Phase 2 selesai. |
| 10 | Pilot NextGrow | Slot terbatas kebun kopi Indonesia. DM / email untuk demo Docker live. |

### Caption LinkedIn (~1,450 karakter)

Platform IoT global hebat di niche masing-masing. Tapi kalau lo operasikan kebun + drone + CCTV + irigasi, lo butuh **satu bahasa event** — bukan lima dashboard.

Kami ship **Next-IOT Universal Mesh**: event bus 6 domain, workflow engine dengan preset smart farming, device resolver (capability + zone + haversine), dan **6 in-process simulators** supaya end-to-end test jalan sebelum hardware LILYGO landing.

Step 8C (Okt 2026): AI Copilot (NL → workflow DSL), Camera Gateway stub (motion → `vision/motion_detected`), Analytics CSV + scheduled reports + energy estimate.

Angka engineering riil: Alembic migration **040**, **584** pytest cases di suite API, **14** test baru Step 8C lulus batch pertama.

Ini bukan deck futuristik — code ada di monorepo, Docker Compose health check hijau, E2E Farm Pest Response di pytest.

**NextGrow** buka pilot terbatas untuk petani kopi & agtech founder Indonesia. Mau lihat demo workflow + mesh graph live? Comment "PILOT" atau DM — kita share arsitektur PDF (`docs/content/mesh-demo/`).

#IoT #AgTech #SmartFarming #Indonesia #Startup #Engineering #NextIOT #UniversalMesh

---

## Twitter / X — 12-tweet thread

**Tweet 1 (hook)**  
Menyelesaikan fondasi **Universal IoT Ecosystem** Next-IOT: 6 domain mesh, workflow DSL, 6 simulators, firmware NextWatch SDL2, Step 8C Copilot+Camera+Analytics. Alembic head 040. Thread 🧵

**Tweet 2**  
Problem: Tuya ≠ farm orchestration. ThingsBoard = lo yang rakit cross-domain. AWS IoT = scale + cost. Indonesia butuh WA-ready, self-host pilot, Bahasa Indonesia workflow.

**Tweet 3**  
Solusi: `MeshDomain` sensor | vision | motion | actuator | security | ui — whitelist event types, no random strings.

**Tweet 4**  
Publish path: device/sim → Postgres `mesh_events` + Redis fan-out + MQTT topic `tenants/{id}/mesh/events/...`

**Tweet 5**  
Workflow listener → match preset (Farm Pest Response, smart irrigation, …) → executor chain + audit `mesh_workflow_executions`.

**Tweet 6**  
Device resolver: capability `can_fly_to`, zone plot_A, nearest_to geo — haversine in code, tested pytest.

**Tweet 7**  
Zero-hardware QA: simulators cctv, sprayer, cyberdeck, gate, weather, smartwatch — E2E demo < 5s in tests.

**Tweet 8**  
Step 8C commits: `5f9ef89` AI Copilot mock LLM · `aea4be1` camera motion ingress · `6b3938f` analytics CSV/energy.

**Tweet 9**  
584 pytest cases collected (API docker). 14 new tests Step 8C green. Model registration FK guard — lesson learned baked in.

**Tweet 10**  
Firmware: next-os-wear simulator, mock MQTT KPI, mesh graph pulse — Phase 2 complete while waiting LILYGO.

**Tweet 11**  
Docs drop: `docs/content/mesh-demo/` architecture write-up + video script + blog post. No fluff, Mermaid diagrams included.

**Tweet 12 (CTA)**  
Pilot smart farming Indonesia — slot limited via NextGrow. RT if you want open-source timeline (planned Q1 2027). DM for Docker demo.

*(Attach: 1 screenshot mesh graph UI + 1 workflow JSON snippet)*

---

## Threads (Meta) — 6 posts, conversational

**Post 1**  
Oke jujur — nunggu hardware IoT datang itu boring. Jadi kami selesain Universal Mesh backend + simulator dulu 😅

**Post 2**  
Bayangin: CCTV deteksi motion → drone dispatch otomatis → sprayer → notif WA. Bukan film. Preset workflow + pytest E2E di Next-IOT.

**Post 3**  
Enam domain event: sensor, vision, motion, actuator, security, UI. Semua lewat satu bus. Developer happy. Petani (nanti) juga happy.

**Post 4**  
Baru minggu ini Step 8C: AI Copilot bikin workflow dari prompt Indo, camera stub, export CSV analytics. 3 commit atomik.

**Post 5**  
Smartwatch firmware? LVGL jalan di laptop (SDL2). Mock MQTT update KPI watch face. Hardware nyusul — software nggak idle.

**Post 6**  
Kalau lo kebun kopi / agtech dan mau pilot — DM NextGrow. Kita cari 10 early partner. Gratis ilustrasi persona, bukan testimonial palsu ya 🙏

---

## Instagram Carousel — 10 slides (image copy)

Design hint: cream `#F5F0E6`, olive `#6B7C4C`, radius 12px cards, icon line-art per slide.

| Slide | Headline (≤8 kata) | Body (≤25 kata) |
| --- | --- | --- |
| 1 | IoT untuk kebun nyata | Next-IOT Universal Mesh — satu ecosystem, enam domain device. |
| 2 | Bukan cuma smart home | Orchestrate drone, sprayer, CCTV, sensor tanah. |
| 3 | Enam domain | Sensor · Vision · Motion · Actuator · Security · UI |
| 4 | Workflow otomatis | Trigger event → action chain → notifikasi petani. |
| 5 | Farm Pest Response | Motion → dispatch → spray. Preset bawaan platform. |
| 6 | Tanpa hardware dulu | Enam simulator in-process + pytest E2E. |
| 7 | AI Copilot | Prompt Indo → workflow JSON. Dev friendly mock mode. |
| 8 | Kamera + analytics | Motion ingress mesh. CSV & energy kWh. |
| 9 | NextWatch sim | Wearable UI sync mesh — SDL2 simulator. |
| 10 | Join pilot | NextGrow — slot terbatas. Link di bio. |

**Instagram caption (short)**  
Satu kebun. Banyak device. Satu workflow. 🌱  
Next-IOT Universal Mesh sudah live untuk pilot (software-first).  
Details di link bio · #smartfarming #iotindonesia #nextiot #nextgrow

---

## Pre-publish checklist

- [ ] Ganti placeholder email/QR dengan kontak NextGrow produksi  
- [ ] Re-run pytest count if marketing stale >30 days  
- [ ] Screenshot mesh graph dari Web HQ (real UI, bukan mock)  
- [ ] Tandai ilustrasi WA / persona di video/carousel jika dipakai  
- [ ] LinkedIn PDF upload optional: export `01-architecture.md` → PDF  

**Commit path:** `docs/content/mesh-demo/*.md` only — zero application code.

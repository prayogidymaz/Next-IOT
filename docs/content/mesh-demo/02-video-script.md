# Video Script — Next-IOT Universal Mesh Demo (3–5 menit)

**Format:** Scene-by-scene · VO Bahasa Indonesia santai · NextGrow tone  
**Target:** YouTube (primary), Instagram Reels, TikTok (crop 9:16 per scene)  
**Durasi total:** ~4:45 (bisa dipadatkan ke ~3:00 dengan skip scene 2:30–3:30)

Legenda: **VIS** = visual · **VO** = voice-over · **MUS** = music · **B-roll** = cutaway

---

## Scene 1 — Hook (0:00–0:15)

**VIS:** Drone shot / stock kebun kopi pagi hari. Overlay 7 icon: sensor tanah, CCTV, drone, sprayer, gate, smartwatch, cloud dashboard. Counter animasi “1 workflow”.

**MUS:** Cinematic pulse, tempo 100 BPM, hopeful.

**VO:**  
“Satu kebun kopi. Tujuh device IoT. Satu workflow otomatis — dari deteksi hama sampai notifikasi WhatsApp. Ini bukan mockup PowerPoint. Ini Next-IOT Universal Mesh.”

---

## Scene 2 — Problem (0:15–0:45)

**VIS:** Split screen: logo Tuya / ThingsBoard / AWS IoT dengan animasi ❌ merah di label “smart farming end-to-end”. Cut ke petani lihat 4 app berbeda di HP.

**B-roll:** Screen recording scroll pricing AWS; diagram rumit ThingsBoard rule chain.

**MUS:** Tension bed tipis, lower volume.

**VO:**  
“Tuya? Kuat di smart home, bukan orchestrate drone plus sprayer plus CCTV. ThingsBoard? Enterprise, bagus telemetry — tapi cross-domain chain lo yang nge-build. AWS IoT? Powerful, tapi biaya dan kompleksitas bikin pilot kebun 2 hektar jadi proyek 6 bulan. Petani Indonesia butuh: **satu bahasa event**, **notifikasi WA**, **demo jalan sebelum hardware lengkap**.”

---

## Scene 3 — Solution intro (0:45–1:30)

**VIS:** Brand slate Next-IOT + NextGrow. Screen record Web HQ: mesh graph nodes pulse. Popup notifikasi Fonnte/WA (mock UI, label “ilustrasi”).

**B-roll:** Docker Compose `healthy` health check; Swagger `/docs` mesh endpoints.

**MUS:** Lift — beat masuk, major chord.

**VO:**  
“Next-IOT Universal Mesh — platform IoT yang nge-unify **enam domain**: sensor, vision, motion, actuator, security, UI. Satu event bus, satu workflow engine, multi-tenant, self-host friendly. Bukan cloud lock-in demo — lo bisa jalanin di laptop dulu, scale ke server kebun nanti.”

---

## Scene 4 — Demo scenario: Farm Pest Response (1:30–2:30)

**VIS:** Screen recording berurutan (speed 1.25x):

1. Dashboard / tactical map — device online  
2. Simulator CCTV publish `motion_detected` (terminal log atau UI)  
3. Workflow execution log — status `success`  
4. Flutter field app / notification toast  
5. Clip drone CGI atau stock “sprayer field” (label **B-roll stock**)

**VO:**  
“Scenario: **Farm Pest Response** — preset workflow bawaan platform. CCTV deteksi motion, confidence tinggi. Event masuk domain **vision**. Workflow listener match rule tenant lo. Device resolver pilih drone terdekat capability `can_fly_to`. Dispatch fly-to, trigger sprayer, kirim notifikasi ke petani. Correlation ID nyatet di database — lo bisa audit: trigger jam berapa, action apa, hasilnya apa. Semua ini sudah divalidasi pytest end-to-end di repo.”

**On-screen text (ID):**  
`vision/motion_detected` → `dispatch_device` → `trigger_device` → `notification`

---

## Scene 5 — Technical quick-tour (2:30–3:30)

**VIS:** Animated Mermaid (export dari `01-architecture.md`): architecture overview + event flow. Cut ke editor: snippet `MeshWorkflowDefinition` JSON singkat. Flash commit hash `5f9ef89` AI Copilot.

**B-roll:** pytest green bar “14 passed” Step 8C; Alembic `040`.

**MUS:** Neutral tech — lo-fi beat, medium.

**VO:**  
“Di balik layar: **Mesh Event Publisher** persist ke Postgres, fan-out Redis, MQTT topic per tenant. Workflow DSL divalidasi Pydantic — no loose JSON. **Device resolver** pakai capability, zone, haversine nearest-to. Enam **in-process simulators** — CCTV, sprayer, cyberdeck, gate, weather, smartwatch — jadi QA bisa jalan tanpa LILYGO. Step 8C nambah **AI Copilot**: prompt Bahasa Indonesia → workflow JSON, mock mode tanpa API key. Plus camera gateway stub dan analytics CSV. API suite? **584** test case terkumpul; modul baru Step 8C: **14 lulus**.”

---

## Scene 6 — Impact + CTA (3:30–4:30)

**VIS:** Founder / engineer to camera (optional). Overlay teks: “Pilot terbatas — 10 kebun kopi Indonesia”. QR code landing NextGrow (placeholder URL). Form waitlist mockup.

**MUS:** Warm outro, fade under VO.

**VO:**  
“Kami percaya Indonesia butuh **ecosystem IoT sendiri** — bukan sekadar resell gateway barat. Next-IOT sudah business-ready untuk pilot: smart farming, security, wearable ops. **NextGrow** buka slot pilot terbatas: onboarding simulator-first, hardware menyusul. Kalau lo founder kebun, CTO agtech, atau distributor IoT — scan QR atau DM, kita jadwalkan demo live Docker plus workflow custom.”

**On-screen:**  
`hubungi@nextgrow.id` *(ganti dengan kontak riil sebelum publish)*  
`docs/content/mesh-demo/`

---

## Scene 7 — Credit + end card (4:30–5:00)

**VIS:** Logo Next-IOT + NextGrow. Link GitHub / docs. Subscribe animation.

**VO:**  
“Next-IOT — The First Indonesian Universal IoT Ecosystem. Built with FastAPI, Flutter, LVGL, pytest, and a lot of coffee. Follow NextGrow for pilot updates. Sampai jumpa di kebun — versi digital dulu.”

**MUS:** Outro sting 3 detik, cut silence.

---

## Production checklist

- [ ] Label **ilustrasi** di WA notification & persona Pak Hendra (jika dipakai di cut extended)  
- [ ] Screen record 1080p, font min 16px untuk mobile crop  
- [ ] Captions ID (burn-in or SRT) — wajib untuk Reels/TikTok  
- [ ] Verify stats before publish: pytest count, migration head, commit hashes  
- [ ] Music: royalty-free, mood notes above  

**Estimated word count VO:** ~1,050 words ≈ 4–5 menit @ 130 wpm Indonesian conversational pace.

---
marp: true
theme: default
paginate: true
title: Next-IOT Series A Pitch Deck
description: Universal IoT Mesh for Smart Farming Indonesia
---

<!-- slide 1 -->
# Next-IOT
## Universal IoT Mesh for Smart Farming Indonesia

**Tagline:** Satu platform — sensor, AI, workflow, hardware siap pakai.

**Founder:** Prayogi  
**Contact:** hello@next-iot.id  
**Round:** Series A — **$2M**

[Visual: Logo Next-IOT centered on gradient hijau-kopi; footer dengan URL platform.next-iot.id dan QR trial 14 hari.]

Next-IOT membantu petani dan perkebunan menaikkan yield, menurunkan biaya operasional, dan mengotomatisasi irigasi serta deteksi hama dengan platform IoT terbuka yang sudah production-grade. Deck ini merangkum masalah pasar, solusi mesh universal, model bisnis, traction teknis, dan penggunaan dana untuk 18 bulan ke depan.

---

<!-- slide 2 -->
# Problem

Petani dan operator perkebunan di Indonesia kehilangan hingga **30% yield** karena tiga celah sistemik yang saling memperparah.

**Telat irigasi:** keputusan siram masih manual; tanah kering terdeteksi setelah kerusakan. **Hama terlambat:** scouting mingguan, bukan real-time; serangan Spodoptera dan jamur menyebar sebelum tindakan. **Data manual:** catatan buku/spreadsheet tidak terhubung ke actuator atau notifikasi.

[Visual: Split screen — kiri tanaman layu + soil crack; tengah daun berlubang hama; kanan buku catatan basah + WhatsApp chat berantakan. Overlay stat “-30% yield”.]

Dampak ekonomi: wasted water, over-fertilize, panic hiring, dan kehilangan premium quality untuk export coffee/palm. Solusi point-solution (sensor saja, app saja) gagal karena tidak menutup loop **sense → decide → act → notify** dalam satu tenant.

---

<!-- slide 3 -->
# Market Opportunity

| Layer | Size | Notes |
|-------|------|-------|
| **TAM** | Rp 450T | Agribusiness Indonesia (food, estate, horticulture) |
| **SAM** | Rp 65T | Global IoT in agriculture (hardware + software + services) |
| **SOM** | Rp 2,5T | Indonesia IoT farming addressable in 3–5 years |

[Visual: Funnel chart TAM → SAM → SOM dengan highlight Indonesia map + crop icons (kopi, sawit, padi).]

Driver: kebutuhan traceability export, tekanan ESG air/energy, dan generasi operator yang expect mobile-first + Bahasa Indonesia. Next-IOT fokus SOM dengan **kit hardware + SaaS + enterprise white-label**, bukan generic IoT horizontal.

---

<!-- slide 4 -->
# Solution — Universal Device Mesh

Arsitektur **cross-domain mesh** menghubungkan sensor, vision, motion, actuator, dan UI notification dalam satu graph workflow — bukan silo per vendor.

- **Sensor + Vision + Motion + Actuator** terintegrasi via mesh events  
- **AI Copilot NL** — petani setup rule dalam Bahasa Indonesia  
- **Visual Workflow Builder** — no-code, versioning, approval, marketplace template  

[Visual: Gunakan `visual-assets/mesh-architecture.svg` — node Sensor → Condition → Action → Notify.]

Defensible layer: tenant isolation, workflow deep (version/approval/analytics), firmware OTA, dan template marketplace yang mempercepat time-to-value dari minggu menjadi hari.

---

<!-- slide 5 -->
# Product Demo

Platform live: **https://platform.next-iot.id** (atau staging demo tenant).

**Dashboard HQ:** devices, alarms, agriculture farms, analytics.  
**Workflow Builder:** drag-drop trigger → condition → action + AI generate.  
**Marketplace:** template irigasi, pest, greenhouse — download ke workspace.  
**Mobile / WA:** alert ke operator lapangan.

[Visual: 3-up screenshot mock — dashboard KPI, workflow canvas, marketplace grid. Annotate arrows “14-day trial”.]

Demo narrative untuk investor: login → import template “Smart Irrigation Kopi” → bind sensor → simulate threshold → WhatsApp alert → chart yield. Placeholder screenshot until marketing capture session.

---

<!-- slide 6 -->
# Business Model

**1. SaaS subscription** — Rp 500rb – 5jt/bulan per tenant (Starter → Pro → Enterprise).  
**2. Hardware kit** — 6 SKU (soil, pond, gateway, switch, camera edge, weather); **margin 40%+**.  
**3. Enterprise license** — white-label + SLA 99.9%, Rp 100jt+ ACV.

[Visual: Stacked bar revenue mix Y3 — 55% SaaS, 35% hardware, 10% enterprise.]

Expansion revenue: additional devices, premium analytics, reseller margin share, and professional services for plantation rollout (install + agronomy playbook).

---

<!-- slide 7 -->
# Traction

- **44** Alembic database migrations — production-grade schema evolution  
- **666+** automated tests (API, web, firmware paths)  
- **6** hardware kit SKU documented + BOM ready  
- **Universal Mesh** architecture shipped (workflows, marketplace, analytics)  
- **[TODO]** Named pilot customer + MRR this month  

[Visual: Timeline “2024–2026” dengan milestone engineering; badge “Production-ready platform”.]

Early GTM: design partner conversations (coffee estate, palm oil SMB). Fundraise accelerates sales hire + field kit inventory.

---

<!-- slide 8 -->
# Competition

**2×2 matrix:** Price (low → high) vs Features (simple → comprehensive)

| | Simple | Comprehensive |
|---|--------|-----------------|
| **Low price** | — | **Next-IOT** |
| **Mid** | TaniHub | eFishery (fish-only) |
| **High** | — | Habibi Garden |

[Visual: `visual-assets/competition-matrix.svg` with quadrant labels.]

Moat: Bahasa Indonesia copilot + mesh workflow + integrated kits + local support — not just dashboards or single-crop vertical SaaS.

---

<!-- slide 9 -->
# Go-to-Market

**1. Direct enterprise sales** — coffee plantation, palm oil, horticulture export.  
**2. Reseller tier** — Bronze / Silver / Gold (margin + certification).  
**3. Content marketing** — NextGrow blog + YouTube Shorts (education → trial).

[Visual: Funnel diagram Awareness → Trial → Paid → Expand; icons WA, YouTube, field visit.]

Playbook: 14-day trial → template marketplace → 1 kit upsell → Pro subscription. Enterprise: multi-farm tenant + custom SLA.

---

<!-- slide 10 -->
# Team

**Founder:** Prayogi — product + engineering vision, IoT platform builder.

**Series A hiring plan:**  
- 2 Backend engineers  
- 1 Frontend engineer  
- 1 Hardware engineer  
- 1 Sales lead  
- 1 Agronomist advisor (part-time → full-time)

[Visual: Org chart founder center; advisor ring; “18-month headcount ~12”.]

Culture: ship production code weekly; field visits monthly; Bahasa Indonesia-first UX.

---

<!-- slide 11 -->
# Financial Projection (3 Year)

| Year | ARR | Drivers |
|------|-----|---------|
| **Y1** | Rp 500jt | 10 pilot customers |
| **Y2** | Rp 3M | 60 customers + 500 kits |
| **Y3** | Rp 15M | 300 customers + 3k kits + 1–2 enterprise |

[Visual: Hockey stick ARR chart; secondary line kit units sold.]

Assumptions detailed in `financial-projection.md` — base case ARPU Pro ~Rp 500rb, churn <2% monthly target post-PMF.

---

<!-- slide 12 -->
# The Ask — $2M Series A

**Use of funds:** 40% engineering · 30% GTM · 20% hardware R&D · 10% ops  

**18-month milestones:** Rp 10M ARR · 100 paying customers · 3 enterprise logos  

**Exit path:** Series B in 24–30 months on ARR + logo traction.

[Visual: Pie chart use of funds; milestone checklist; contact hello@next-iot.id + calendar link.]

Thank you — let's modernize Indonesian farming with open IoT mesh.

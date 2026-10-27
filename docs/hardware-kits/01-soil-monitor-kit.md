# Kit #1 — Soil Monitor Kit

**SKU:** `NIOT-K01-SOIL`  
**Target:** Petani kopi, kakao, sayur **2–10 hektar**  
**Launch:** Q4 2026  
**Harga jual:** **Rp 1.800.000** (HPP ±Rp 900.000 · margin ~50%)

---

## Hero image (placeholder)

Foto produk: enclosure IP66 di tiang plot, 4 probe moisture di tanah, panel solar 10W; overlay UI Next-IOT menampilkan moisture + pH + NPK. *Shoot setelah sample kit assembly.*

---

## What's in the box

- [ ] 1× ESP32-S3 dev board (Next-IOT pre-provisioned)
- [ ] 4× capacitive soil moisture sensor + kabel 3 m
- [ ] 1× modul multi-NPK (RS485/Analog — sesuai batch)
- [ ] 1× pH probe + conditioning board
- [ ] 1× DHT22 (temp & humidity ambient)
- [ ] 1× solar 10W + MPPT charger + 2× Li-ion 18650 (pre-installed)
- [ ] 1× enclosure IP66 + bracket tiang
- [ ] Kit konektor waterproof + tie wrap
- [ ] Quickstart ID (1 lembar) + sticker QR aktivasi NextGrow
- [ ] Kartu garansi 1 tahun

---

## BOM estimasi (Alibaba 2026)

| Komponen | Est. USD |
| --- | --- |
| ESP32-S3 | $4 |
| Moisture ×4 | $3 |
| Multi-NPK module | $8 |
| pH probe + board | $12 |
| DHT22 | $2 |
| Solar 10W + MPPT + 18650×2 | $18 |
| Enclosure IP66 + mount | $5 |
| Kabel + connector | $3 |
| Shipping + packaging | $5 |
| **Total HPP** | **~$60 (±Rp 900.000)** |

---

## Spec sheet teknis

| Parameter | Spesifikasi |
| --- | --- |
| MCU | ESP32-S3, WiFi 802.11 b/g/n |
| Input power | Solar 10W; battery 18650 ×2 (~7 Ah equivalent) |
| Moisture | Capacitive, 0–100% VWC (kalibrasi per soil type) |
| NPK | Indicative index (bukan lab SNI — untuk trend) |
| pH | Range 3–9, akurasi ±0,2 pH (dengan kalibrasi 2-point) |
| Temp/humidity | DHT22, −40–80°C / 0–100% RH |
| Enclosure | IP66, −20–60°C operating |
| Uplink | MQTT TLS → Next-IOT tenant (EMQX) |
| Mesh domain | `sensor` — `reading_update`, `threshold_exceeded` |
| OTA | Supported via Next-IOT firmware channel |

**Firmware:** Next-IOT ESP32 SDK **pre-flash dari pabrik** — claim token + pairing QR.

---

## Quickstart instalasi (1 halaman)

1. Pasang enclosure di tiang plot (tinggi 1,2 m, hindari shadow panel).
2. Tanam 4 probe moisture pada kedalaman 15–20 cm (representatif zona irigasi).
3. Power on — LED pairing blink → scan QR di kartu → app Field / Web HQ.
4. Assign **device profile** `env_sensor` / agriculture profile tenant.
5. Set threshold moisture di Rules atau workflow **Smart Irrigation Extended** (mesh preset).
6. Verifikasi telemetry di dashboard < 5 menit.

---

## Use case & ROI (ilustrasi)

**Persona ilustrasi:** Pak Hendra, kopi 5 ha, 3 plot.

| Skenario | Tanpa monitor | Dengan K01 |
| --- | --- | --- |
| Kekeringan tidak terdeteksi 3 hari | Potensi loss Rp **10.000.000** / musim (contoh ilustrasi) | Alert `threshold_exceeded` → irigasi / WA |
| Over-irrigation | Biaya listrik + air | Rule cancel jika hujan ( + K06 optional ) |

**Payback kasar:** 1× musim cegah kekeringan parah → **>5×** harga kit (ilustrasi, bukan jaminan hasil panen).

---

## Subscription & platform

| Plan | Harga | Fitur relevan |
| --- | --- | --- |
| **Starter** | Rp 50.000/bulan | Telemetry 90 hari, 3 rules, WA notif basic |
| **Pro** | Rp 200.000/bulan | Mesh workflow, analytics export, multi-user |

Aktivasi wajiu untuk cloud; device tetap milik customer.

**Integrasi:** Smart Farming hub Next-IOT — sensor tile, irrigation, NDVI (kamera terpisah).  
Deep link docs: `apps/api` agriculture vertical · mesh preset `smart_irrigation_extended`.

---

## CTA

- **Beli / pre-order:** NextGrow (lihat [`09-marketing-assets.md`](09-marketing-assets.md))
- **Pilot software dulu:** simulator mesh — tanpa hardware

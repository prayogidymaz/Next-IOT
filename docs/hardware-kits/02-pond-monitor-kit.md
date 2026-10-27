# Kit #2 — Pond Monitor Kit

**SKU:** `NIOT-K02-POND-B` (Basic) · `NIOT-K02-POND-P` (Pro + 4G)  
**Target:** Tambak udang vaname, lele, nila **1–5 hektar**  
**Launch:** Q1 2027

| Variant | HPP | Harga jual | Margin |
| --- | --- | --- | --- |
| **Basic** (WiFi) | ~$123 (±Rp 1,8 jt) | **Rp 3.500.000** | ~48% |
| **Pro** (+ 4G fallback) | ~$148 (±Rp 2,2 jt) | **Rp 4.500.000** | ~51% |

---

## Hero image (placeholder)

Tambak dengan floating probe DO/pH, enclosure IP68 di pinggir kolam, notifikasi WhatsApp “DO KRITIS 3.2 mg/L” di mockup HP. *Ilustrasi — bukan foto kejadian nyata.*

---

## What's in the box

- [ ] ESP32-S3 + enclosure **IP68**
- [ ] DO (dissolved oxygen) sensor + conditioning board
- [ ] pH probe industrial
- [ ] Salinity probe
- [ ] DS18B20 temperature probe
- [ ] Relay 4-channel (kontrol aerator)
- [ ] Solar 20W + LiFePO4 battery pack
- [ ] (Pro only) 4G modem LTE Cat-1 + SIM tray (SIM tidak included)
- [ ] Manual bilingual + QR aktivasi

---

## BOM estimasi

| Komponen | Basic USD | Pro (+) |
| --- | --- | --- |
| ESP32-S3 + IP68 box | $12 | — |
| DO sensor + conditioning | $35 | — |
| pH industrial | $18 | — |
| Salinity | $12 | — |
| DS18B20 | $3 | — |
| Relay 4-ch | $8 | — |
| 4G modem | — | +$25 |
| Solar 20W + LiFePO4 | $35 | — |
| **Total HPP** | **~$123** | **~$148** |

---

## Spec sheet teknis

| Parameter | Spesifikasi |
| --- | --- |
| DO | 0–20 mg/L, akurasi **±0,1 mg/L** (setelah kalibrasi) |
| pH | 0–14, industrial probe |
| Salinity | PSU / ppt (sensor batch-dependent) |
| Temp | DS18B20 ±0,5°C |
| Relay | 4× 10A @ 250VAC — **aerator auto-trigger** via Rule Engine / mesh |
| Connectivity | WiFi; Pro: **4G fallback** auto jika WiFi down |
| Alarm latency target | **WhatsApp < 30 detik** (Fonnte/gateway tenant) |
| Mesh | `sensor` + `actuator` (relay) cross-workflow |

**Killer feature:** DO alarm WA — **1× mass mortality** tambak bisa Rp **100–500 juta** kerugian (range ilustrasi industri; bukan klaim legal).

---

## Aerator automation

- Rule: IF DO < 4.0 mg/L THEN relay CH1 ON (aerator) + notification Pro
- Mesh: `threshold_exceeded` → workflow → `trigger_device` open aerator
- Compatible **Smart Farming AquaMonitor** sub-vertical (roadmap UI)

---

## ROI (ilustrasi)

| Event | Kerugian potensial | Payback vs kit Pro |
| --- | --- | --- |
| 1× gagal panen massal (DO drop malam) | Rp 100–500 jt | **≤ 1 musim** |
| 10× early warning kecil | Rp 5–15 jt kumulatif | **< 1 tahun** |

*Angka edukasi — audit lapangan per tambak bervariasi.*

---

## Subscription

- **Starter:** monitoring + 1 rule DO (Rp 50rb/bln)
- **Pro:** mesh workflow + 4G cloud routing + priority support (Rp 200rb/bln)

---

## CTA

Pre-order Pond Pro Bundle dengan Weather Station → [`07-pricing-reseller.md`](07-pricing-reseller.md) (Rp 6.300.000)

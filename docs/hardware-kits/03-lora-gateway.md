# Kit #3 — LoRa Gateway

**SKU:** `NIOT-K03-LORA`  
**Target:** Perkebunan **50+ ha** (sawit, karet, kopi korporat), area minim internet  
**Launch:** Q1 2027  
**Harga jual:** **Rp 2.500.000** (HPP ±Rp 990.000 · margin ~60%)

---

## Hero image (placeholder)

Gateway di tiang 6 m, antenna directional, peta coverage radius di slide pitch. Background kebun sawit/kopi.

---

## What's in the box

- [ ] ESP32-S3 + **SX1262** LoRa 868 MHz (ITU Region 1 — Indonesia)
- [ ] Antenna directional 5 dBi + coax N-type/SMA
- [ ] Enclosure IP66 outdoor
- [ ] Solar 30W + LiFePO4
- [ ] Pole mount bracket
- [ ] Quickstart + QR tenant gateway claim

---

## BOM estimasi (~$66)

| Item | USD |
| --- | --- |
| ESP32-S3 + SX1262 | $15 |
| Antenna 5 dBi + cable | $8 |
| Enclosure IP66 | $8 |
| Solar 30W + LiFePO4 | $30 |
| Pole mount | $5 |
| **Total** | **~$66** |

---

## Spec sheet

| Parameter | Nilai |
| --- | --- |
| Frequency | 865–867 MHz (config compliance Indonesia) |
| Coverage | **5–15 km** line-of-sight; 1–3 km hilly plantation |
| Backhaul | WiFi / Ethernet (optional module) → MQTT cloud |
| Capacity | **≤ 100 LoRa nodes** per gateway (recommended) |
| Mesh platform | Device LoRa → gateway → **Next-IOT cloud**; multi-hop gateway optional roadmap |
| Power | Solar 30W continuous duty cycle |

---

## Use cases

1. **Perkebunan korporat:** ratusan node moisture tanpa SIM per titik.
2. **Upgrade path:** WiFi-only K01 nodes → add LoRa radio module (SKU future).
3. **Pemerintah / BPBD:** area minim internet — backhaul sat optional partner.

Compatible dengan **AgriLoraGateway** model di platform (`agriculture` vertical).

---

## Pairing dengan kit lain

- **Starter Farm Bundle:** K01 + K03 → Rp 3.870.000 ([`00-master-catalog.md`](00-master-catalog.md))

---

## CTA

Diskusi site survey coverage — NextGrow B2B (Gold reseller untuk korporat).

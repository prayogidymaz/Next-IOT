# Kit #6 — Weather Station Kit

**SKU:** `NIOT-K06-WX`  
**Target:** Kebun **5+ ha** microclimate (kopi, hortikultura, nursery)  
**Launch:** Q2 2027  
**Harga jual:** **Rp 3.000.000** (HPP ±Rp 1.350.000 · margin ~55%)

---

## Hero image (placeholder)

Station di open area plot: anemometer, rain gauge, radiation shield BME280, pole 2 m.

---

## What's in the box

- [ ] ESP32-S3 hub
- [ ] BME280 (temp, humidity, pressure)
- [ ] Anemometer (speed + direction)
- [ ] Rain gauge tipping bucket
- [ ] UV index sensor
- [ ] Solar radiation sensor
- [ ] Solar 20W + battery
- [ ] Outdoor enclosure + pole kit 2 m
- [ ] Manual siting (jarak dari pohon/minimal obstacle)

---

## BOM (~$90)

| Item | USD |
| --- | --- |
| ESP32-S3 | $4 |
| BME280 | $5 |
| Anemometer | $18 |
| Rain gauge | $12 |
| UV sensor | $6 |
| Solar radiation | $8 |
| Solar 20W + battery | $25 |
| Enclosure + pole | $12 |
| **Total** | **~$90** |

---

## Spec sheet — 6-in-1 microclimate

| Sensor | Measure |
| --- | --- |
| BME280 | Temp, RH, pressure (hPa) |
| Anemometer | Wind speed & direction |
| Rain gauge | mm/h cumulative |
| UV | Index 0–11+ |
| Solar radiation | W/m² (sensor tier) |

**Hybrid intelligence:** telemetry lokal + **BMKG API** cross-reference (tenant config) untuk forecast hujan.

---

## Workflow examples

- “Hujan 70% besok” → cancel irrigation schedule (mesh + rules)
- Frost alert → notification + valve drain protocol (custom workflow)
- Correlate with **Analytics energy** (K04 pump runtime vs weather)

Compatible Smart Farming hub analytics + export CSV Step 8C.

---

## CTA

**Pond Pro Aqua Bundle** dengan K02 Pro → Rp 6.300.000 ([`07-pricing-reseller.md`](07-pricing-reseller.md))

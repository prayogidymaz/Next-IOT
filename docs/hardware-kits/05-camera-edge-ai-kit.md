# Kit #5 — ESP32-CAM Edge AI

**SKU:** `NIOT-K05-CAMAI`  
**Target:** Security + deteksi hama outdoor, kebun **2–10 ha**  
**Launch:** Q1 2027  
**Harga jual:** **Rp 1.500.000** (HPP ±Rp 705.000 · margin ~53%)

---

## Hero image (placeholder)

ESP32-CAM di tiang dengan IR night vision, bounding box “motion/pest” overlay, snapshot di dashboard Camera Gateway.

---

## What's in the box

- [ ] ESP32-CAM (OV2640)
- [ ] IR LED array night vision
- [ ] Enclosure IP65 outdoor
- [ ] Solar 10W + battery pack
- [ ] microSD 32 GB (edge buffer)
- [ ] Adjustable mounting bracket
- [ ] Pre-flash firmware edge AI lite + Next-IOT agent

---

## BOM (~$47)

| Item | USD |
| --- | --- |
| ESP32-CAM OV2640 | $10 |
| IR LED array | $4 |
| Enclosure IP65 | $8 |
| Solar 10W + battery | $15 |
| microSD 32GB | $5 |
| Mount bracket | $5 |
| **Total** | **~$47** |

---

## Spec sheet

| Parameter | Spesifikasi |
| --- | --- |
| Image | OV2640 UXGA, snapshot JPEG |
| Edge AI | **YOLOv8-n lite** — motion / pest / intruder class (model OTA) |
| Storage | microSD ring buffer 7 hari local |
| Uplink | WiFi snapshot → **Camera Gateway** Step 8C (`/api/v1/cameras`) |
| Mesh | `vision/motion_detected` → workflow **Farm Pest Response** |
| Battery life | **~7 hari** idle / **~2 hari** continuous motion (estimasi solar) |

---

## Cross-domain mesh (differentiator)

1. K05 detect motion confidence ≥ 0.75  
2. Platform publish mesh event  
3. Workflow dispatch drone / sprayer (simulator atau hardware nyata)  
4. WA notification petani  

Ini **bukan** CCTV cloud generic — terintegrasi **Universal Mesh**.

---

## CTA

Bundle Smart Farm Complete — lihat [`07-pricing-reseller.md`](07-pricing-reseller.md)

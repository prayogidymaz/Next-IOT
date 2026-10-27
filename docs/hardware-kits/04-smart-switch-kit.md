# Kit #4 — Smart Switch 4-Channel

**SKU:** `NIOT-K04-SW4`  
**Target:** Smart home DIY, actuator kebun, UMKM lighting/pompa  
**Launch:** Q4 2026  
**Harga jual:** **Rp 650.000** (HPP ±Rp 285.000 · margin ~56%)

---

## Hero image (placeholder)

Modul DIN rail 4 relay, label CH1–CH4 (Lampu, Pompa, Aerator, Valve), screenshot app Next-IOT toggle.

---

## What's in the box

- [ ] ESP32-S3
- [ ] 4-channel relay **220 VAC 10 A** (per channel)
- [ ] Enclosure DIN rail + box plastik
- [ ] WiFi antenna external
- [ ] Screw terminal + kabel warning label
- [ ] Manual **ID + EN** instalasi 1–2 jam

---

## BOM (~$19)

| Item | USD |
| --- | --- |
| ESP32-S3 | $4 |
| Relay 4-ch 10A | $6 |
| DIN enclosure | $5 |
| Antenna | $1 |
| Kabel + terminal | $3 |
| **Total** | **~$19** |

---

## Spec sheet

| Parameter | Spesifikasi |
| --- | --- |
| Supply | 220 VAC input (instalasi oleh teknisi berlisensi) |
| Per channel | **10 A max**, resistive load recommended |
| Total load | **≤ 2200 W** combined (derating if inductive) |
| Control | App Next-IOT, Rules, mesh `actuator/state_changed` |
| Safety | NO/COM per channel; **tidak** untuk motor VFD berat tanpa contactor external |

---

## Use cases

- Lampu greenhouse / drying bed kopi
- Pompa irigasi kecil / aerator backup
- Valve solenoid 24 VDC (via power supply external)
- **Rule Engine:** if moisture < X → relay ON 15 min

**Roadmap:** NextHome vertical (smart home bundle) — compatible profile `smart_switch`.

---

## CTA

Entry point termurah ekosistem Next-IOT — pair dengan subscription Starter Rp 50rb/bln.

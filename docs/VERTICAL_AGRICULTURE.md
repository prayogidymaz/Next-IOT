# Smart Agriculture Vertical (Step 11)

LoRa-first monitoring for Indonesian plantations: kopi, sawit, padi, hortikultura.

## Architecture

- **API:** `/api/agriculture/*` (tenant-scoped farms, plots, LoRa sensors/gateways, irrigation, disease alerts, yield).
- **Data:** Migration `033` — farms, plots, sensors, gateways, valves, irrigation logs, disease alerts, crop calendar, yield.
- **Edge:** Firmware Studio templates (`agri_*.cpp`) for soil, weather, valve, NPK nodes.
- **Jobs:** Disease scan every 30 minutes; auto-irrigation uses BMKG forecast cache + soil moisture thresholds.

See `docs/agriculture/` for hardware and onboarding.

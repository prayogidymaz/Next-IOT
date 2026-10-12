# Agriculture API Reference

Base path: `/api/agriculture`

| Area | Methods |
|------|---------|
| Farms | `GET/POST /farms`, `GET/PUT/DELETE /farms/{id}`, `GET .../overview` |
| Plots | `GET/POST /farms/{id}/plots`, `GET/PUT /plots/{id}`, `GET .../heatmap` |
| Sensors | `GET/POST /farms/{id}/sensors`, readings, calibrate, battery-history |
| Gateways | `GET/POST /gateways`, `GET /gateways/{id}/stats` |
| Irrigation | valves per plot, open/close, schedule, `POST .../irrigation/auto-run` |
| Disease | alerts list, acknowledge, resolve, 7-day forecast |
| Yield & analytics | calendar, yield records, water/environmental/cost analytics |

Super admin: `/api/v1/super-admin/agriculture/stats`, `/firmware-fleet`.

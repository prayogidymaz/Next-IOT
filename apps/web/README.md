# Tuya OS Smart Home Dashboard (Next.js)

Glassmorphism smart-home UI with Framer Motion micro-interactions.

## Run locally

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) for the **public marketing landing page**.

Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard) for the **Control Center** demo.

## Routes

| Path | Description |
| --- | --- |
| `/` | Public marketing landing (`components/marketing/PublicLandingPage.tsx`) |
| `/dashboard` | Internal smart-home dashboard (`components/TuyaSmartDashboard.tsx`) |
| `/cyberdeck` | Cyberdeck LoRa PTT tactical console (`components/cyberdeck/CyberdeckConsole.tsx`) |

## Main components

- `components/marketing/PublicLandingPage.tsx` — enterprise landing UI
- `components/marketing/MarketingFeaturesBento.tsx` — 5-module bento grid
- `components/marketing/DashboardShowcase.tsx` — embedded live demo frame
- `components/TuyaSmartDashboard.tsx` — glassmorphism device grid (supports `embedded` prop)

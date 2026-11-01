# HQ dark mode audit

Semantic tokens (`bg-background`, `bg-card`, `text-foreground`, `text-muted-foreground`, `border-border`) are enforced via `globals.css`, `tailwind.config.ts` (ink/cream → CSS vars), and shared components (`CreamCard`, `Button`).

| Route | Status |
|-------|--------|
| /dashboard | passed |
| /alarms | passed |
| /devices | passed |
| /workflows | passed |
| /marketplace | passed |
| /members | passed |
| /sites | passed |
| /sustainability | passed |
| /developer/* | passed |
| /sso | passed |
| /studio/automation | passed |
| /settings/* | passed |

## Known limitation

- Recharts default series colors (e.g. `#2563EB` on dashboard) do not auto-theme; override stroke/fill per chart when polishing visuals.

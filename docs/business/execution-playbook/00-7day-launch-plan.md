# 7-Day Launch Plan — Next-IoT Series A Outreach

**Goal:** Deck live, landing live, demo video published, first 10 investor emails sent.  
**Owner:** Prayogi · **Week start:** [set date]

---

## Day 1 — Assets export + landing deploy

- [ ] Export pitch deck PDF from Marp (`docs/business/pitch-deck/pitch-deck.md` → PDF via VS Code Marp extension)
- [ ] Export one-pager PDF (`docs/business/one-pager.html` → print to PDF)
- [ ] Connect `apps/landing` to Vercel (GitHub integration, preview URL)
- [ ] Set env: `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_SITE_URL`, optional `NEXT_PUBLIC_GA_ID`
- [ ] Smoke-check: hero CTA → register, pricing, FAQ render mobile

## Day 2 — Domain + DNS

- [ ] Register **next-iot.id** (or fallback: nextiot.id / getnextiot.com)
- [ ] Vercel: add domain, verify DNS (A/CNAME per Vercel panel)
- [ ] Platform subdomain plan: `platform.next-iot.id` → production/staging
- [ ] Email SPF/DKIM prep for `@next-iot.id` (Day 7 dependency)

## Day 3 — Demo video shoot (5 min)

- [ ] Script: `docs/business/video-scripts/demo-video-5min.md`
- [ ] Tools: OBS Studio (1080p screen + optional face cam), phone B-roll kebun
- [ ] Record: Copilot NL, workflow mesh, marketplace, WhatsApp alert mock
- [ ] Raw footage → folder `media/raw/demo-YYYY-MM-DD/`

## Day 4 — Edit + YouTube

- [ ] DaVinci Resolve: cut to 4:30–5:00, captions ID, lower-third Next-IoT
- [ ] Export MP4 H.264, upload YouTube (unlisted → public when ready)
- [ ] Embed URL noted for landing `#demo` section update

## Day 5 — Investor list (30 targets)

Research partners + thesis fit; log in `02-investor-tracker.csv`.

**Indonesia / SEA funds (starting list):**

| Fund | Focus |
|------|--------|
| East Ventures | SEA early stage |
| AC Ventures | Indonesia tech |
| Alpha JWC Ventures | Indonesia |
| Monk's Hill Ventures | SEA |
| Sequoia Capital SEA | Growth/early |
| 500 Global | Accelerator + seed |
| Golden Gate Ventures | SEA |
| Vertex Ventures SEA | Enterprise/tech |
| MDI Ventures | Telkom-linked |
| BRI Ventures | Corporate VC |
| Mandiri Capital | Corporate VC |

- [ ] Add 19 more angels / micro-VCs (agri, climate, IoT)
- [ ] LinkedIn + email discovery per partner

## Day 6 — Outreach drafts

- [ ] Personalize opening line per fund (portfolio company, recent article)
- [ ] Attach: PDF deck + one-pager; link landing + YouTube
- [ ] Use templates: `01-investor-outreach-templates.md`
- [ ] Calendly 20-min slot ready

## Day 7 — Send batch 1

- [ ] Send **10 emails** (mix Template A/B/C)
- [ ] Update tracker: Status = Sent, Email Sent Date
- [ ] Follow-up rule: +5 business days if no reply
- [ ] Daily standup: replies, meetings booked, objections log

---

**Success criteria (end of week):** Landing on custom domain, video public, 10 outreach sent, ≥2 positive replies or meetings.

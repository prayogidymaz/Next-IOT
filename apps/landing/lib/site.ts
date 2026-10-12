export const APP_URL = process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000";
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3002";

export const PRICING_PLANS = [
  { code: "free", name: "Free", price: "Rp 0", period: "/bulan", devices: "5 devices", highlight: false },
  { code: "starter", name: "Starter", price: "Rp 499rb", period: "/bulan", devices: "50 devices", highlight: false },
  { code: "pro", name: "Pro", price: "Rp 1,99jt", period: "/bulan", devices: "500 devices", highlight: true },
  { code: "enterprise", name: "Enterprise", price: "Custom", period: "", devices: "Unlimited + SLA", highlight: false },
] as const;

export const FEATURES = [
  {
    emoji: "🧩",
    title: "Thing Model & Device Profile",
    body: "Validasi otomatis per metric — data bersih sejak edge.",
  },
  {
    emoji: "📡",
    title: "MQTT Broker + Security",
    body: "EMQX production-grade dengan Topic ACL per tenant.",
  },
  {
    emoji: "🤖",
    title: "Rule Engine aktif",
    body: "5 triggers, 7 action types, template Jinja2.",
  },
  {
    emoji: "📨",
    title: "Notification 5 Channel",
    body: "WhatsApp, Telegram, Email, FCM, SMS.",
  },
  {
    emoji: "🔧",
    title: "Firmware Studio",
    body: "Generate firmware ESP32 ready-to-flash dari browser.",
  },
  {
    emoji: "💳",
    title: "Billing Integrated",
    body: "Midtrans + Xendit, invoice otomatis + PPN 11%.",
  },
] as const;

export type UseCaseSlug = "farming" | "drone-sar" | "smart-building" | "industrial";

export const USE_CASES: Record<
  UseCaseSlug,
  { title: string; emoji: string; bullets: string[]; description: string }
> = {
  farming: {
    emoji: "🌾",
    title: "Smart Farming",
    description: "Tambak udang, sayuran organik, dan perkebunan skala menengah.",
    bullets: ["Monitoring sensor real-time", "Alarm threshold otomatis", "Laporan operasional harian"],
  },
  "drone-sar": {
    emoji: "🚁",
    title: "Drone & SAR",
    description: "Fleet monitoring dan mission planning untuk operasi SAR.",
    bullets: ["Live telemetry fleet", "Geofence & mission studio", "Notifikasi insiden prioritas"],
  },
  "smart-building": {
    emoji: "🏢",
    title: "Smart Building",
    description: "Energy management, HVAC, dan keamanan gedung terpadu.",
    bullets: ["Dashboard konsumsi energi", "Integrasi multi-sensor", "Automation rules siap pakai"],
  },
  industrial: {
    emoji: "🏭",
    title: "Industrial IoT",
    description: "Factory floor dan predictive maintenance untuk Industri 4.0.",
    bullets: ["OEE & uptime tracking", "Predictive alerts", "Audit trail compliance"],
  },
};

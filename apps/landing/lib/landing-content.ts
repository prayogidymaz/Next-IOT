export const TRUST_LOGOS = ["Kebun Kopi X", "Perkebunan Sawit Y", "Horti Nusantara", "Tambak Prima"] as const;

export const METRIC_CARDS = [
  { label: "6 kit siap pakai", sub: "Hardware + firmware OTA" },
  { label: "95% automated", sub: "Rule + workflow mesh" },
  { label: "30% yield increase*", sub: "*Target pilot; hasil bervariasi" },
] as const;

export const PAIN_POINTS = [
  {
    icon: "💧",
    title: "Irigasi reaktif",
    body: "Tanah sudah kering saat operator menyadari — yield turun dan biaya air membengkak.",
  },
  {
    icon: "🐛",
    title: "Hama terlambat",
    body: "Scouting manual tidak skala; serangan menyebar sebelum tindakan terkoordinasi.",
  },
  {
    icon: "📒",
    title: "Data terpisah",
    body: "Catatan lapangan, WhatsApp, dan spreadsheet tidak menggerakkan actuator otomatis.",
  },
] as const;

export const SOLUTIONS = [
  {
    icon: "🌐",
    title: "Mesh terintegrasi",
    body: "Sensor, kamera, actuator, dan notifikasi dalam satu workflow tenant-isolated.",
  },
  {
    icon: "🧠",
    title: "AI Copilot ID",
    body: "Setup aturan dalam Bahasa Indonesia — tanpa tim IT dedicated.",
  },
  {
    icon: "📊",
    title: "Analytics & alert",
    body: "Yield, anomaly, dan cost tracking dengan alert multi-channel termasuk WhatsApp.",
  },
] as const;

export const HOME_FEATURES = [
  { emoji: "🧠", title: "AI Copilot Bahasa Indonesia", body: "Generate workflow dari perintah natural language." },
  { emoji: "📊", title: "Smart Analytics", body: "Yield forecast, anomaly detection, dan cost savings." },
  { emoji: "🌐", title: "Universal Device Mesh", body: "Cross-domain events — sensor, vision, motion, actuator." },
  { emoji: "🎨", title: "Visual Workflow Builder", body: "No-code builder dengan versioning & approval." },
  { emoji: "🛒", title: "Marketplace Template", body: "Template irigasi, pest, greenhouse siap deploy." },
  { emoji: "🔌", title: "Edge Agent (ESP32 + OTA)", body: "Firmware studio + secure OTA updates." },
] as const;

export const HOW_IT_WORKS = [
  { step: "1", title: "Pasang sensor", body: "Dari kit Next-IoT atau hardware existing yang compatible." },
  { step: "2", title: "Setup di platform", body: "AI Copilot bantu konfigurasi dalam Bahasa Indonesia." },
  { step: "3", title: "Pantau + automate", body: "Dashboard real-time, alert, dan irigasi otomatis." },
] as const;

export const PRICING_TIERS = [
  {
    name: "Starter",
    price: "Gratis",
    period: "",
    bullets: ["1 kebun", "5 sensor", "Basic alert", "Community support"],
    cta: "Mulai Gratis",
    highlight: false,
  },
  {
    name: "Pro",
    price: "Rp 500rb",
    period: "/bulan",
    bullets: ["Unlimited device", "Advanced analytics", "AI Copilot", "1 user included"],
    cta: "Trial 14 Hari",
    highlight: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    bullets: ["Multi-tenant", "Dedicated support", "SLA 99.9%", "White-label option"],
    cta: "Hubungi Sales",
    highlight: false,
  },
] as const;

export const HARDWARE_KITS = [
  { name: "Soil Monitor", price: "from Rp 1,5jt", emoji: "🌱" },
  { name: "Pond Monitor", price: "from Rp 1,8jt", emoji: "🐟" },
  { name: "LoRa Gateway", price: "from Rp 2,2jt", emoji: "📡" },
  { name: "Smart Switch", price: "from Rp 850rb", emoji: "🔌" },
  { name: "Camera Edge AI", price: "from Rp 3,5jt", emoji: "📷" },
  { name: "Weather Station", price: "from Rp 2,8jt", emoji: "🌤️" },
] as const;

export const TESTIMONIALS = [
  { quote: "Plot kopi kami dapat alert kelembaban sebelum tanaman stress.", name: "Pak Hartono", role: "Petani kopi, Jawa Timur" },
  { quote: "Satu dashboard untuk 3 kebun — tim lapangan jauh lebih efisien.", name: "Ibu Sari", role: "Pemilik kebun horticulture" },
  { quote: "Template marketplace mempercepat rollout rekomendasi agronomi.", name: "Dr. Reza", role: "Agronomist advisor" },
] as const;

export const FAQ_ITEMS = [
  {
    q: "Berapa biaya setup awal?",
    a: "Starter gratis; Pro mulai Rp 500rb/bulan. Kit hardware optional mulai ~Rp 850rb.",
  },
  {
    q: "Perlu teknisi untuk install?",
    a: "Kit plug-and-play dengan panduan; enterprise rollout bisa dengan partner reseller certified.",
  },
  {
    q: "Compatible dengan sensor existing?",
    a: "Ya — MQTT/LoRa/WiFi profiles dapat dikonfigurasi via device profile.",
  },
  {
    q: "Bisa offline?",
    a: "Edge agent buffer telemetry; sync saat koneksi kembali (tergantung konfigurasi site).",
  },
  {
    q: "Data saya aman di mana?",
    a: "Tenant-isolated di cloud Indonesia-ready; enkripsi in-transit; enterprise VPC optional.",
  },
  {
    q: "Garansi hardware?",
    a: "12 bulan manufacturing defect; RMA via partner/reseller.",
  },
  {
    q: "Bisa integrasi dengan WhatsApp?",
    a: "Ya — alert dan approval flow mendukung WhatsApp Business API channel.",
  },
  {
    q: "Pilot program ada?",
    a: "Ya — 14 hari trial Pro + design partner untuk estate skala menengah.",
  },
] as const;

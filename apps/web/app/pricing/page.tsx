import Link from "next/link";

const PLANS = [
  { code: "free", name: "Free", price: "Rp 0", devices: "5 devices" },
  { code: "starter", name: "Starter", price: "Rp 100rb/bln", devices: "20 devices" },
  { code: "pro", name: "Pro", price: "Rp 500rb/bln", devices: "100 devices" },
  { code: "enterprise", name: "Enterprise", price: "Rp 5jt/bln", devices: "Unlimited" },
];

export default function PricingPage() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="text-3xl font-semibold text-ink-primary">Next-IOT Pricing</h1>
      <p className="mt-2 text-ink-secondary">14-day trial on every paid plan. Start on Free anytime.</p>
      <div className="mt-10 grid gap-4 md:grid-cols-2">
        {PLANS.map((p) => (
          <div key={p.code} className="rounded-xl border border-cream-border p-6">
            <h2 className="text-xl font-medium">{p.name}</h2>
            <p className="mt-2 text-2xl font-semibold">{p.price}</p>
            <p className="text-sm text-ink-secondary">{p.devices}</p>
          </div>
        ))}
      </div>
      <Link
        href="/register"
        className="mt-10 inline-block rounded-lg bg-accent-cobalt px-6 py-3 text-white"
      >
        Start free trial
      </Link>
    </main>
  );
}

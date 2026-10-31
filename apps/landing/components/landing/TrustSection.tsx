import { METRIC_CARDS, TRUST_LOGOS } from "@/lib/landing-content";

export function TrustSection() {
  return (
    <section className="border-b border-slate-100 bg-slate-50 py-12 dark:border-slate-800 dark:bg-slate-900/40">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <p className="text-center text-sm font-medium text-slate-500 dark:text-slate-400">Dipercaya oleh</p>
        <div className="mt-4 flex flex-wrap justify-center gap-6 opacity-70">
          {TRUST_LOGOS.map((name) => (
            <span key={name} className="text-sm font-semibold text-slate-500 dark:text-slate-400">
              {name}
            </span>
          ))}
        </div>
        <div className="mt-10 grid gap-4 sm:grid-cols-3">
          {METRIC_CARDS.map((m) => (
            <div
              key={m.label}
              className="rounded-xl border border-slate-200 bg-white p-5 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900"
            >
              <p className="text-lg font-semibold text-slate-900 dark:text-white">{m.label}</p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{m.sub}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

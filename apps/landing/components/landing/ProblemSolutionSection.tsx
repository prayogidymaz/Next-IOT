import { PAIN_POINTS, SOLUTIONS } from "@/lib/landing-content";

export function ProblemSolutionSection() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2 className="text-center text-3xl font-semibold text-slate-900 dark:text-white">Masalah petani, solusi terintegrasi</h2>
        <div className="mt-12 grid gap-10 lg:grid-cols-2">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-red-600">Pain points</h3>
            <ul className="mt-4 space-y-6">
              {PAIN_POINTS.map((p) => (
                <li key={p.title} className="flex gap-4">
                  <span className="text-2xl" aria-hidden>
                    {p.icon}
                  </span>
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{p.title}</p>
                    <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{p.body}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Next-IoT</h3>
            <ul className="mt-4 space-y-6">
              {SOLUTIONS.map((s) => (
                <li key={s.title} className="flex gap-4">
                  <span className="text-2xl" aria-hidden>
                    {s.icon}
                  </span>
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{s.title}</p>
                    <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{s.body}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

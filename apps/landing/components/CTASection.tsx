import Link from "next/link";

import { APP_URL } from "@/lib/site";

export function CTASection() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-20 text-center md:px-6">
      <h2 className="text-3xl font-semibold text-slate-900">Siap transform operation IoT Anda?</h2>
      <p className="mt-3 text-slate-600">Trial 14 hari — tanpa kartu kredit untuk tier Free.</p>
      <div className="mt-8 flex flex-wrap justify-center gap-4">
        <Link
          href={`${APP_URL}/register`}
          className="rounded-lg bg-slate-900 px-8 py-3 text-sm font-semibold text-white shadow-soft hover:bg-slate-800"
        >
          Start Free Trial
        </Link>
        <Link
          href="/contact"
          className="rounded-lg border border-slate-200 px-8 py-3 text-sm font-semibold text-slate-800 hover:bg-slate-50"
        >
          Book Demo Call
        </Link>
      </div>
    </section>
  );
}

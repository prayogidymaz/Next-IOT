import Link from "next/link";

import { APP_URL } from "@/lib/site";

export function FinalCTAHomeSection() {
  return (
    <section className="border-t border-slate-100 bg-slate-900 py-20 text-white dark:border-slate-800">
      <div className="mx-auto max-w-3xl px-4 text-center md:px-6">
        <h2 className="text-3xl font-semibold">Siap transformasi kebun Anda?</h2>
        <p className="mt-4 text-slate-300">Trial 14 hari · setup dalam 1 hari · support Bahasa Indonesia</p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link
            href={`${APP_URL}/register`}
            className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-100"
          >
            Mulai Gratis
          </Link>
          <Link
            href="/contact"
            className="rounded-lg border border-slate-600 px-6 py-3 text-sm font-semibold hover:bg-slate-800"
          >
            Hubungi Sales
          </Link>
        </div>
        <p className="mt-8 text-sm text-slate-400">
          hello@next-iot.id · WA +62-812-0000-0000 · Instagram @next.iot.id
        </p>
      </div>
    </section>
  );
}

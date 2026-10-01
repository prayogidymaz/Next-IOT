"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import { ExternalLink } from "lucide-react";

import { TuyaSmartDashboard } from "@/components/TuyaSmartDashboard";

export function DashboardShowcase() {
  const reduceMotion = useReducedMotion();

  return (
    <section id="automation" className="mx-auto max-w-6xl px-4 py-16 md:px-8 md:py-20">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-tuya-blue">Live UI demo</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-white md:text-4xl">
            Smart control center, out of the box
          </h2>
          <p className="mt-3 max-w-xl text-slate-400">
            Interact with the Tuya-inspired device grid below — the same component powers the internal dashboard at{" "}
            <code className="rounded bg-white/5 px-1.5 py-0.5 text-tuya-green">/dashboard</code>.
          </p>
        </div>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 self-start rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition-all duration-300 ease-out hover:scale-[1.02] active:scale-95"
        >
          Open full dashboard
          <ExternalLink className="h-4 w-4" />
        </Link>
      </div>

      <motion.div
        initial={reduceMotion ? false : { opacity: 0, y: 32 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ type: "spring", stiffness: 260, damping: 28 }}
        className="overflow-hidden rounded-[32px] border border-white/10 bg-[#0B0F17] shadow-[0_40px_120px_-40px_rgba(0,122,255,0.35)]"
      >
        <div className="flex items-center gap-2 border-b border-white/10 bg-slate-900/80 px-4 py-3">
          <span className="h-3 w-3 rounded-full bg-rose-400/90" />
          <span className="h-3 w-3 rounded-full bg-amber-400/90" />
          <span className="h-3 w-3 rounded-full bg-emerald-400/90" />
          <span className="ml-3 flex-1 rounded-lg bg-white/5 px-3 py-1 text-center text-xs text-slate-400">
            app.next-iot.cloud/dashboard
          </span>
        </div>
        <div className="max-h-[640px] overflow-y-auto overflow-x-hidden">
          <div className="pointer-events-auto origin-top scale-[0.92] md:scale-100">
            <TuyaSmartDashboard embedded />
          </div>
        </div>
      </motion.div>
    </section>
  );
}

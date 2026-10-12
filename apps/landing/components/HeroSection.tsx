"use client";

import { motion } from "framer-motion";
import Link from "next/link";

import { APP_URL } from "@/lib/site";

export function HeroSection() {
  return (
    <section className="hero-grid relative overflow-hidden border-b border-slate-100 bg-gradient-to-b from-sky-50/40 to-white">
      <div className="mx-auto grid max-w-6xl gap-12 px-4 py-20 md:grid-cols-2 md:items-center md:px-6 md:py-28">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <p className="text-sm font-medium text-sky-600">Production-ready IoT platform</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight tracking-tight text-slate-900 md:text-5xl">
            Platform IoT Komersial Indonesia untuk Smart Farming, Drone/SAR, dan Industri 4.0
          </h1>
          <p className="mt-6 text-lg text-slate-600">
            Dari sensor sampai dashboard — semua terintegrasi dalam satu platform. Thing Model, MQTT, Rule Engine,
            Firmware Studio. Production-ready.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href={`${APP_URL}/register`}
              className="rounded-lg bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-slate-800 hover:scale-[1.02]"
            >
              Start Free Trial 14 Hari
            </Link>
            <a
              href="#demo"
              className="rounded-lg border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-800 shadow-sm transition hover:bg-slate-50"
            >
              Lihat Demo
            </a>
          </div>
          <ul className="mt-8 flex flex-wrap gap-4 text-xs text-slate-500">
            <li>Setara ThingsBoard Pro + fitur lebih lengkap</li>
            <li>100% Local Indonesia Support</li>
          </ul>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft"
          aria-hidden
        >
          <div className="rounded-xl bg-gradient-to-br from-slate-900 to-slate-700 p-6 text-white">
            <p className="text-xs text-slate-300">Dashboard preview</p>
            <div className="mt-4 grid grid-cols-2 gap-3">
              {["Devices online", "Alarms", "Msg/min", "MRR"].map((label) => (
                <div key={label} className="rounded-lg bg-white/10 p-3">
                  <p className="text-[10px] text-slate-300">{label}</p>
                  <p className="mt-1 font-mono text-lg font-semibold">—</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

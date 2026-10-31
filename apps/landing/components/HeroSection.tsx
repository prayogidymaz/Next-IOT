"use client";

import { motion } from "framer-motion";
import Link from "next/link";

import { APP_URL } from "@/lib/site";

export function HeroSection() {
  return (
    <section className="hero-grid relative overflow-hidden border-b border-slate-100 bg-gradient-to-b from-emerald-50/50 to-white dark:border-slate-800 dark:from-slate-900 dark:to-slate-950">
      <div className="mx-auto grid max-w-6xl gap-12 px-4 py-16 md:grid-cols-2 md:items-center md:px-6 md:py-24">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <p className="text-sm font-medium text-emerald-700 dark:text-emerald-400">Platform IoT terbuka · Smart Farming Indonesia</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight tracking-tight text-slate-900 dark:text-white md:text-5xl">
            Platform IoT Terbuka untuk Pertanian Modern Indonesia
          </h1>
          <p className="mt-6 text-lg text-slate-600 dark:text-slate-300">
            AI Copilot, visual workflow builder, dan ekosistem device-mesh dalam satu platform. Setup dalam 1 hari, hemat
            30% operational cost.*
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href={`${APP_URL}/register`}
              className="rounded-lg bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-slate-800 dark:bg-emerald-600 dark:hover:bg-emerald-500"
            >
              Mulai Gratis 14 Hari
            </Link>
            <a
              href="#demo"
              className="rounded-lg border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-800 shadow-sm transition hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-800"
            >
              Lihat Demo
            </a>
          </div>
          <p className="mt-4 text-xs text-slate-500">*Estimasi pilot; hasil bervariasi per crop dan kondisi lapangan.</p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-700 dark:bg-slate-900"
          aria-hidden
        >
          <div className="rounded-xl bg-gradient-to-br from-slate-900 to-emerald-900 p-6 text-white">
            <p className="text-xs text-slate-300">[Visual: dashboard HQ + smartphone alert]</p>
            <div className="mt-4 grid grid-cols-2 gap-3">
              {["Soil moisture", "Workflows", "Marketplace", "Alarms"].map((label) => (
                <div key={label} className="rounded-lg bg-white/10 p-3">
                  <p className="text-[10px] text-slate-300">{label}</p>
                  <p className="mt-1 font-mono text-lg font-semibold">Live</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

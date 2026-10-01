"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  AirVent,
  Droplets,
  Lamp,
  Lock,
  Moon,
  Sun,
  Zap,
} from "lucide-react";
import { useMemo, useState } from "react";

type ThemeMode = "dark" | "light";

type DeviceAccent = {
  glow: string;
  gradientFrom: string;
  gradientTo: string;
  iconBg: string;
  ring: string;
};

type DeviceConfig = {
  id: string;
  title: string;
  subtitleOff: string;
  subtitleOn: string;
  icon: typeof Lamp;
  accent: DeviceAccent;
  wide?: boolean;
  hasSlider?: boolean;
  sliderLabel?: string;
  sliderUnit?: string;
  sliderMin?: number;
  sliderMax?: number;
  sliderDefault?: number;
};

const DEVICES: DeviceConfig[] = [
  {
    id: "ac",
    title: "Living Room AC",
    subtitleOff: "Off • Idle",
    subtitleOn: "24°C • Cooling",
    icon: AirVent,
    wide: true,
    accent: {
      glow: "rgba(6, 194, 112, 0.55)",
      gradientFrom: "from-emerald-500/25",
      gradientTo: "to-cyan-500/10",
      iconBg: "bg-emerald-500/20",
      ring: "ring-emerald-400/40",
    },
    hasSlider: true,
    sliderLabel: "Target",
    sliderUnit: "°C",
    sliderMin: 18,
    sliderMax: 30,
    sliderDefault: 24,
  },
  {
    id: "light",
    title: "Ambient Lighting",
    subtitleOff: "Off • 0%",
    subtitleOn: "Warm white • On",
    icon: Lamp,
    accent: {
      glow: "rgba(245, 158, 11, 0.55)",
      gradientFrom: "from-amber-400/30",
      gradientTo: "to-orange-500/10",
      iconBg: "bg-amber-400/20",
      ring: "ring-amber-300/50",
    },
    hasSlider: true,
    sliderLabel: "Brightness",
    sliderUnit: "%",
    sliderMin: 0,
    sliderMax: 100,
    sliderDefault: 72,
  },
  {
    id: "power",
    title: "Power Meter",
    subtitleOff: "Standby • 12W",
    subtitleOn: "Live • 450W",
    icon: Zap,
    accent: {
      glow: "rgba(0, 122, 255, 0.5)",
      gradientFrom: "from-sky-500/25",
      gradientTo: "to-blue-600/10",
      iconBg: "bg-sky-500/20",
      ring: "ring-sky-400/45",
    },
  },
  {
    id: "lock",
    title: "Smart Lock",
    subtitleOff: "Locked • Secure",
    subtitleOn: "Unlocked • Entry",
    icon: Lock,
    accent: {
      glow: "rgba(99, 102, 241, 0.5)",
      gradientFrom: "from-indigo-500/25",
      gradientTo: "to-violet-500/10",
      iconBg: "bg-indigo-500/20",
      ring: "ring-indigo-400/40",
    },
  },
  {
    id: "humidity",
    title: "Bedroom Sensor",
    subtitleOff: "Offline",
    subtitleOn: "58% • Comfortable",
    icon: Droplets,
    accent: {
      glow: "rgba(6, 194, 112, 0.45)",
      gradientFrom: "from-teal-500/20",
      gradientTo: "to-emerald-500/10",
      iconBg: "bg-teal-500/20",
      ring: "ring-teal-400/40",
    },
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.05 },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 320, damping: 28 },
  },
};

function StatusDot({ active, pulse }: { active: boolean; pulse?: boolean }) {
  return (
    <span className="relative flex h-2.5 w-2.5">
      {active && pulse && (
        <motion.span
          className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
          animate={{ scale: [1, 1.8, 1], opacity: [0.6, 0, 0.6] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
      )}
      <span
        className={`relative inline-flex h-2.5 w-2.5 rounded-full ${
          active ? "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" : "bg-slate-500/80"
        }`}
      />
    </span>
  );
}

function SpringToggle({
  on,
  onToggle,
  theme,
}: {
  on: boolean;
  onToggle: () => void;
  theme: ThemeMode;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={on}
      onClick={(e) => {
        e.stopPropagation();
        onToggle();
      }}
      className={`relative h-8 w-14 shrink-0 rounded-full p-1 transition-colors duration-300 ease-out active:scale-95 ${
        on
          ? "bg-tuya-green/90"
          : theme === "dark"
            ? "bg-white/10"
            : "bg-slate-200"
      }`}
    >
      <motion.span
        layout
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
        className={`block h-6 w-6 rounded-full shadow-md ${
          theme === "dark" ? "bg-white" : "bg-white shadow-slate-300/80"
        }`}
        animate={{ x: on ? 24 : 0 }}
      />
    </button>
  );
}

function DeviceSlider({
  value,
  min,
  max,
  unit,
  label,
  disabled,
  onChange,
  theme,
}: {
  value: number;
  min: number;
  max: number;
  unit: string;
  label: string;
  disabled: boolean;
  onChange: (v: number) => void;
  theme: ThemeMode;
}) {
  return (
    <div
      className="mt-4 space-y-2"
      onClick={(e) => e.stopPropagation()}
      onKeyDown={(e) => e.stopPropagation()}
    >
      <div className="flex items-center justify-between text-xs">
        <span className={theme === "dark" ? "text-slate-400" : "text-slate-500"}>{label}</span>
        <span className={`font-semibold tabular-nums ${theme === "dark" ? "text-white" : "text-slate-800"}`}>
          {value}
          {unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`h-2 w-full cursor-pointer appearance-none rounded-full transition-opacity duration-300 ${
          disabled ? "opacity-40" : "opacity-100"
        } ${theme === "dark" ? "accent-emerald-400" : "accent-tuya-blue"}`}
        style={{
          background:
            theme === "dark"
              ? `linear-gradient(to right, #06C270 ${((value - min) / (max - min)) * 100}%, rgba(255,255,255,0.12) ${((value - min) / (max - min)) * 100}%)`
              : `linear-gradient(to right, #007AFF ${((value - min) / (max - min)) * 100}%, #e2e8f0 ${((value - min) / (max - min)) * 100}%)`,
        }}
      />
    </div>
  );
}

function SmartDeviceCard({
  device,
  on,
  sliderValue,
  onToggle,
  onSliderChange,
  theme,
  reduceMotion,
}: {
  device: DeviceConfig;
  on: boolean;
  sliderValue: number;
  onToggle: () => void;
  onSliderChange: (v: number) => void;
  theme: ThemeMode;
  reduceMotion: boolean;
}) {
  const Icon = device.icon;
  const subtitle = on
    ? device.id === "light"
      ? `Warm white • ${sliderValue}%`
      : device.id === "ac"
        ? `${sliderValue}°C • Cooling`
        : device.subtitleOn
    : device.subtitleOff;

  const glass =
    theme === "dark"
      ? "border-white/10 bg-slate-900/60 backdrop-blur-xl"
      : "border-slate-200/80 bg-white/80 shadow-sm backdrop-blur-xl";

  return (
    <motion.article
      variants={reduceMotion ? undefined : cardVariants}
      whileHover={reduceMotion ? undefined : { scale: 1.02 }}
      whileTap={reduceMotion ? undefined : { scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      onClick={onToggle}
      style={{ "--glow-color": on ? device.accent.glow : "transparent" } as React.CSSProperties}
      className={`group relative cursor-pointer overflow-hidden rounded-[28px] border p-5 transition-all duration-300 ease-out md:p-6 ${
        device.wide ? "md:col-span-2" : ""
      } ${glass} ${on ? "shadow-glow" : ""}`}
    >
      <motion.div
        className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${device.accent.gradientFrom} ${device.accent.gradientTo}`}
        initial={false}
        animate={{ opacity: on ? 1 : 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
      />

      <div className="relative z-10 flex h-full min-h-[140px] flex-col justify-between">
        <div className="flex items-start justify-between gap-3">
          <motion.div
            initial={false}
            animate={{
              scale: on ? 1 : 0.92,
              boxShadow: on ? `0 0 28px -4px ${device.accent.glow}` : "0 0 0px transparent",
            }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className={`flex h-12 w-12 items-center justify-center rounded-2xl transition-colors duration-300 ${
              on ? `${device.accent.iconBg} ring-2 ${device.accent.ring}` : theme === "dark" ? "bg-white/5" : "bg-slate-100"
            }`}
          >
            <motion.div
              initial={false}
              animate={{ rotate: on && device.id === "ac" ? 360 : 0 }}
              transition={
                on && device.id === "ac"
                  ? { repeat: Infinity, duration: 8, ease: "linear" }
                  : { type: "spring", stiffness: 300, damping: 20 }
              }
            >
              <Icon
                className={`h-6 w-6 transition-colors duration-300 ${
                  on
                    ? device.id === "light"
                      ? "text-amber-300"
                      : device.id === "ac"
                        ? "text-emerald-300"
                        : "text-sky-300"
                    : theme === "dark"
                      ? "text-slate-400"
                      : "text-slate-500"
                }`}
                strokeWidth={1.75}
              />
            </motion.div>
          </motion.div>

          <div className="flex items-center gap-3">
            <StatusDot active={on} pulse={on} />
            <SpringToggle on={on} onToggle={onToggle} theme={theme} />
          </div>
        </div>

        <div className="mt-6">
          <h3
            className={`text-lg font-bold tracking-tight transition-colors duration-300 md:text-xl ${
              theme === "dark" ? "text-white" : "text-slate-900"
            }`}
          >
            {device.title}
          </h3>
          <motion.p
            key={subtitle}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            className={`mt-1 text-sm ${theme === "dark" ? "text-slate-400" : "text-slate-500"}`}
          >
            {subtitle}
          </motion.p>

          {device.hasSlider && (
            <DeviceSlider
              value={sliderValue}
              min={device.sliderMin ?? 0}
              max={device.sliderMax ?? 100}
              unit={device.sliderUnit ?? ""}
              label={device.sliderLabel ?? ""}
              disabled={!on}
              onChange={onSliderChange}
              theme={theme}
            />
          )}
        </div>
      </div>
    </motion.article>
  );
}

export function TuyaSmartDashboard({ embedded = false }: { embedded?: boolean }) {
  const reduceMotion = useReducedMotion();
  const [theme, setTheme] = useState<ThemeMode>("dark");
  const [power, setPower] = useState<Record<string, boolean>>({
    ac: true,
    light: true,
    power: true,
    lock: false,
    humidity: true,
  });
  const [sliders, setSliders] = useState<Record<string, number>>({
    ac: 24,
    light: 72,
  });

  const pageBg = theme === "dark" ? "bg-[#0B0F17]" : "bg-[#F8FAFC]";
  const headerText = theme === "dark" ? "text-white" : "text-slate-900";
  const subText = theme === "dark" ? "text-slate-400" : "text-slate-500";

  const activeCount = useMemo(() => Object.values(power).filter(Boolean).length, [power]);

  const toggle = (id: string) => setPower((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <div
      className={`transition-colors duration-500 ease-out ${pageBg} ${
        embedded ? "min-h-0 px-3 py-4 md:px-4 md:py-5" : "min-h-screen px-4 py-8 md:px-8 md:py-10"
      }`}
    >
      <div className={`mx-auto ${embedded ? "max-w-full" : "max-w-6xl"}`}>
        <header
          className={`flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between ${
            embedded ? "mb-4" : "mb-8"
          }`}
        >
          <div>
            <motion.p
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-sm font-medium uppercase tracking-widest text-tuya-green`}
            >
              Smart Life • Home
            </motion.p>
            <motion.h1
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className={`mt-1 font-bold tracking-tight ${headerText} ${
                embedded ? "text-xl md:text-2xl" : "text-3xl md:text-4xl"
              }`}
            >
              Good evening, Alex
            </motion.h1>
            <p className={`mt-2 text-sm md:text-base ${subText}`}>
              {activeCount} devices active • All rooms synced
            </p>
          </div>

          <motion.button
            type="button"
            whileTap={{ scale: 0.95 }}
            onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
            className={`inline-flex items-center gap-2 self-start rounded-2xl border px-4 py-2.5 text-sm font-medium transition-all duration-300 ease-out active:scale-95 sm:self-auto ${
              theme === "dark"
                ? "border-white/10 bg-slate-900/60 text-white backdrop-blur-xl hover:scale-[1.02]"
                : "border-slate-200/80 bg-white/80 text-slate-800 shadow-sm backdrop-blur-xl hover:scale-[1.02]"
            }`}
          >
            {theme === "dark" ? <Sun className="h-4 w-4 text-amber-300" /> : <Moon className="h-4 w-4 text-indigo-500" />}
            {theme === "dark" ? "Light mode" : "Dark mode"}
          </motion.button>
        </header>

        <motion.section
          variants={reduceMotion ? undefined : containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-5 lg:grid-cols-3 lg:gap-6"
        >
          {DEVICES.map((device) => (
            <SmartDeviceCard
              key={device.id}
              device={device}
              on={!!power[device.id]}
              sliderValue={sliders[device.id] ?? device.sliderDefault ?? 0}
              onToggle={() => toggle(device.id)}
              onSliderChange={(v) => setSliders((s) => ({ ...s, [device.id]: v }))}
              theme={theme}
              reduceMotion={!!reduceMotion}
            />
          ))}

          <motion.article
            variants={reduceMotion ? undefined : cardVariants}
            whileHover={reduceMotion ? undefined : { scale: 1.02 }}
            className={`flex aspect-square flex-col justify-between rounded-[28px] border p-5 md:p-6 ${
              theme === "dark"
                ? "border-tuya-blue/30 bg-gradient-to-br from-sky-500/15 to-slate-900/60 backdrop-blur-xl"
                : "border-sky-200/80 bg-gradient-to-br from-sky-50 to-white/90 shadow-sm backdrop-blur-xl"
            }`}
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-tuya-blue/20 ring-2 ring-sky-400/30">
              <Zap className="h-6 w-6 text-sky-400" strokeWidth={1.75} />
            </div>
            <div>
              <p className={`text-sm ${subText}`}>Today&apos;s usage</p>
              <p className={`mt-1 text-3xl font-bold tabular-nums ${headerText}`}>4.2 kWh</p>
              <p className="mt-2 text-xs font-medium text-tuya-green">↓ 12% vs yesterday</p>
            </div>
          </motion.article>
        </motion.section>
      </div>
    </div>
  );
}

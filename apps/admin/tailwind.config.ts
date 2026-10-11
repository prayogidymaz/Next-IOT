import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "ui-monospace", "monospace"],
      },
      colors: {
        command: {
          bg: "#0a0e1a",
          panel: "#121820",
          border: "#1e293b",
          muted: "#0f172a",
          text: "#e2e8f0",
          secondary: "#94a3b8",
          tertiary: "#64748b",
          accent: "#06b6d4",
          "accent-soft": "rgba(6, 182, 212, 0.12)",
          warn: "#f97316",
          "warn-soft": "rgba(249, 115, 22, 0.12)",
        },
      },
      boxShadow: {
        panel: "0 0 0 1px rgba(6, 182, 212, 0.08), 0 8px 32px rgba(0, 0, 0, 0.45)",
      },
    },
  },
  plugins: [],
};

export default config;

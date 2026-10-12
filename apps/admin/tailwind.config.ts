import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "ui-monospace", "monospace"],
      },
      colors: {
        admin: {
          bg: "#ffffff",
          sidebar: "#f8fafc",
          border: "#e2e8f0",
          text: "#0f172a",
          secondary: "#64748b",
          accent: "#1e40af",
          "accent-soft": "#dbeafe",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.04), 0 4px 16px rgba(15, 23, 42, 0.06)",
      },
      maxWidth: {
        content: "1400px",
      },
    },
  },
  plugins: [],
};

export default config;

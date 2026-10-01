import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        cream: {
          page: "#F9F8F6",
          alt: "#FBFBF9",
          border: "#ECECE8",
          muted: "#F3F2EF",
        },
        ink: {
          primary: "#1A1A1A",
          secondary: "#666666",
          tertiary: "#8A8A85",
        },
        accent: {
          emerald: "#10B981",
          "emerald-soft": "#D1FAE5",
          indigo: "#4F46E5",
          "indigo-soft": "#E0E7FF",
          amber: "#F59E0B",
          "amber-soft": "#FEF3C7",
          violet: "#7C3AED",
          "violet-soft": "#EDE9FE",
          cobalt: "#2563EB",
          "cobalt-soft": "#DBEAFE",
        },
        tuya: {
          blue: "#007AFF",
          green: "#06C270",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(26, 26, 26, 0.04), 0 4px 16px rgba(26, 26, 26, 0.06)",
        "card-md": "0 2px 4px rgba(26, 26, 26, 0.05), 0 8px 24px rgba(26, 26, 26, 0.08)",
        glow: "0 0 40px -8px var(--glow-color, rgba(0, 122, 255, 0.45))",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.25rem",
      },
    },
  },
  plugins: [],
};

export default config;

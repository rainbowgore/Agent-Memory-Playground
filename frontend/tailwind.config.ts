import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0f172a",
        window: "#1e1e1e",
        windowBorder: "#2d2d2d",
        surface: "#1e293b",
        surfaceElevated: "#334155",
        border: "#475569",
        primary: "#a78bfa",
        primaryHover: "#8b5cf6",
        textPrimary: "#f1f5f9",
        textSecondary: "#cbd5e1",
        textTertiary: "#64748b",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
        serif: ["var(--font-serif)", "Georgia", "serif"],
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
}

export default config

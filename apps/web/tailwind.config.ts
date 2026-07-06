import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./features/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["var(--font-display)", "Space Grotesk", "ui-sans-serif", "system-ui"],
        sans: ["var(--font-sans)", "Inter", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-mono)", "JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        brand: {
          600: "#0d9488",
          700: "#0f766e",
        },
        urgency: {
          critical: "#f43f5e",
          high: "#f59e0b",
          medium: "#3b82f6",
          low: "#cbd5e1",
        },
      },
    },
  },
  plugins: [],
};

export default config;
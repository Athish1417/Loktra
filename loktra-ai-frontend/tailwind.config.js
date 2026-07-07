/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Brand
        ink: {
          DEFAULT: "#12172E", // deep indigo-navy — sidebar, authority
          800: "#1B2145",
          700: "#242C5C",
        },
        royal: {
          DEFAULT: "#3B49C4", // primary interactive
          600: "#3340B0",
          500: "#4E5BD6",
          100: "#E7E9FB",
          50: "#F1F2FD",
        },
        saffron: {
          DEFAULT: "#F5A524", // civic-action accent (sparingly)
          600: "#DB8F16",
          100: "#FDF0D7",
        },
        paper: "#F6F7FB", // app background
        // Semantic — urgency + status
        emergency: "#E5484D",
        high: "#F5820B",
        medium: "#3B82F6",
        low: "#64748B",
        success: "#12A150",
        // Text
        body: "#151A33",
        muted: "#5B6178",
        hairline: "#E6E8F0",
      },
      fontFamily: {
        display: ['"Space Grotesk"', "system-ui", "sans-serif"],
        sans: ['"Inter"', "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "monospace"],
      },
      // Numeric weight aliases so `font-500`/`font-600`/`font-700` resolve.
      fontWeight: {
        400: "400",
        500: "500",
        600: "600",
        700: "700",
      },
      spacing: {
        4.5: "1.125rem",
      },
      boxShadow: {
        card: "0 1px 2px rgba(18,23,46,0.04), 0 8px 24px -12px rgba(18,23,46,0.12)",
        lift: "0 12px 32px -12px rgba(18,23,46,0.28)",
        rail: "inset 3px 0 0 var(--rail, #3B49C4)",
      },
      keyframes: {
        "pulse-ring": {
          "0%": { boxShadow: "0 0 0 0 rgba(229,72,77,0.45)" },
          "70%": { boxShadow: "0 0 0 8px rgba(229,72,77,0)" },
          "100%": { boxShadow: "0 0 0 0 rgba(229,72,77,0)" },
        },
        "fade-up": {
          "0%": { opacity: 0, transform: "translateY(8px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "pulse-ring": "pulse-ring 1.8s cubic-bezier(0.4,0,0.6,1) infinite",
        "fade-up": "fade-up 0.4s ease-out both",
        shimmer: "shimmer 1.5s infinite",
      },
    },
  },
  plugins: [],
};

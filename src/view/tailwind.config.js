/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#0a0a0f",          // Deep near-black with a faint blue-black tint
          surface: "#111118",     // Slightly lighter surface for layering
          card: "#16161f",        // Card background — dark navy-black
          border: "#1e1e2e",      // Subtle border, cool-toned
          accent: "#3bff6f",
          "accent-dim": "#1aff5540",
          positive: "#3bff6f",
          negative: "#ff4d6d",
          warning: "#fbbf24",
          muted: "#6b6b85",
          text: "#f0f0fa",
          subtext: "#9898b0",
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'sans-serif'],
        mono: ['"DM Mono"', 'monospace'],
        display: ['"Syne"', 'sans-serif'],
      },
      borderRadius: {
        card: '14px',
        pill: '999px',
        sm: '8px',
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.04)',
        accent: '0 0 20px rgba(59,255,111,0.25)',
        "accent-sm": '0 0 10px rgba(59,255,111,0.15)',
        glow: '0 4px 32px rgba(59,255,111,0.12)',
        inset: 'inset 0 1px 0 rgba(255,255,255,0.05)',
      },
      backgroundImage: {
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E\")",
        'card-gradient': 'linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0) 100%)',
        'accent-gradient': 'linear-gradient(135deg, #3bff6f 0%, #00d4aa 100%)',
      },
      fontSize: {
        // Financial display sizes
        'display': ['3rem', { lineHeight: '1', letterSpacing: '-0.03em', fontWeight: '600' }],
        'heading': ['1.5rem', { lineHeight: '1.2', letterSpacing: '-0.02em', fontWeight: '600' }],
        'label': ['0.6875rem', { lineHeight: '1', letterSpacing: '0.08em', fontWeight: '500' }],
      },
      animation: {
        'fade-up': 'fadeUp 0.4s ease-out forwards',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'shimmer': 'shimmer 1.5s linear infinite',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
};
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#0a0a0f",
          surface: "#111118",
          border: "#1e1e2e",
          accent: "#e8ff47",
          accent2: "#47ffe8",
          muted: "#5a5a7a",
          text: "#e8e8f0",
          positive: "#47ff8a",
          negative: "#ff4747",
        },
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', 'monospace'],
        display: ['Syne', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

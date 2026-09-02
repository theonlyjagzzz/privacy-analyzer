/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#EDEBE2",
        "paper-raised": "#F4F2EA",
        ink: "#1C2321",
        line: "#C9C5B6",
        risk: {
          high: "#B23A2E",
          medium: "#B8862E",
          low: "#3F6B4A",
        },
        slate: {
          accent: "#34495F",
        },
        muted: "#6b6a63",
        faint: "#8a887e",
      },
      fontFamily: {
        serif: ["'Source Serif Pro'", "Georgia", "serif"],
        mono: ["'IBM Plex Mono'", "'Courier New'", "monospace"],
      },
    },
  },
  plugins: [],
};

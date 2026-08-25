import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bd: {
          green: {
            DEFAULT: "#006A4E",
            50: "#E6F5F0",
            100: "#CCE8DF",
            200: "#99D1BF",
            300: "#66BA9F",
            400: "#33A37F",
            500: "#006A4E",
            600: "#00553E",
            700: "#00402F",
            800: "#002B1F",
            900: "#001510",
          },
          red: {
            DEFAULT: "#F42A41",
            50: "#FEE8EB",
            100: "#FCD1D7",
            200: "#F9A3AF",
            300: "#F67587",
            400: "#F3475F",
            500: "#F42A41",
            600: "#C32234",
            700: "#921927",
            800: "#61111A",
            900: "#31080D",
          },
          gold: "#F4C430",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        bengali: ["var(--font-noto-bengali)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;

import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        accent: "var(--color-accent)",
      },
    },
  },
  plugins: [],
}

export default config

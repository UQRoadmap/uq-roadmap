import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: false,
  theme: {
    extend: {
      colors: {
        primary: "var(--color-primary)",
        secondary: "var(--color-secondary)",
        tertiary: "var(--color-tertiary)",
        incomplete: "var(--color-incomplete)",
        complete: "var(--color-complete)"
      },
    },
  },
  plugins: [],
}

export default config
/** @type {import('tailwindcss').Config} */
module.exports = {
  // The Play CDN used to compile Tailwind in the browser on every request.
  // Scanning the templates at build time gives the same utilities without
  // shipping (and running) the compiler in each visitor's browser.
  content: [
    "./base/templates/**/*.html",
    "./catalog/templates/**/*.html",
    "./core/templates/**/*.html",
    "./accounts/templates/**/*.html",
    "./static/**/*.js",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        cream: "#F8F6F0",
        forest: "#243B32",
        gold: "#A58A5A",
        ink: "rgb(var(--cf-ink) / <alpha-value>)",
      },
      fontFamily: {
        display: ["Italiana", "serif"],
        sans: ["DM Sans", "sans-serif"],
      },
    },
  },
  plugins: [],
};

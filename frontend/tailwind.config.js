/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class', // Enables dark mode support
  theme: {
    extend: {
      colors: {
        // High-contrast colors for Dark Mode (WCAG 2.1 Compliant)
        primary: '#22c55e',       // Success Green
        'primary-hover': '#16a34a',
        'dark-card': '#121212',   // Slightly lighter than pure black
        'dark-lighter': '#1e1e1e', // Lighter grey for buttons/sections
        'accessible-gray': '#a1a1aa', // Zinc-400 for placeholders/muted text
      },
    },
  },
  plugins: [],
};
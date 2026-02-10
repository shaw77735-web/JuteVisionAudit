/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        obsidian: {
          bg: '#0a0b0d',
          card: '#111318',
          border: '#1a1d24',
          muted: '#8b9199',
        },
        emerald: {
          DEFAULT: '#10b981',
          bright: '#34d399',
          dim: '#059669',
          glow: 'rgba(16, 185, 129, 0.4)',
        },
      },
      boxShadow: {
        emerald: '0 0 20px rgba(16, 185, 129, 0.4)',
      },
    },
  },
  plugins: [],
}

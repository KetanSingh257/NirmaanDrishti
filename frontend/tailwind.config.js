/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#f4f7ff',
          900: '#ffffff',
          850: '#eef3ff',
          800: '#dde7ff',
          700: '#c6d6fb',
          600: '#7f90c7',
        },
        parchment: {
          50: '#16204a',
          100: '#2f3a67',
          200: '#637097',
          300: '#3154ff',
          400: '#243fd4',
        },
        signal: {
          cyan: '#21c7d9',
          teal: '#18b6aa',
          rose: '#ff5c8a',
          amber: '#ffb020',
          emerald: '#19c37d',
        },
      },
      fontFamily: {
        display: ['"Syne"', 'sans-serif'],
        sans: ['"Outfit"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        glow: '0 18px 42px -22px rgba(49, 84, 255, 0.75)',
        card: '0 24px 60px -32px rgba(49, 84, 255, 0.35)',
      },
      backgroundImage: {
        'grid-fade':
          'linear-gradient(to right, rgba(49,84,255,0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(49,84,255,0.08) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
}

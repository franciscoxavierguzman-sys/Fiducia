/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        fiducia: {
          ink: '#17212b',
          navy: '#17324d',
          teal: '#0f8b8d',
          mint: '#dff5f1',
          gold: '#f2b84b',
          cloud: '#f7fafc',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

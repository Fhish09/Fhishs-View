/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        glass: {
          light: 'rgba(255, 255, 255, 0.12)',
          dark: 'rgba(20, 20, 25, 0.75)',
        },
        accent: {
          DEFAULT: '#007AFF',
          soft: 'rgba(0, 122, 255, 0.2)',
        },
      },
      borderRadius: {
        island: '32px',
        'island-sm': '24px',
      },
      boxShadow: {
        island: '0 8px 32px rgba(0, 0, 0, 0.25), 0 2px 8px rgba(0, 0, 0, 0.15)',
        'island-glow': '0 0 40px rgba(0, 122, 255, 0.15)',
      },
      backdropBlur: {
        island: '40px',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
      animation: {
        'spring-in': 'springIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'morph': 'morph 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
      },
      keyframes: {
        springIn: {
          '0%': { transform: 'scale(0.8)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        morph: {
          '0%': { borderRadius: '50%' },
          '100%': { borderRadius: '32px' },
        },
      },
    },
  },
  plugins: [],
}

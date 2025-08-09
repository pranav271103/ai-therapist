/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './pages/**/*.{js,ts,jsx,tsx,mdx}',
      './components/**/*.{js,ts,jsx,tsx,mdx}',
      './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        animation: {
          'pulse-stress': 'pulse-stress 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          'heartbeat': 'heartbeat 1.5s ease-in-out infinite',
          'warning-pulse': 'warning-pulse 1s ease-in-out infinite',
        },
        keyframes: {
          'pulse-stress': {
            '0%, 100%': { opacity: 1, transform: 'scale(1)' },
            '50%': { opacity: 0.7, transform: 'scale(1.02)' }
          },
          'heartbeat': {
            '0%, 50%, 100%': { transform: 'scale(1)' },
            '25%': { transform: 'scale(1.1)' },
            '75%': { transform: 'scale(0.95)' }
          },
          'warning-pulse': {
            '0%, 100%': { boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.7)' },
            '50%': { boxShadow: '0 0 0 10px rgba(239, 68, 68, 0)' }
          }
        }
      },
    },
    plugins: [],
  }
  
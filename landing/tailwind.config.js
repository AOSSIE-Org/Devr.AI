/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#22c55e', // green-500
                    hover: '#16a34a', // green-600
                    light: '#4ade80', // green-400
                    dark: '#15803d', // green-700
                },
                secondary: {
                    DEFAULT: '#06b6d4', // cyan-500 (turquoise)
                    hover: '#0891b2', // cyan-600
                    light: '#22d3ee', // cyan-400
                    dark: '#0e7490', // cyan-700
                },
                dark: {
                    DEFAULT: '#09090b', // gray-950
                    lighter: '#18181b', // gray-900
                    card: '#27272a', // gray-800
                },
                gray: {
                    950: '#09090b',
                    900: '#18181b',
                    800: '#27272a',
                    700: '#3f3f46',
                    600: '#52525b',
                    500: '#71717a',
                    400: '#a1a1aa',
                    300: '#d4d4d8',
                },
            },
            fontFamily: {
                sans: [
                    'Inter',
                    '-apple-system',
                    'BlinkMacSystemFont',
                    'Segoe UI',
                    'sans-serif',
                ],
            },
            fontSize: {
                '8xl': ['6rem', { lineHeight: '1', letterSpacing: '-0.03em' }],
                '9xl': ['8rem', { lineHeight: '1', letterSpacing: '-0.03em' }],
            },
            boxShadow: {
                sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                glow: '0 0 20px rgba(34, 197, 94, 0.25)',
                'glow-strong': '0 0 30px rgba(34, 197, 94, 0.4)',
                'glow-lg':
                    '0 0 40px rgba(34, 197, 94, 0.3), 0 0 80px rgba(34, 197, 94, 0.15)',
                'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.25)',
                'glow-cyan-strong': '0 0 30px rgba(6, 182, 212, 0.4)',
            },
            spacing: {
                18: '4.5rem',
                22: '5.5rem',
                26: '6.5rem',
                30: '7.5rem',
            },
            borderRadius: {
                '4xl': '2rem',
            },
            animation: {
                'spin-slow': 'spin 8s linear infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            transitionDuration: {
                400: '400ms',
                600: '600ms',
            },
            backdropBlur: {
                xs: '2px',
            },
        },
    },
    plugins: [],
};

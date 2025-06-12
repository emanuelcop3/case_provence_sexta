/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        provence: {
          DEFAULT: '#8A9AA6', // azul acinzentado principal
          dark: '#3A4A5A',   // azul escuro
          light: '#F5F7FA',  // cinza claro
          black: '#22292F',  // preto
          white: '#FFFFFF',  // branco
        },
      },
    },
  },
  plugins: [],
} 
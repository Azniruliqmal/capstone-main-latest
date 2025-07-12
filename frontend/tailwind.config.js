/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx,vue}"
  ],
  theme: {
    extend: {
      colors: {
        // Primary colors from the design system
        primary: {
          50: '#1F2937',  // Lightest primary
          100: '#131726', // Second lightest
          200: '#0D1019', // Third lightest
          300: '#070914', // Darkest primary
        },
        // Secondary color (Yellow/Gold)
        secondary: {
          DEFAULT: '#D4AF37', // Main secondary color
          hover: '#C19B26',   // Darker for hover states
        },
        // Font colors
        text: {
          primary: '#FFFFFF',   // White text
          secondary: '#9CA3AF', // Gray text
          muted: '#6B7280',     // Muted gray text
        },
        // Button colors
        button: {
          yellow: '#D4AF37',
          green: '#10B981',
          cyan: '#06B6D4',
        },
        // Background colors
        background: {
          primary: '#1F2937',
          secondary: '#131726',
          tertiary: '#0D1019',
          quaternary: '#070914',
        },
        // Gray scale updates to match design
        gray: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
          950: '#030712',
        },
        // Keep existing colors for compatibility
        white: "#FFFFFF",
        darkgray: "#9CA3AF",
        goldenrod: "#D4AF37",
        lightgray: "#D1D5DB",
        gainsboro: "#E5E7EB",
        dimgray: "#4B5563",
        mediumseagreen: "#10B981",
        slategray: "#6B7280",
        yellow: {
          400: "#D4AF37"
        },
        green: {
          400: "#10B981"
        },
        cyan: {
          400: "#06B6D4"
        }
      },
      fontFamily: {
        // Inter font family with proper weights
        'inter': ['Inter', 'system-ui', 'sans-serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        // Font sizes based on Inter font scale
        'xs': ['0.75rem', { lineHeight: '1rem' }],      // 12px
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
        'base': ['1rem', { lineHeight: '1.5rem' }],     // 16px
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }],      // 24px
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],   // 36px
      },
      fontWeight: {
        'thin': '100',
        'extralight': '200',
        'light': '300',
        'normal': '400',
        'medium': '500',
        'semibold': '600',
        'bold': '700',
        'extrabold': '800',
        'black': '900',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
};
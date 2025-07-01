import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['fa3777315fb68c.lhr.life', '6b4c767dc82992.lhr.life'],
    proxy: {
      '/auth': 'https://6b4c767dc82992.lhr.life',
      '/goals': 'https://6b4c767dc82992.lhr.life',
    }
  }
})


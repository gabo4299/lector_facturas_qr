import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

import tailwindcss from '@tailwindcss/vite'
import fs from 'fs'
// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react(), tailwindcss()],
  server: mode === 'development'
    ? {
        https: {
          key: fs.readFileSync('../localhost+4-key.pem'),
          cert: fs.readFileSync('../localhost+4.pem'),
        },
        host: true,
        port: 5173,
      }
    : {}, // En producción no usar certificados
}))

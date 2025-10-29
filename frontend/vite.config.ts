import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

import tailwindcss from '@tailwindcss/vite'
import fs from 'fs'
// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(),],
  server:{
    https: {
      key: fs.readFileSync('../localhost+4-key.pem'),
      cert: fs.readFileSync('../localhost+4.pem'),
    },
     host: true, // permite conexiones externas (0.0.0.0)
    port: 5173, // o el puerto que prefieras
  }
})

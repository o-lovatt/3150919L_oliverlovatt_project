import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Scotland Bird Predictor',
        short_name: 'BirdApp',
        description: 'Historical bird species occurrence likelihood across Scotland',
        theme_color: '#2b6cb0',
        icons: [
          // add your own icon files to /public later, e.g.:
          // { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          // { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
          {src: '/192.png', sizes: '192x192', type: 'image/png'},
          {src: '/512.png', sizes: '512x512', type: 'image/png'},
        ],
      },
    }),
  ],
})

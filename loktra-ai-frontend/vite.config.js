import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies /api and /uploads to the FastAPI backend on :8000,
// so the frontend can call same-origin paths with no CORS friction.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
      "/uploads": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
  build: {
    rollupOptions: {
      output: {
        // Split heavy libraries into their own cacheable chunks.
        manualChunks: {
          "vendor-react": ["react", "react-dom", "react-router-dom"],
          "vendor-charts": ["recharts"],
          "vendor-map": ["leaflet", "react-leaflet"],
          "vendor-motion": ["framer-motion"],
        },
      },
    },
  },
});

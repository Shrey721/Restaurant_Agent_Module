import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// in dev, forward /api calls to the FastAPI server
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});

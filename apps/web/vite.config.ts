/**
 * Vite configuration — ARCHITECTURE.md Sections 4.1 and 4.2, Phase 2.
 *
 * Two shipping targets share this config: the Electron renderer and the offline
 * PWA. The PWA registers `public/sw.ts`, which precaches the models and returns
 * 504 for any cross-origin request — the second layer of INV-1.
 */

import { defineConfig } from "vite";

export default defineConfig({
  // Relative base so the same build loads from file:// in the Electron shell.
  base: "./",
  build: {
    target: "es2022",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // The renderers dominate the bundle; splitting them keeps the first
          // paint budget (<= 1.5 s, Section 4.3) reachable.
          renderers: ["@audiosheet/render-sheet", "@audiosheet/render-tab"],
          engine: ["@audiosheet/engine"],
        },
      },
    },
  },
  worker: {
    format: "es",
  },
  server: {
    host: "127.0.0.1",
    strictPort: true,
  },
});

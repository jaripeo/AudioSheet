import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["packages/*/test/**/*.test.ts"],
    environment: "node",
    // INV-2: no test may depend on wall-clock time or an unseeded random source.
    restoreMocks: true,
    clearMocks: true,
  },
});

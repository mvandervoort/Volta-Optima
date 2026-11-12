import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  use: {
    baseURL: "http://localhost:8080",
  },
  webServer: {
    command: "bun run build && bun run start",
    url: "http://localhost:8080",
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
import { defineConfig } from "@playwright/test";

const APP_PORT = 8091;
const SIM_PORT = 1188;

const env = process.env as Record<string, string>;

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: /.*\.e2e\.ts/,
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: `http://127.0.0.1:${APP_PORT}`,
  },
  webServer: [
    {
      command: `bun tools/simulator/index.ts ${SIM_PORT}`,
      port: SIM_PORT,
      reuseExistingServer: !process.env.CI,
      timeout: 20_000,
    },
    {
      command: "rm -rf .e2e-data && mkdir -p .e2e-data && bun src/server/index.ts",
      url: `http://127.0.0.1:${APP_PORT}/api/v1/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: {
        ...env,
        FLOWHUB_CONFIG: "tests/e2e/fixtures/config.test.json",
        FLOWHUB_DATA_DIR: ".e2e-data",
        FLOWHUB_PORT: String(APP_PORT),
        FLOWHUB_SESSION_SECRET: "e2e-session-secret-0123456789abcdef",
        FLOWHUB_ADMIN_USER: "admin",
        FLOWHUB_ADMIN_PASSWORD: "e2e-admin-password",
        FLOWHUB_INSECURE_COOKIE: "1",
      },
    },
  ],
});
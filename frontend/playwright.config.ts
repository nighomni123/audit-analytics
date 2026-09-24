import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 90_000,
  expect: { timeout: 15_000 },
  outputDir: "test-results",
  use: {
    baseURL: "http://127.0.0.1:8789",
    headless: true,
    trace: "retain-on-failure",
    launchOptions: process.env.PLAYWRIGHT_CHROMIUM ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM } : undefined,
  },
  webServer: {
    command: "../.venv/bin/python ../tests/e2e_server.py",
    url: "http://127.0.0.1:8789/api/health",
    reuseExistingServer: false,
    timeout: 120_000,
  },
});

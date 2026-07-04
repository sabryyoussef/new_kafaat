import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  timeout: 120_000,
  expect: { timeout: 30_000 },
  workers: 1,
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: process.env.ODOO_BASE_URL || 'http://127.0.0.1:8069',
    viewport: { width: 1440, height: 900 },
    screenshot: 'off',
  },
  outputDir: '../../docs/op206/evidence/playwright-output',
});

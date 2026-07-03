import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  timeout: 180_000,
  expect: { timeout: 45_000 },
  retries: 1,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: process.env.ODOO_BASE_URL || process.env.ODOO_URL || 'http://127.0.0.1:8069',
    screenshot: 'off',
    trace: 'off',
    video: 'off',
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
  },
  outputDir: '../../docs/op86/evidence/playwright-output',
});

import { defineConfig } from '@playwright/test';
import path from 'path';

const screenshotDir = path.resolve(
  __dirname,
  '../../../docs/student_profile/uat_evidence/screenshots',
);

export default defineConfig({
  testDir: '.',
  timeout: 120_000,
  expect: { timeout: 30_000 },
  retries: 0,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: process.env.ODOO_BASE_URL || 'http://localhost:8069',
    screenshot: 'off',
    trace: 'off',
    video: 'off',
  },
  outputDir: path.resolve(__dirname, '.playwright-output'),
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
  metadata: { screenshotDir },
});

import { chromium } from '@playwright/test';
import { ODOO_BASE_URL, dismissModals, odooLogin, screenshotPath } from './helpers.mjs';

const browser = await chromium.launch({
  headless: true,
  args: ['--disable-dev-shm-usage', '--no-sandbox'],
});
const page = await browser.newPage({
  viewport: { width: 1440, height: 900 },
  userAgent:
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
});

const logs = [];
page.on('console', (msg) => logs.push(`[${msg.type()}] ${msg.text()}`));
page.on('pageerror', (err) => logs.push(`[pageerror] ${err.message}`));

await odooLogin(page);
await page.goto(`${ODOO_BASE_URL}/odoo/students`, { waitUntil: 'networkidle', timeout: 120000 }).catch(() => {});
await page.waitForTimeout(15000);
await dismissModals(page);

console.log('body length', (await page.locator('body').innerText()).length);
console.log('logs tail', logs.slice(-20));
await page.screenshot({ path: screenshotPath('debug/console_students.png'), fullPage: true });
await browser.close();

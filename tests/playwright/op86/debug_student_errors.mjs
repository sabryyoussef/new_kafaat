import { chromium } from '@playwright/test';
import { odooLogin, dismissModals, ODOO_BASE_URL } from './helpers.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const logs = [];
page.on('console', (m) => logs.push(`${m.type()}: ${m.text()}`));
page.on('pageerror', (e) => logs.push(`PAGEERROR: ${e.message}`));

await odooLogin(page);
await page.goto(`${ODOO_BASE_URL}/odoo/students`, { waitUntil: 'domcontentloaded' });
for (let i = 0; i < 6; i += 1) {
  await page.waitForTimeout(3000);
  await dismissModals(page);
}
console.log('ERRORS', logs.filter((l) => /error|Error|PAGEERROR/i.test(l)).slice(0, 30));
console.log('TOTAL LOGS', logs.length);

await browser.close();

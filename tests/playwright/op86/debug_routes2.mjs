import { chromium } from '@playwright/test';
import { odooLogin, dismissModals, ODOO_BASE_URL, screenshotPath } from './helpers.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await odooLogin(page);

for (const path of ['/odoo/students', '/odoo/action-1311', '/odoo/student', '/odoo/op.student/80']) {
  await page.goto(`${ODOO_BASE_URL}${path}`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(12000);
  await dismissModals(page);
  const info = await page.evaluate(() => ({
    len: document.body.innerText.length,
    sample: document.body.innerText.slice(0, 400),
    url: location.href,
  }));
  console.log(path, info);
  await page.screenshot({ path: screenshotPath(`debug/route_${path.replace(/\//g, '_')}.png`), fullPage: true });
}
await browser.close();

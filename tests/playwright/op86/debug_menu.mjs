import { chromium } from '@playwright/test';
import { odooLogin, dismissModals, screenshotPath } from './helpers.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await odooLogin(page);
await page.goto('http://127.0.0.1:8069/odoo', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(3000);
await dismissModals(page);

const studentsTab = page.getByRole('menuitem', { name: /طلاب|Students/i }).first();
console.log('studentsTab visible', await studentsTab.isVisible().catch(() => false));
if (await studentsTab.isVisible().catch(() => false)) {
  await studentsTab.click();
}
await page.waitForTimeout(8000);
for (let i = 0; i < 5; i += 1) await page.keyboard.press('Escape');

const info = await page.evaluate(() => ({
  url: location.href,
  text: document.body.innerText.slice(0, 800),
  list: document.querySelectorAll('.o_list_view, .o_data_row, table').length,
}));
console.log(JSON.stringify(info, null, 2));
await page.screenshot({ path: screenshotPath('debug/menu_students.png'), fullPage: true });

await browser.close();

import { chromium } from '@playwright/test';
import { odooLogin, dismissModals, ODOO_BASE_URL, screenshotPath } from './helpers.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await odooLogin(page);
await page.locator('[href="/odoo/action-1346"]').click();
await page.waitForTimeout(5000);
await dismissModals(page);

const search = page.locator('.o_searchview_input, input.o_searchview_input').first();
await search.click();
await search.fill('UAT-PW-Student-A');
await page.keyboard.press('Enter');
await page.waitForTimeout(8000);
await dismissModals(page);
console.log(await page.evaluate(() => document.body.innerText.slice(0, 600)));
await page.screenshot({ path: screenshotPath('debug/global_search_student.png'), fullPage: true });

await browser.close();

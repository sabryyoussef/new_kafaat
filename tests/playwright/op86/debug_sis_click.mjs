import { chromium } from '@playwright/test';
import { odooLogin, dismissModals, ODOO_BASE_URL, screenshotPath } from './helpers.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await odooLogin(page);
await page.goto(`${ODOO_BASE_URL}/odoo`);
await page.waitForTimeout(2000);
await dismissModals(page);

console.log('click SIS app link');
await page.locator('[href="/odoo/students"]').click();
await page.waitForTimeout(15000);
await dismissModals(page);
let info = await page.evaluate(() => ({ len: document.body.innerText.length, sample: document.body.innerText.slice(0, 500) }));
console.log('after SIS click', info);
await page.screenshot({ path: screenshotPath('debug/sis_app_click.png'), fullPage: true });

console.log('click Student Registrations then students menu');
await page.goto(`${ODOO_BASE_URL}/odoo`);
await page.waitForTimeout(2000);
await page.locator('[href="/odoo/action-1346"]').click();
await page.waitForTimeout(5000);
await page.goto(`${ODOO_BASE_URL}/odoo/students`);
await page.waitForTimeout(15000);
await dismissModals(page);
info = await page.evaluate(() => ({ len: document.body.innerText.length, sample: document.body.innerText.slice(0, 500) }));
console.log('after reg then students', info);
await page.screenshot({ path: screenshotPath('debug/reg_then_students.png'), fullPage: true });

await browser.close();

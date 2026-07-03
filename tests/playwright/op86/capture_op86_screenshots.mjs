#!/usr/bin/env node
import { chromium } from '@playwright/test';
import {
  ODOO_BASE_URL,
  captureScreenshot,
  dismissModals,
  odooLogin,
  screenshotPath,
} from './helpers.mjs';

const browser = await chromium.launch({
  headless: true,
  args: ['--disable-dev-shm-usage', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

console.log('1. Login');
await odooLogin(page);
await captureScreenshot(page, '00_home_apps.png');

console.log('2. Students list');
await page.goto(`${ODOO_BASE_URL}/odoo/students`, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(8000);
await dismissModals(page);
await captureScreenshot(page, '01_student_list.png');

console.log('3. Filters');
const filterToggle = page.locator('.o_searchview_dropdown_toggler').first();
if (await filterToggle.isVisible().catch(() => false)) {
  await filterToggle.click();
  await page.waitForTimeout(800);
}
await captureScreenshot(page, '02_student_list_filters.png');

console.log('4. Trainee form');
await page.locator('.o_kanban_record').filter({ hasText: /UAT-PW-Student-A/i }).first().click();
await page.waitForTimeout(8000);
await dismissModals(page);
await captureScreenshot(page, '03_trainee_form.png');

console.log('5. Registration list');
await page.goto(`${ODOO_BASE_URL}/odoo`, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1500);
await page.locator('[href="/odoo/action-1346"]').click();
await page.waitForTimeout(6000);
await dismissModals(page);
await captureScreenshot(page, '04b_registration_list.png');

console.log('6. Registration form');
await page.locator('.o_kanban_record').filter({ hasText: /OP86 UAT English/i }).first().dblclick();
await page.waitForTimeout(8000);
await dismissModals(page);
await captureScreenshot(page, '04_registration_form.png');

console.log('7. Multi-select (switch to list view)');
await page.goto(`${ODOO_BASE_URL}/odoo/students`, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(6000);
await dismissModals(page);
const listBtn = page.locator('.o_switch_view.o_list').first();
if (await listBtn.isVisible().catch(() => false)) {
  await listBtn.click();
  await page.waitForTimeout(3000);
}
const row = page.locator('.o_data_row, tbody tr').filter({ hasText: /UAT-PW-Student-A/i }).first();
if (await row.isVisible().catch(() => false)) {
  const cb = row.locator('input[type="checkbox"]').first();
  if (await cb.isVisible().catch(() => false)) await cb.check({ force: true });
}
await captureScreenshot(page, '05_student_multi_select.png');

console.log(`Done → ${screenshotPath('')}`);
await browser.close();

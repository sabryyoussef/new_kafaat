import { test, expect } from '@playwright/test';
import {
  ODOO_BASE_URL,
  captureScreenshot,
  dismissModals,
  odooLogin,
  screenshotPath,
} from './helpers.mjs';

test.describe('OP#86 Playwright UAT', () => {
  test.beforeEach(async ({ page }) => {
    await odooLogin(page);
  });

  test('student kanban list loads', async ({ page }) => {
    await page.goto(`${ODOO_BASE_URL}/odoo/students`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(6000);
    await dismissModals(page);
    await expect(page.getByText(/UAT-PW-Student-A/i)).toBeVisible({ timeout: 30_000 });
    await captureScreenshot(page, '01_student_list.png');
  });

  test('trainee form shows profile fields', async ({ page }) => {
    await page.goto(`${ODOO_BASE_URL}/odoo/students`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(6000);
    await dismissModals(page);
    await page.locator('.o_kanban_record').filter({ hasText: /UAT-PW-Student-A/i }).first().click();
    await page.waitForTimeout(6000);
    await dismissModals(page);
    const body = await page.locator('body').innerText();
    expect(body).toMatch(/ID Number|Specialization|Phone|Arabic/i);
    await captureScreenshot(page, '03_trainee_form.png');
  });

  test('registration form shows OP86 fields', async ({ page }) => {
    await page.goto(`${ODOO_BASE_URL}/odoo/action-1346`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(6000);
    await dismissModals(page);
    await page.locator('.o_kanban_record').filter({ hasText: /OP86 UAT English/i }).first().dblclick();
    await page.waitForTimeout(6000);
    await dismissModals(page);
    const body = await page.locator('body').innerText();
    expect(body).toMatch(/OP86 UAT|id_number|Specialization|Student Profile/i);
    await captureScreenshot(page, '04_registration_form.png');
  });
});

test.afterAll(async () => {
  console.log(`Screenshots: ${screenshotPath('')}`);
});

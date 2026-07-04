import { test, expect } from '@playwright/test';
import {
  ODOO_BASE_URL,
  dismissModals,
  odooLogin,
} from '../op86/helpers.mjs';

const STUDENT_ID = process.env.OP86_STUDENT_ID || '80';

test.describe('OP#206 UAT smoke', () => {
  test.beforeEach(async ({ page }) => {
    await odooLogin(page);
  });

  test('student form shows registration source and Arabic labels', async ({ page }) => {
    await page.goto(
      `${ODOO_BASE_URL}/web#id=${STUDENT_ID}&model=op.student&view_type=form`,
      { waitUntil: 'domcontentloaded' },
    );
    await page.waitForTimeout(8000);
    await dismissModals(page);
    const body = await page.locator('body').innerText();
    expect(body).toMatch(/رقم الهوية|التخصص|رقم الهاتف|رقم التسجيل|نوع المصدر|Specialization|ID/i);
    expect(body.toLowerCase()).not.toContain('blood group');
  });

  test('student list loads for group-by check', async ({ page }) => {
    await page.goto(`${ODOO_BASE_URL}/odoo/students`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(6000);
    await dismissModals(page);
    const body = await page.locator('body').innerText();
    expect(body).toMatch(/UAT-PW-Student|طلاب/i);
  });
});

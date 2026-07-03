import { test, expect } from '@playwright/test';

const user = process.env.ODOO_USER || 'admin';
const password = process.env.ODOO_PASSWORD || 'admin';

test.describe('OP#86 trainee profile smoke', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/web/login');
    await page.fill('input[name="login"]', user);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/web(\?|$|#)/);
  });

  test('student list loads and search view has certificate filters', async ({ page }) => {
    await page.goto('/web#action=&model=op.student&view_type=list');
    await page.waitForSelector('.o_list_view, .o_action_manager', { timeout: 60000 });
    await page.click('.o_searchview_dropdown_toggler');
    const filters = page.locator('.o_filter_menu, .dropdown-menu');
    await expect(filters).toContainText(/Previous Certificate|Issued Certificate/i);
  });

  test('student form opens from list', async ({ page }) => {
    await page.goto('/web#action=&model=op.student&view_type=list');
    await page.waitForSelector('.o_list_view tbody tr', { timeout: 60000 });
    await page.click('.o_list_view tbody tr:first-child');
    await page.waitForSelector('.o_form_view', { timeout: 30000 });
    await expect(page.locator('.o_form_view')).toBeVisible();
  });
});

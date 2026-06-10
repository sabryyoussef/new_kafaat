import { test, expect, Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const SCREENSHOT_DIR = path.resolve(
  __dirname,
  '../../../docs/training_crm_enhancements/uat_evidence/screenshots',
);

const ODOO_DB = process.env.ODOO_DB || 'sabry-test';
const ODOO_LOGIN = process.env.ODOO_LOGIN || 'admin';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || '';

function requireEnv() {
  if (!ODOO_PASSWORD) {
    throw new Error(
      'ODOO_PASSWORD environment variable is required. Do not commit credentials.',
    );
  }
}

async function snap(page: Page, filename: string) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, filename),
    fullPage: true,
  });
}

async function dismissModals(page: Page) {
  for (let i = 0; i < 5; i += 1) {
    const closeBtn = page
      .locator(
        '.s_popup_close.js_close_popup, .modal.show button.btn-close, .modal.d-block button.btn-close, .modal button:has-text("إغلاق"), .modal button:has-text("Close"), [aria-label="يغلق"]',
      )
      .first();
    if (!(await closeBtn.isVisible().catch(() => false))) break;
    await closeBtn.click({ force: true });
    await page.waitForTimeout(400);
  }
  await page.keyboard.press('Escape').catch(() => {});
}

async function login(page: Page) {
  requireEnv();
  await page.goto(`/web/login?db=${ODOO_DB}`);
  await page.locator('input[name="login"]').fill(ODOO_LOGIN);
  await page.locator('input[name="password"]').fill(ODOO_PASSWORD);
  await page.getByRole('button', { name: /^log in$/i }).click();
  await page.waitForURL((url) => !url.pathname.includes('/login'), {
    timeout: 60_000,
  });
  await page.waitForLoadState('domcontentloaded');
  await dismissModals(page);
}

async function openAction(page: Page, actionId: number) {
  await page.goto(`/odoo/action-${actionId}`, {
    waitUntil: 'domcontentloaded',
  });
  await page.waitForTimeout(2500);
  await dismissModals(page);
}

async function clickTab(page: Page, pattern: RegExp) {
  const tab = page.getByRole('tab', { name: pattern }).first();
  await tab.click({ force: true });
  await page.waitForTimeout(1500);
}

async function openFirstListRow(page: Page) {
  const row = page.locator('table tbody tr').first();
  if (await row.isVisible().catch(() => false)) {
    await row.click();
    await page.waitForTimeout(2500);
    await dismissModals(page);
    return;
  }
  const kanban = page.locator('.o_kanban_record').first();
  await expect(kanban).toBeVisible({ timeout: 20_000 });
  await kanban.click();
  await page.waitForTimeout(2500);
  await dismissModals(page);
}

async function openStudent(page: Page, idNumber: string) {
  const studentId = await page.evaluate(async (idn) => {
    const response = await fetch('/web/dataset/call_kw/op.student/search_read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'op.student',
          method: 'search_read',
          args: [[['id_number', '=', idn]], ['id', 'name_english']],
          kwargs: { limit: 1 },
        },
        id: Date.now(),
      }),
      credentials: 'include',
    });
    const payload = await response.json();
    if (payload.error) {
      throw new Error(payload.error.data?.message || payload.error.message);
    }
    return payload.result?.[0]?.id as number | undefined;
  }, idNumber);
  if (!studentId) {
    throw new Error(`Student fixture not found for id_number=${idNumber}`);
  }
  await page.goto(`/odoo/op.student/${studentId}`, {
    waitUntil: 'domcontentloaded',
  });
  await page.waitForTimeout(2500);
  await dismissModals(page);
}

test.describe('Training CRM UAT', () => {
  test('UAT-CRM-01 Sales Team lead target', async ({ page }) => {
    await login(page);
    const teamId = await page.evaluate(async () => {
      const response = await fetch('/web/dataset/call_kw/crm.team/search_read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'crm.team',
            method: 'search_read',
            args: [[], ['id', 'name']],
            kwargs: { limit: 1 },
          },
          id: Date.now(),
        }),
        credentials: 'include',
      });
      const payload = await response.json();
      return payload.result?.[0]?.id as number | undefined;
    });
    if (!teamId) {
      test.skip(true, 'No crm.team records found');
    }
    await page.goto(`/odoo/crm.team/${teamId}`, {
      waitUntil: 'domcontentloaded',
    });
    await page.waitForTimeout(2500);
    await dismissModals(page);
    await expect(page.locator('.o_field_widget[name="lead_target"]').first()).toBeVisible({
      timeout: 15_000,
    });
    await snap(page, '01_crm_lead_target.png');
  });

  test('UAT-CRM-02 CRM Students menu / wording', async ({ page }) => {
    await login(page);
    await openAction(page, 1311);
    await expect(page.getByText(/Students|طلاب/i).first()).toBeVisible({
      timeout: 15_000,
    });
    await snap(page, '02_crm_student_customer_label.png');
  });

  test('UAT-PROG-01 Program workflow statusbar', async ({ page }) => {
    await login(page);
    await openAction(page, 1324);
    await openFirstListRow(page);
    await expect(page.locator('.o_field_widget[name="state"]').first()).toBeVisible({
      timeout: 15_000,
    });
    await snap(page, '03_program_workflow_statusbar.png');
  });

  test('UAT-PROG-02 Program Arabic tabs', async ({ page }) => {
    await login(page);
    await openAction(page, 1324);
    await openFirstListRow(page);
    for (const label of [/وصف البرنامج/, /الاعتمادات/, /التسويق/]) {
      await expect(page.getByRole('tab', { name: label }).first()).toBeVisible({
        timeout: 15_000,
      });
    }
    await snap(page, '04_program_tabs.png');
  });

  test('UAT-PROG-03 Program enhancement fields', async ({ page }) => {
    await login(page);
    await openAction(page, 1324);
    await openFirstListRow(page);
    const fieldTabs: Record<string, RegExp | null> = {
      duration_text: null,
      training_language: null,
      max_trainees: null,
      available_schedules: /طريقة|delivery/i,
      program_objectives: /وصف/i,
      career_outcomes: /وصف/i,
    };
    for (const [field, tab] of Object.entries(fieldTabs)) {
      if (tab) {
        await clickTab(page, tab);
      }
      await expect(page.locator(`.o_field_widget[name="${field}"]`).first()).toBeVisible({
        timeout: 15_000,
      });
    }
    await snap(page, '05_program_fields.png');
  });

  test('UAT-PROG-04 Program Skills regression', async ({ page }) => {
    await login(page);
    await openAction(page, 1324);
    await openFirstListRow(page);
    await clickTab(page, /skills/i);
    await expect(page.locator('.o_field_widget[name="skill_ids"]').first()).toBeVisible({
      timeout: 15_000,
    });
    await snap(page, '06_program_skills_regression.png');
  });

  test('UAT-PROG-05 Linked courses on program', async ({ page }) => {
    await login(page);
    await openAction(page, 1324);
    await openFirstListRow(page);
    await clickTab(page, /linked courses|courses/i);
    await expect(
      page.locator('.o_field_widget[name="course_ids"]').first(),
    ).toBeVisible({ timeout: 15_000 });
    await snap(page, '07_program_linked_courses.png');
  });

  test('UAT-PROG-06 Marketing and media section', async ({ page }) => {
    await login(page);
    await openAction(page, 1324);
    await openFirstListRow(page);
    await clickTab(page, /التسويق|marketing/i);
    await expect(
      page.locator('.o_field_widget[name="brochure"], .o_field_widget[name="marketing_materials"]').first(),
    ).toBeVisible({ timeout: 15_000 });
    await snap(page, '08_program_marketing_media.png');
  });

  test('UAT-REG-01 Student profile regression', async ({ page }) => {
    await login(page);
    await openStudent(page, 'UAT-PW-A');
    for (const field of ['name_arabic', 'name_english', 'id_number', 'email']) {
      await expect(page.locator(`.o_field_widget[name="${field}"]`).first()).toBeVisible({
        timeout: 15_000,
      });
    }
    await clickTab(page, /courses|دورات/i);
    await snap(page, '09_student_profile_regression.png');
  });
});

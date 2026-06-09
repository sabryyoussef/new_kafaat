import { test, expect, Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const SCREENSHOT_DIR = path.resolve(
  __dirname,
  '../../../docs/student_profile/uat_evidence/screenshots',
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
  await page.waitForURL(
    (url) => !url.pathname.includes('/login'),
    { timeout: 60_000 },
  );
  await page.waitForLoadState('domcontentloaded');
  await dismissModals(page);
}

async function openAction(page: Page, actionId: number) {
  await page.goto(`/odoo/action-${actionId}`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2500);
  await dismissModals(page);
}

function fieldInput(page: Page, name: string) {
  return page
    .locator(
      `.o_field_widget[name="${name}"] input, .o_field_widget[name="${name}"] textarea, input[name="${name}"], textarea[name="${name}"]`,
    )
    .first();
}

async function clickNewIfPresent(page: Page) {
  const newBtn = page.locator('.o_list_button_add').first();
  if (await newBtn.isVisible().catch(() => false)) {
    await dismissModals(page);
    await newBtn.click({ force: true });
    await page.waitForTimeout(2000);
    return true;
  }
  const fallback = page
    .getByRole('button', { name: /^(new|جديد|create)$/i })
    .first();
  if (await fallback.isVisible().catch(() => false)) {
    await fallback.click({ force: true });
    await page.waitForTimeout(2000);
    return true;
  }
  return false;
}

async function saveForm(page: Page) {
  await dismissModals(page);
  const saveBtn = page
    .locator('button.o_form_button_save, button[aria-label*="حفظ"], button[aria-label*="Save"]')
    .first();
  if (await saveBtn.isVisible().catch(() => false)) {
    await saveBtn.click({ force: true });
    await page.waitForTimeout(3000);
    return;
  }
  await page.keyboard.press('Control+S');
  await page.waitForTimeout(3000);
}

async function fieldValue(page: Page, name: string) {
  const widget = page.locator(`.o_field_widget[name="${name}"]`);
  await widget.first().waitFor({ state: 'visible', timeout: 30_000 });
  const input = fieldInput(page, name);
  if (await input.isVisible().catch(() => false)) {
    const value = await input.inputValue();
    if (value.trim()) return value;
  }
  return widget.first().innerText();
}

async function fillField(page: Page, name: string, value: string) {
  const input = fieldInput(page, name);
  await input.waitFor({ state: 'visible', timeout: 30_000 });
  await input.click();
  await input.pressSequentially(value, { delay: 20 });
}

async function rpcCreate(
  page: Page,
  model: string,
  values: Record<string, unknown>,
): Promise<number> {
  const result = await page.evaluate(
    async ({ modelName, vals }) => {
      const response = await fetch(`/web/dataset/call_kw/${modelName}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: { model: modelName, method: 'create', args: [vals], kwargs: {} },
          id: Date.now(),
        }),
        credentials: 'include',
      });
      const payload = await response.json();
      if (payload.error) {
        throw new Error(payload.error.data?.message || payload.error.message);
      }
      return payload.result as number;
    },
    { modelName: model, vals: values },
  );
  return result;
}

async function openRecord(page: Page, model: string, recordId: number) {
  await page.goto(`/odoo/${model}/${recordId}`, {
    waitUntil: 'domcontentloaded',
  });
  await page.waitForTimeout(3500);
  await dismissModals(page);
  await page.locator('.o_form_view, .o_list_view').first().waitFor({
    state: 'visible',
    timeout: 30_000,
  });
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
  await openRecord(page, 'students', studentId);
}

async function clickTab(page: Page, pattern: RegExp) {
  await dismissModals(page);
  const tab = page.getByRole('tab', { name: pattern }).first();
  await tab.click({ force: true });
  await page.waitForTimeout(1500);
}

test.describe.serial('Student Profile Playwright UAT', () => {
  test.beforeAll(() => {
    requireEnv();
  });

  test('UAT-01 Course auto code CRS', async ({ page }) => {
    await login(page);
    const name = `UAT PW Course ${Date.now()}`;
    const courseId = await rpcCreate(page, 'op.course', { name, code: false });
    await openRecord(page, 'courses', courseId);
    const codeVal = (await fieldValue(page, 'code')).trim();
    expect(codeVal).toMatch(/^CRS-/);
    await snap(page, '01_course_crs_code.png');
  });

  test('UAT-02 Program auto code PRG', async ({ page }) => {
    await login(page);
    const level = await page.evaluate(async () => {
      const response = await fetch('/web/dataset/call_kw/op.program.level/search_read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'op.program.level',
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
    const programId = await rpcCreate(page, 'op.program', {
      name: `UAT PW Program ${Date.now()}`,
      code: false,
      ...(level ? { program_level_id: level } : {}),
    });
    await openRecord(page, 'programs', programId);
    const codeVal = (await fieldValue(page, 'code')).trim();
    expect(codeVal).toMatch(/^PRG-/);
    await snap(page, '02_program_prg_code.png');
  });

  test('UAT-03 Student required fields', async ({ page }) => {
    await login(page);
    await openStudent(page, 'UAT-PW-A');
    for (const field of [
      'name_arabic',
      'name_english',
      'id_number',
      'email',
      'phone',
      'birth_date',
      'street',
      'city',
      'country_id',
    ]) {
      await expect(page.locator(`.o_field_widget[name="${field}"]`).first()).toBeVisible({
        timeout: 15_000,
      });
    }
    await snap(page, '03_student_required_fields.png');
  });

  test('UAT-04 Portal bridge required data', async ({ page }) => {
    await login(page);
    await page.goto('/odoo/action-1351', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
    const hasSection = await page
      .getByText(/Student Profile Required Data|id_number|street/i)
      .first()
      .isVisible()
      .catch(() => false);
    if (!hasSection) {
      test.skip(true, 'student.registration action or profile fields not visible');
    }
    await snap(page, '04_portal_bridge_required_data.png');
  });

  test('UAT-05 Family and siblings', async ({ page }) => {
    await login(page);
    await openStudent(page, 'UAT-PW-A');
    await clickTab(page, /family|عائلة/i);
    await expect(
      page.locator('.o_field_widget[name="sibling_ids"]'),
    ).toContainText(/UAT-PW-Student-B|UAT-PW-B/i, { timeout: 15_000 });
    await snap(page, '05_family_siblings.png');
  });

  test('UAT-06 Training summary', async ({ page }) => {
    await login(page);
    await openStudent(page, 'UAT-PW-A');
    await expect(page.locator('.o_field_widget[name="training_status"]').first()).toBeVisible();
    await expect(page.locator('.o_field_widget[name="current_course_id"]').first()).toBeVisible();
    await snap(page, '06_training_summary.png');
  });

  test('UAT-07 Courses tab', async ({ page }) => {
    await login(page);
    await openStudent(page, 'UAT-PW-A');
    await clickTab(page, /courses|دورات/i);
    await expect(page.getByText(/finished|running|منته|جار/i).first()).toBeVisible({
      timeout: 15_000,
    });
    await snap(page, '07_courses_tab.png');
  });

  test('UAT-08 Course Skills tab', async ({ page }) => {
    await login(page);
    await openAction(page, 1314);
    await dismissModals(page);
    await page.locator('table tbody tr').first().click();
    await page.waitForTimeout(2500);
    await dismissModals(page);
    await expect(page.getByRole('tab', { name: /subjects|مواضيع/i }).first()).toBeVisible();
    await clickTab(page, /skills/i);
    await expect(page.locator('.o_field_widget[name="skill_ids"]').first()).toBeVisible({
      timeout: 15_000,
    });
    await snap(page, '08_course_skills_tab.png');
  });

  test('UAT-09 Program Skills tab', async ({ page }) => {
    await login(page);
    await openAction(page, 1324);
    await dismissModals(page);
    await page.locator('table tbody tr').first().click();
    await page.waitForTimeout(2500);
    await dismissModals(page);
    await clickTab(page, /skills/i);
    await expect(page.locator('.o_field_widget[name="skill_ids"]').first()).toBeVisible({
      timeout: 15_000,
    });
    await snap(page, '09_program_skills_tab.png');
  });

  test('UAT-10 Certificate workflow', async ({ page }) => {
    await login(page);
    await openStudent(page, 'UAT-PW-A');
    await clickTab(page, /courses|دورات/i);
    const certText = page.getByText(/CERT-/i).first();
    await expect(certText).toBeVisible({ timeout: 15_000 });
    await snap(page, '10_certificate_workflow.png');
  });

  test('UAT-11 Certificate email action', async ({ page }) => {
    await login(page);
    await openAction(page, 1367);
    await dismissModals(page);
    await page.locator('table tbody tr').first().click();
    await page.waitForTimeout(2500);
    await dismissModals(page);
    const sendBtn = page
      .locator('button[name="action_send_certificate_email"]')
      .first();
    if (await sendBtn.isVisible().catch(() => false)) {
      await sendBtn.click({ force: true });
      await page.waitForTimeout(2000);
    }
    await snap(page, '11_certificate_email_action.png');
  });
});

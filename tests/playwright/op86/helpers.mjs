import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const SCREENSHOT_DIR = path.resolve(
  __dirname,
  '../../../docs/op86/evidence/screenshots',
);

export const ODOO_DB = process.env.ODOO_DB || 'sabry-test';
export const ODOO_BASE_URL = process.env.ODOO_BASE_URL || process.env.ODOO_URL || 'http://127.0.0.1:8069';
export const ODOO_LOGIN = process.env.ODOO_USER || process.env.ODOO_LOGIN || 'admin';
export const ODOO_PASSWORD = process.env.ODOO_PASSWORD || 'admin';

export function screenshotPath(name) {
  const full = path.join(SCREENSHOT_DIR, name);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  return full;
}

export async function exitFullscreen(page) {
  for (let i = 0; i < 6; i += 1) {
    await page.keyboard.press('Escape');
    await page.waitForTimeout(250);
  }
}

export async function dismissModals(page) {
  await exitFullscreen(page);
  for (let i = 0; i < 8; i += 1) {
    const closeBtn = page
      .locator(
        '.o_onboarding_container button.btn-close, .s_popup_close.js_close_popup, .modal.show button.btn-close, .modal.d-block button.btn-close, .modal button:has-text("Close"), .modal button:has-text("إغلاق"), dialog button.btn-close',
      )
      .first();
    if (!(await closeBtn.isVisible().catch(() => false))) break;
    await closeBtn.click({ force: true });
    await page.waitForTimeout(400);
  }
}

export async function consumeTours(page) {
  await page.evaluate(async () => {
    try {
      await fetch('/web/dataset/call_kw/web_tour.tour/consume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'web_tour.tour',
            method: 'consume',
            args: [],
            kwargs: {},
          },
          id: Date.now(),
        }),
        credentials: 'include',
      });
    } catch {
      /* ignore */
    }
  });
}

export async function odooLogin(page) {
  await page.goto(`${ODOO_BASE_URL}/web/login?db=${ODOO_DB}`, {
    waitUntil: 'domcontentloaded',
  });
  await page.locator('input[name="login"]').waitFor({ state: 'visible', timeout: 30_000 });
  await page.locator('input[name="login"]').fill(ODOO_LOGIN);
  await page.locator('input[name="password"]').fill(ODOO_PASSWORD);
  await page.getByRole('button', { name: /log in|login|تسجيل/i }).click();
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 60_000 });
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2000);
  await consumeTours(page);
  await dismissModals(page);
}

export async function openApp(page, appName) {
  await page.goto(`${ODOO_BASE_URL}/odoo`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await dismissModals(page);
  const app = page.locator('.o_app', { hasText: appName }).first();
  await app.waitFor({ state: 'visible', timeout: 30_000 });
  await app.click();
  await page.waitForTimeout(3000);
  await dismissModals(page);
}

export async function openSISStudents(page) {
  await openApp(page, 'SIS');
  const studentsMenu = page.locator(
    '.o_main_navbar a, .o_menu_brand, nav a, .o_menu_sections a',
  ).filter({ hasText: /^طلاب$|^Students$/ }).first();
  await studentsMenu.waitFor({ state: 'visible', timeout: 30_000 });
  await studentsMenu.click();
  await page.waitForTimeout(4000);
  await dismissModals(page);
  await page.getByText(/UAT-PW-Student|Student|طالب/i).first().waitFor({
    state: 'visible',
    timeout: 60_000,
  }).catch(() => {});
}

export async function openStudentRegistrationsApp(page) {
  await page.goto(`${ODOO_BASE_URL}/odoo`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await dismissModals(page);
  const app = page.locator('.o_app', { hasText: /Student Registrations/i }).first();
  await app.waitFor({ state: 'visible', timeout: 30_000 });
  await app.click();
  await page.waitForTimeout(4000);
  await dismissModals(page);
}

export async function openStudentForm(page, studentId) {
  await page.goto(
    `${ODOO_BASE_URL}/odoo/op.student/${studentId}?model=op.student&resId=${studentId}`,
    { waitUntil: 'domcontentloaded' },
  );
  await page.waitForTimeout(5000);
  await dismissModals(page);
  await page.getByText(/ID Number|رقم|Specialization|UAT-PW/i).first().waitFor({
    state: 'visible',
    timeout: 60_000,
  }).catch(() => {});
}

export async function openRegistrationForm(page, registrationId) {
  await page.goto(
    `${ODOO_BASE_URL}/odoo/student.registration/${registrationId}?model=student.registration&resId=${registrationId}`,
    { waitUntil: 'domcontentloaded' },
  );
  await page.waitForTimeout(5000);
  await dismissModals(page);
  await page.getByText(/REG|Registration|OP86 UAT|Student Name/i).first().waitFor({
    state: 'visible',
    timeout: 60_000,
  }).catch(() => {});
}

export async function captureScreenshot(page, filename) {
  await page.waitForTimeout(1000);
  await dismissModals(page);
  await page.screenshot({ path: screenshotPath(filename), fullPage: true });
}

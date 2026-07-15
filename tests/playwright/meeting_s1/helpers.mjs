import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const SCREENSHOT_DIR = path.resolve(
  __dirname,
  '../../../docs/op_meeting_nabil/evidence/screenshots',
);

export const ODOO_DB = process.env.ODOO_DB || 'sabry-test';
export const ODOO_BASE_URL =
  process.env.ODOO_BASE_URL || process.env.ODOO_URL || 'http://127.0.0.1:8069';
export const ODOO_LOGIN = process.env.ODOO_USER || process.env.ODOO_LOGIN || 'admin';
export const ODOO_PASSWORD = process.env.ODOO_PASSWORD || 'admin';

export const PROOF_STUDENT_ID = process.env.S1_PROOF_STUDENT_ID || '213';
export const PROOF_ID_NUMBER = process.env.S1_PROOF_ID_NUMBER || '35135399001';
export const PROOF_VOUCHER = process.env.S1_PROOF_VOUCHER || 'VCH-S1-PW-001';

export function screenshotPath(name) {
  const full = path.join(SCREENSHOT_DIR, name);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  return full;
}

export async function dismissModals(page) {
  for (let i = 0; i < 6; i += 1) {
    await page.keyboard.press('Escape');
    await page.waitForTimeout(200);
  }
  for (let i = 0; i < 10; i += 1) {
    const closeBtn = page
      .locator(
        [
          '.o_error_dialog button:has-text("Close")',
          '.o_error_dialog button:has-text("إغلاق")',
          '.o_technical_modal button:has-text("Close")',
          '.o_technical_modal button.btn-primary',
          '.o_dialog .modal-footer button.btn-primary',
          '.o_onboarding_container button.btn-close',
          '.s_popup_close.js_close_popup',
          '.modal.show button.btn-close',
          '.modal.d-block button.btn-close',
          '.modal button:has-text("Close")',
          '.modal button:has-text("إغلاق")',
          'dialog button.btn-close',
        ].join(', '),
      )
      .first();
    if (!(await closeBtn.isVisible().catch(() => false))) break;
    await closeBtn.click({ force: true });
    await page.waitForTimeout(400);
  }
}

/**
 * Mark every web tour consumed for the current user.
 * Must pass tourName — bare consume() raises and opens Odoo's error dialog.
 */
export async function consumeTours(page) {
  await page.evaluate(async () => {
    const callKw = async (model, method, args = [], kwargs = {}) => {
      const resp = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: { model, method, args, kwargs },
          id: Date.now() + Math.random(),
        }),
      });
      return resp.json();
    };
    try {
      const me = await callKw('res.users', 'context_get', []);
      const uid = me?.result?.uid || 2;
      await callKw('res.users', 'write', [[uid], { tour_enabled: false }]);
      const listed = await callKw('web_tour.tour', 'search_read', [[]], {
        fields: ['name'],
        limit: 200,
      });
      const tours = listed.result || [];
      for (const tour of tours) {
        if (!tour?.name) continue;
        await callKw('web_tour.tour', 'consume', [tour.name]);
      }
    } catch {
      /* ignore — screenshots still proceed after dismissModals */
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
  await exitFullscreenHard(page);
  await dismissModals(page);
}

export async function openSISApp(page) {
  await page.goto(`${ODOO_BASE_URL}/odoo`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await dismissModals(page);
  const app = page.locator('.o_app', { hasText: /SIS/i }).first();
  await app.waitFor({ state: 'visible', timeout: 30_000 });
  await app.click();
  await page.waitForTimeout(3000);
  await dismissModals(page);
}

export async function exitFullscreenHard(page) {
  await page.evaluate(() => {
    try {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      }
    } catch {
      /* ignore */
    }
  });
  for (let i = 0; i < 8; i += 1) {
    await page.keyboard.press('Escape');
    await page.waitForTimeout(150);
  }
  // Click "Press esc to exit full screen" hint if present
  const hint = page.getByText(/Press esc to exit full screen/i).first();
  if (await hint.isVisible().catch(() => false)) {
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
  }
}

export async function openStudentForm(page, studentId) {
  await exitFullscreenHard(page);
  await page.goto(
    `${ODOO_BASE_URL}/web#id=${studentId}&model=op.student&view_type=form&cids=1`,
    { waitUntil: 'domcontentloaded' },
  );
  await page.waitForTimeout(5000);
  await exitFullscreenHard(page);
  await dismissModals(page);
  await page.locator('.o_form_view, .o_form_sheet, .o_field_widget[name="id_number"]').first().waitFor({
    state: 'visible',
    timeout: 60_000,
  });
}

export async function openStudentsList(page) {
  await exitFullscreenHard(page);
  // Prefer classic action hash — more reliable than /odoo/students menu shell
  await page.goto(
    `${ODOO_BASE_URL}/web#action=1311&model=op.student&view_type=list`,
    { waitUntil: 'domcontentloaded' },
  );
  await page.waitForTimeout(5000);
  await exitFullscreenHard(page);
  await dismissModals(page);

  const listReady = page.locator('.o_list_renderer, .o_list_table, .o_searchview, .o_control_panel').first();
  if (!(await listReady.isVisible().catch(() => false))) {
    // Fallback: numeric action id if external id hash fails in this Odoo build
    await page.goto(
      `${ODOO_BASE_URL}/web#action=${process.env.S1_STUDENT_ACTION_ID || '1311'}&model=op.student&view_type=list`,
      { waitUntil: 'domcontentloaded' },
    );
    await page.waitForTimeout(5000);
    await exitFullscreenHard(page);
    await dismissModals(page);
  }

  // Last fallback — SIS menu click
  if (!(await listReady.isVisible().catch(() => false))) {
    await openSISApp(page);
    await page.getByRole('menuitem', { name: /Students|طلاب/i }).first().click();
    await page.waitForTimeout(5000);
    await exitFullscreenHard(page);
    await dismissModals(page);
  }

  await listReady.waitFor({ state: 'visible', timeout: 60_000 });
}

export async function searchStudents(page, query) {
  const candidates = [
    page.locator('.o_searchview_input').first(),
    page.locator('input.o_searchview_input').first(),
    page.locator('.o_searchview input').first(),
    page.getByRole('searchbox').first(),
  ];
  let input = null;
  for (const loc of candidates) {
    if (await loc.isVisible().catch(() => false)) {
      input = loc;
      break;
    }
  }
  if (!input) {
    // Expand search if collapsed
    const toggle = page.locator('.o_searchview, .o_searchview_icon, .oi-search').first();
    if (await toggle.isVisible().catch(() => false)) {
      await toggle.click();
      await page.waitForTimeout(500);
    }
    input = page.locator('.o_searchview_input, .o_searchview input').first();
  }
  await input.waitFor({ state: 'visible', timeout: 30_000 });
  await input.click();
  await input.fill('');
  await input.fill(query);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(2500);
}

export async function captureScreenshot(page, filename) {
  await page.waitForTimeout(500);
  await dismissModals(page);
  await page.screenshot({ path: screenshotPath(filename), fullPage: true });
}

export async function fieldValue(page, name) {
  const widget = page.locator(`.o_field_widget[name="${name}"]`).first();
  await widget.waitFor({ state: 'visible', timeout: 20_000 });
  const input = widget.locator('input, textarea').first();
  if (await input.count()) {
    const val = await input.inputValue().catch(() => '');
    if (val) return val;
  }
  return (await widget.innerText()).trim();
}

export async function callKw(page, model, method, args = [], kwargs = {}) {
  return page.evaluate(
    async ({ model, method, args, kwargs }) => {
      const resp = await fetch('/web/dataset/call_kw/' + model + '/' + method, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: { model, method, args, kwargs },
          id: Date.now(),
        }),
      });
      return resp.json();
    },
    { model, method, args, kwargs },
  );
}

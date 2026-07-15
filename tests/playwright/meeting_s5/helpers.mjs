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

export const S5_BATCH_ID = process.env.S5_BATCH_ID || '';
export const S5_TOKEN = process.env.S5_TOKEN || '';
export const S5_PORTAL_LOGIN = process.env.S5_PORTAL_LOGIN || 's5.pw.student@test.local';
export const S5_PORTAL_PASSWORD = process.env.S5_PORTAL_PASSWORD || 'S5Portal!23';
export const S5_OTHER_LOGIN = process.env.S5_OTHER_LOGIN || 's5.pw.other@test.local';
export const S5_OTHER_PASSWORD = process.env.S5_OTHER_PASSWORD || 'S5Portal!23';

export function screenshotPath(name) {
  const full = path.join(SCREENSHOT_DIR, name);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  return full;
}

export async function dismissModals(page) {
  for (let i = 0; i < 6; i += 1) {
    await page.keyboard.press('Escape');
    await page.waitForTimeout(150);
  }
}

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
      for (const tour of listed.result || []) {
        if (tour?.name) await callKw('web_tour.tour', 'consume', [tour.name]);
      }
    } catch {
      /* ignore */
    }
  });
}

export async function odooLogin(page, login = ODOO_LOGIN, password = ODOO_PASSWORD) {
  await page.goto(`${ODOO_BASE_URL}/web/login?db=${ODOO_DB}`, {
    waitUntil: 'domcontentloaded',
  });
  await page.locator('input[name="login"]').waitFor({ state: 'visible', timeout: 30_000 });
  await page.locator('input[name="login"]').fill(login);
  await page.locator('input[name="password"]').fill(password);
  await page.getByRole('button', { name: /log in|login|تسجيل/i }).click();
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 60_000 });
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1500);
  await consumeTours(page);
  await dismissModals(page);
}

export async function callKw(page, model, method, args = [], kwargs = {}) {
  return page.evaluate(
    async ({ model, method, args, kwargs }) => {
      const resp = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
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

export async function captureScreenshot(page, name) {
  await page.screenshot({ path: screenshotPath(name), fullPage: true });
}

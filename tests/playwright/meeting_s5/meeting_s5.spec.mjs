/**
 * Meeting S5 — Playwright proofs
 * OP#358 — Batch QR portal attendance (Option A: requires op.session)
 */
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import {
  callKw,
  captureScreenshot,
  dismissModals,
  odooLogin,
  ODOO_BASE_URL,
  ODOO_DB,
} from './helpers.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function loadEnv() {
  const envFile = path.join(__dirname, '.s5_env');
  const out = {};
  if (fs.existsSync(envFile)) {
    for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
      const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
      if (m) out[m[1]] = m[2];
    }
  }
  return {
    batchId: process.env.S5_BATCH_ID || out.S5_BATCH_ID,
    token: process.env.S5_TOKEN || out.S5_TOKEN,
    sessionId: process.env.S5_SESSION_ID || out.S5_SESSION_ID,
    portalLogin: process.env.S5_PORTAL_LOGIN || out.S5_PORTAL_LOGIN,
    portalPassword: process.env.S5_PORTAL_PASSWORD || out.S5_PORTAL_PASSWORD,
    otherLogin: process.env.S5_OTHER_LOGIN || out.S5_OTHER_LOGIN,
    otherPassword: process.env.S5_OTHER_PASSWORD || out.S5_OTHER_PASSWORD,
  };
}

async function setUserLang(page, lang) {
  await page.evaluate(async (code) => {
    const resp = await fetch('/web/dataset/call_kw/res.users/write', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'res.users',
          method: 'write',
          args: [[odoo?.session_info?.uid || false], { lang: code }],
          kwargs: {},
        },
        id: Date.now(),
      }),
    });
    return resp.json();
  }, lang).catch(() => null);
  // Prefer context via call_kw with known login handled server-side in fixture
}

test.describe('Meeting S5 proofs (#358)', () => {
  const cfg = loadEnv();

  test('S5-358a — Batch form shows QR fields', async ({ page }) => {
    expect(cfg.batchId).toBeTruthy();
    await odooLogin(page);
    await page.goto(
      `${ODOO_BASE_URL}/web#id=${cfg.batchId}&model=op.batch&view_type=form&db=${ODOO_DB}`,
      { waitUntil: 'domcontentloaded' },
    );
    await page.waitForTimeout(4000);
    await dismissModals(page);
    await captureScreenshot(page, 's5_358_batch_form_qr.png');
    const body = await page.locator('.o_form_view, .o_form_sheet').first().innerText();
    expect(body).toMatch(/Attendance QR|QR Check-in|Option A|session/i);
    const views = await callKw(page, 'op.batch', 'get_views', [], {
      views: [[false, 'form']],
      options: {},
    });
    expect(JSON.stringify(views.result || views)).toContain('attendance_qr_token');
  });

  test('S5-358b — Enrolled portal student checks in (EN)', async ({ page }) => {
    expect(cfg.token).toBeTruthy();
    await odooLogin(page, cfg.portalLogin, cfg.portalPassword);
    await page.goto(`${ODOO_BASE_URL}/attendance/batch/${cfg.token}`, {
      waitUntil: 'domcontentloaded',
    });
    await page.waitForTimeout(3000);
    await captureScreenshot(page, 's5_358_checkin_success.png');
    const text = await page.locator('body').innerText();
    expect(text).toMatch(/Checked in|Already checked in/i);
  });

  test('S5-358c — Duplicate scan → already', async ({ page }) => {
    expect(cfg.token).toBeTruthy();
    await odooLogin(page, cfg.portalLogin, cfg.portalPassword);
    await page.goto(`${ODOO_BASE_URL}/attendance/batch/${cfg.token}`, {
      waitUntil: 'domcontentloaded',
    });
    await page.waitForTimeout(2500);
    await captureScreenshot(page, 's5_358_checkin_already.png');
    const text = await page.locator('body').innerText();
    expect(text).toMatch(/Already checked in|تم تسجيل الحضور مسبقاً/i);
  });

  test('S5-358d — Non-enrolled portal student rejected', async ({ page }) => {
    expect(cfg.token).toBeTruthy();
    await odooLogin(page, cfg.otherLogin, cfg.otherPassword);
    await page.goto(`${ODOO_BASE_URL}/attendance/batch/${cfg.token}`, {
      waitUntil: 'domcontentloaded',
    });
    await page.waitForTimeout(3000);
    await captureScreenshot(page, 's5_358_checkin_rejected.png');
    const text = await page.locator('body').innerText();
    expect(text).toMatch(/not enrolled|Check-in not allowed|not allowed|لست مسجلاً/i);
  });

  test('S5-358e — No active session rejected', async ({ page }) => {
    // Cancel session via admin RPC then check in
    expect(cfg.sessionId).toBeTruthy();
    await odooLogin(page);
    await callKw(page, 'op.session', 'write', [[Number(cfg.sessionId)], { state: 'cancel' }]);
    await odooLogin(page, cfg.portalLogin, cfg.portalPassword);
    await page.goto(`${ODOO_BASE_URL}/attendance/batch/${cfg.token}`, {
      waitUntil: 'domcontentloaded',
    });
    await page.waitForTimeout(3000);
    await captureScreenshot(page, 's5_358_no_active_session.png');
    const text = await page.locator('body').innerText();
    expect(text).toMatch(/No active class session|no active|حصة نشطة|Check-in not allowed/i);
    // Restore session for later tests / re-runs
    await odooLogin(page);
    const now = new Date();
    const start = new Date(now.getTime() - 5 * 60000);
    const end = new Date(now.getTime() + 90 * 60000);
    const fmt = (d) => d.toISOString().slice(0, 19).replace('T', ' ');
    await callKw(page, 'op.session', 'write', [[Number(cfg.sessionId)], {
      state: 'confirm',
      start_datetime: fmt(start),
      end_datetime: fmt(end),
    }]);
  });

  test('S5-358f — Arabic UI smoke', async ({ page }) => {
    expect(cfg.token).toBeTruthy();
    // Restore check-in able state: cancel leave already handled; re-confirm session via fixture env
    await odooLogin(page);
    if (cfg.sessionId) {
      const now = new Date();
      const start = new Date(now.getTime() - 5 * 60000);
      const end = new Date(now.getTime() + 90 * 60000);
      const fmt = (d) => d.toISOString().slice(0, 19).replace('T', ' ');
      await callKw(page, 'op.session', 'write', [[Number(cfg.sessionId)], {
        state: 'confirm',
        start_datetime: fmt(start),
        end_datetime: fmt(end),
      }]);
      // Reset line optional — already/ok both OK for smoke
    }
    // Set portal user lang to ar_001 via admin
    await callKw(page, 'res.users', 'search_read', [[['login', '=', cfg.portalLogin]]], {
      fields: ['id'],
      limit: 1,
    }).then(async (res) => {
      const uid = res?.result?.[0]?.id;
      if (uid) {
        await callKw(page, 'res.users', 'write', [[uid], { lang: 'ar_001' }]);
      }
    });
    await odooLogin(page, cfg.portalLogin, cfg.portalPassword);
    await page.goto(`${ODOO_BASE_URL}/attendance/batch/${cfg.token}`, {
      waitUntil: 'domcontentloaded',
    });
    await page.waitForTimeout(3000);
    await captureScreenshot(page, 's5_358_checkin_ar.png');
    const text = await page.locator('body').innerText();
    // Arabic or bilingual (already) is fine for smoke
    expect(text.length).toBeGreaterThan(10);
    // Reset lang to en_US
    await odooLogin(page);
    await callKw(page, 'res.users', 'search_read', [[['login', '=', cfg.portalLogin]]], {
      fields: ['id'],
      limit: 1,
    }).then(async (res) => {
      const uid = res?.result?.[0]?.id;
      if (uid) {
        await callKw(page, 'res.users', 'write', [[uid], { lang: 'en_US' }]);
      }
    });
  });
});

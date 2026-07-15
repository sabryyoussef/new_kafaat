/**
 * Meeting S5 — Playwright proofs
 * OP#358 — Batch QR portal attendance
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
  screenshotPath,
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
    portalLogin: process.env.S5_PORTAL_LOGIN || out.S5_PORTAL_LOGIN,
    portalPassword: process.env.S5_PORTAL_PASSWORD || out.S5_PORTAL_PASSWORD,
    otherLogin: process.env.S5_OTHER_LOGIN || out.S5_OTHER_LOGIN,
    otherPassword: process.env.S5_OTHER_PASSWORD || out.S5_OTHER_PASSWORD,
  };
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
    expect(body).toMatch(/Attendance QR|QR Check-in|attendance_qr/i);
    const views = await callKw(page, 'op.batch', 'get_views', [], {
      views: [[false, 'form']],
      options: {},
    });
    expect(JSON.stringify(views.result || views)).toContain('attendance_qr_token');
  });

  test('S5-358b — Enrolled portal student checks in', async ({ page }) => {
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

  test('S5-358c — Non-enrolled portal student rejected', async ({ page }) => {
    expect(cfg.token).toBeTruthy();
    await odooLogin(page, cfg.otherLogin, cfg.otherPassword);
    await page.goto(`${ODOO_BASE_URL}/attendance/batch/${cfg.token}`, {
      waitUntil: 'domcontentloaded',
    });
    await page.waitForTimeout(3000);
    await captureScreenshot(page, 's5_358_checkin_rejected.png');
    const text = await page.locator('body').innerText();
    expect(text).toMatch(/not enrolled|Check-in not allowed|not allowed/i);
  });
});

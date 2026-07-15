/**
 * Meeting S2 — Playwright proofs with screenshots
 *
 * OP#352 — application_status (حالة الطالب)
 * OP#354 — Batch Arabic guide context shots (list/form)
 *
 * Screenshots → docs/op_meeting_nabil/evidence/screenshots/
 */
import { test, expect } from '@playwright/test';
import {
  callKw,
  captureScreenshot,
  dismissModals,
  fieldValue,
  odooLogin,
  openStudentForm,
  openStudentsList,
  PROOF_STUDENT_ID,
  ODOO_BASE_URL,
} from './helpers.mjs';

test.describe('Meeting S2 proofs (#352 / #354)', () => {
  test.beforeEach(async ({ page }) => {
    await odooLogin(page);
  });

  test('S2-352a — Student form shows application_status (حالة الطالب)', async ({ page }) => {
    await openStudentForm(page, PROOF_STUDENT_ID);
    await captureScreenshot(page, 's2_352_student_form_application_status.png');

    const body = await page.locator('.o_form_view, .o_form_sheet').first().innerText();
    expect(body).toMatch(/حالة الطالب/);

    const status = await fieldValue(page, 'application_status');
    expect(status.length).toBeGreaterThan(0);

    const views = await callKw(page, 'op.student', 'get_views', [], {
      views: [[false, 'form']],
      options: {},
    });
    const payload = JSON.stringify(views.result || views);
    expect(payload).toContain('application_status');
  });

  test('S2-352b — List/search include application_status', async ({ page }) => {
    await openStudentsList(page);
    await captureScreenshot(page, 's2_352_students_list_application_status.png');

    const views = await callKw(page, 'op.student', 'get_views', [], {
      views: [
        [false, 'list'],
        [false, 'search'],
      ],
      options: {},
    });
    const payload = JSON.stringify(views.result || views);
    expect(payload).toContain('application_status');
    expect(payload).toMatch(/حالة الطالب/);

    const read = await callKw(page, 'op.student', 'read', [
      [Number(PROOF_STUDENT_ID)],
      ['application_status', 'active'],
    ]);
    const row = (read.result || read)[0];
    expect(row.application_status).toBeTruthy();
    expect(row.active).toBe(true);
  });

  test('S2-354 — Batch Intakes list opens (guide context)', async ({ page }) => {
    await page.goto(
      `${ODOO_BASE_URL}/web#action=1380&model=batch.intake&view_type=list`,
      { waitUntil: 'domcontentloaded' },
    );
    await page.waitForTimeout(6000);
    await dismissModals(page);
    await captureScreenshot(page, 's2_354_batch_intakes_list.png');

    const countJson = await callKw(page, 'batch.intake', 'search_count', [[]]);
    expect(Number(countJson.result ?? countJson)).toBeGreaterThanOrEqual(0);
  });
});

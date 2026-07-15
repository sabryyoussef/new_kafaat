/**
 * Meeting S1 — Playwright proofs with screenshots
 *
 * OP#351 — Search trainees by national ID (رقم الهوية)
 * OP#353 — Voucher Number on student profile
 * OP#356 — Courses visibility context (admin Courses list count)
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
  searchStudents,
  PROOF_ID_NUMBER,
  PROOF_STUDENT_ID,
  PROOF_VOUCHER,
  ODOO_BASE_URL,
} from './helpers.mjs';

test.describe('Meeting S1 proofs (#351 / #353 / #356)', () => {
  test.beforeEach(async ({ page }) => {
    await odooLogin(page);
  });

  test('S1-351a — Search view exposes id_number (رقم الهوية)', async ({ page }) => {
    await openStudentsList(page);

    const searchViews = await callKw(page, 'op.student', 'get_views', [], {
      views: [[false, 'search']],
      options: {},
    });
    const payload = JSON.stringify(searchViews.result || searchViews);
    expect(payload).toContain('id_number');
    expect(payload).toMatch(/رقم الهوية/);

    await captureScreenshot(page, 's1_351_students_list_before_search.png');
  });

  test('S1-351b — Search students by national ID finds proof trainee', async ({ page }) => {
    await openStudentsList(page);
    await searchStudents(page, PROOF_ID_NUMBER);
    await captureScreenshot(page, 's1_351_search_by_id_number.png');

    const listText = await page
      .locator('.o_list_renderer, .o_content, .o_list_view')
      .first()
      .innerText();
    expect(listText).toContain(PROOF_ID_NUMBER);

    const nameSearch = await callKw(page, 'op.student', 'name_search', [
      PROOF_ID_NUMBER,
      [],
      'ilike',
      10,
    ]);
    const hits = (nameSearch.result || nameSearch).map((h) => h[0]);
    expect(hits).toContain(Number(PROOF_STUDENT_ID));
  });

  test('S1-353a — Student form shows voucher_number with Arabic label', async ({ page }) => {
    await openStudentForm(page, PROOF_STUDENT_ID);
    await captureScreenshot(page, 's1_353_student_form_voucher.png');

    const body = await page.locator('.o_form_view, .o_form_sheet').first().innerText();
    expect(body).toMatch(/رقم قسيمة الاختبار/);
    expect(body).toMatch(/رقم الهوية/);

    const voucher = await fieldValue(page, 'voucher_number');
    expect(voucher).toContain(PROOF_VOUCHER);

    const idNumber = await fieldValue(page, 'id_number');
    expect(idNumber).toContain(PROOF_ID_NUMBER);
  });

  test('S1-353b — List/search arch includes voucher_number', async ({ page }) => {
    await openStudentsList(page);

    const listViews = await callKw(page, 'op.student', 'get_views', [], {
      views: [
        [false, 'list'],
        [false, 'search'],
      ],
      options: {},
    });
    const payload = JSON.stringify(listViews.result || listViews);
    expect(payload).toContain('voucher_number');
    expect(payload).toMatch(/رقم قسيمة الاختبار/);

    await searchStudents(page, PROOF_VOUCHER);
    await captureScreenshot(page, 's1_353_search_by_voucher.png');

    const found = await callKw(page, 'op.student', 'search', [
      [['voucher_number', '=', PROOF_VOUCHER]],
    ]);
    const ids = found.result || found;
    expect(ids).toContain(Number(PROOF_STUDENT_ID));
  });

  test('S1-356 — Admin Courses list is not capped at two (context)', async ({ page }) => {
    await page.goto(
      `${ODOO_BASE_URL}/web#action=openeducat_core.act_open_op_course_view&model=op.course&view_type=list`,
      { waitUntil: 'domcontentloaded' },
    );
    await page.waitForTimeout(7000);
    await dismissModals(page);
    await captureScreenshot(page, 's1_356_admin_courses_list.png');

    const countJson = await callKw(page, 'op.course', 'search_count', [[]]);
    const total = countJson.result ?? countJson;
    expect(Number(total)).toBeGreaterThan(2);

    await captureScreenshot(page, 's1_356_courses_count_context.png');
  });
});

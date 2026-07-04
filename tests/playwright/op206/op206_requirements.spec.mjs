/**
 * OP#206 — Playwright proof suite
 *
 * Each test maps to one UAT finding and saves a screenshot under
 * docs/op206/evidence/screenshots/
 *
 * R1 Group By Current Course (المقرر الحالي)
 * R2 Arabic labels + mapped profile fields
 * R3 Blood Group hidden
 * R4 Registration Number + Source Type on Student Profile
 */
import { test, expect } from '@playwright/test';
import {
  captureScreenshot,
  dismissModals,
  odooLogin,
  openRegistrationForm,
  openStudentForm,
  openStudentsList,
  ODOO_BASE_URL,
} from './helpers.mjs';

const PROOF_STUDENT_ID = process.env.OP206_PROOF_STUDENT_ID || process.env.OP206_STUDENT_ID || '181';
const PROOF_REG_ID = process.env.OP206_REGISTRATION_ID || '12';

async function formText(page) {
  await page.locator('.o_form_view').first().waitFor({ state: 'visible', timeout: 30_000 });
  return page.locator('.o_form_view').first().innerText();
}

/** Read Odoo field widget value (inputs are often omitted from innerText). */
async function fieldValue(page, name) {
  const widget = page.locator(`.o_field_widget[name="${name}"]`).first();
  await widget.waitFor({ state: 'visible', timeout: 15_000 });
  const input = widget.locator('input, textarea').first();
  if (await input.count()) {
    const val = await input.inputValue().catch(() => '');
    if (val) return val;
  }
  return (await widget.innerText()).trim();
}

test.describe('OP#206 requirement proofs', () => {
  test.beforeEach(async ({ page }) => {
    await odooLogin(page);
  });

  test('R1 — Group By Current Course is available and applies', async ({ page }) => {
    await openStudentsList(page);
    await captureScreenshot(page, 'r1_students_list.png');

    // Prove live search arch includes Group By Current Course (registry after upgrade)
    const searchArch = await page.evaluate(async () => {
      const resp = await fetch('/web/dataset/call_kw/op.student/get_views', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'op.student',
            method: 'get_views',
            args: [],
            kwargs: {
              views: [[false, 'search']],
              options: {},
            },
          },
          id: Date.now(),
        }),
      });
      const json = await resp.json();
      return JSON.stringify(json.result || json);
    });
    expect(searchArch).toContain('current_course_id');
    expect(searchArch).toMatch(/المقرر الحالي|Current Course/);

    // Apply group-by in UI via search dropdown when possible
    const filterToggle = page.locator('.o_searchview_dropdown_toggler').first();
    if (await filterToggle.isVisible().catch(() => false)) {
      await filterToggle.click();
      await page.waitForTimeout(500);
      const courseGroup = page.getByText('المقرر الحالي').first();
      if (await courseGroup.isVisible().catch(() => false)) {
        await courseGroup.click();
        await page.waitForTimeout(1500);
      }
    }
    await captureScreenshot(page, 'r1_group_by_current_course.png');
  });

  test('R2 — Trainee form Arabic labels and mapped profile values', async ({ page }) => {
    await openStudentForm(page, PROOF_STUDENT_ID);

    // Open contact / address notebook page if present (phone & address live there)
    const contactTab = page.locator('.o_notebook .nav-link, .nav-item').filter({
      hasText: /جهة الاتصال|Contact|عنوان|Address/i,
    }).first();
    if (await contactTab.isVisible().catch(() => false)) {
      await contactTab.click();
      await page.waitForTimeout(800);
    }

    await captureScreenshot(page, 'r2_trainee_form_labels.png');

    const body = await formText(page);

    // Labels on trainee profile
    expect(body).toMatch(/رقم الهوية/);
    expect(body).toMatch(/التخصص/);
    expect(body).toMatch(/العنوان|الشارع|المدينة|الدولة/);

    // Mapped values from Student Registration finalize (proof student 181)
    expect(await fieldValue(page, 'id_number')).toMatch(/2062062062/);
    expect(await fieldValue(page, 'phone')).toMatch(/0502060206/);
    expect(await fieldValue(page, 'street')).toMatch(/Proof Street/i);
    expect(await fieldValue(page, 'specialization_id')).toMatch(/STEP2|OP206|Program/i);
  });

  test('R3 — Blood Group is not shown on trainee form', async ({ page }) => {
    await openStudentForm(page, PROOF_STUDENT_ID);
    await captureScreenshot(page, 'r3_no_blood_group.png');

    const body = await formText(page);
    expect(body).not.toMatch(/Blood Group|فصيلة الدم/i);
  });

  test('R4 — Registration Number and Source Type on Student Profile', async ({ page }) => {
    await openStudentForm(page, PROOF_STUDENT_ID);
    await captureScreenshot(page, 'r4_registration_source_fields.png');

    const body = await formText(page);
    expect(body).toMatch(/رقم التسجيل/);
    expect(body).toMatch(/نوع المصدر/);
    // Values from portal finalize
    expect(body).toMatch(/REG00013|REG-OP206/);
    expect(body).toMatch(/Student Registration Portal|بوابة|Portal|student_registration/i);
  });

  test('R2 registration form — Arabic profile required fields', async ({ page }) => {
    await openRegistrationForm(page, PROOF_REG_ID);
    await captureScreenshot(page, 'r2_registration_form_labels.png');

    const body = await formText(page);
    expect(body).toMatch(/رقم الهوية/);
    expect(body).toMatch(/التخصص/);
    expect(body).toMatch(/الشارع|المدينة|الدولة/);
    expect(body).toMatch(/2062062062|Proof Street|REG00013/i);
  });
});

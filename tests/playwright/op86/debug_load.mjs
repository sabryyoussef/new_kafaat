import { chromium } from '@playwright/test';
import { ODOO_BASE_URL, ODOO_DB, ODOO_PASSWORD, dismissModals, odooLogin, screenshotPath } from './helpers.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await odooLogin(page);

const urls = [
  [`students`, `${ODOO_BASE_URL}/odoo/students`],
  [`student_form_hash`, `${ODOO_BASE_URL}/web#id=80&model=op.student&view_type=form`],
  [`student_form_path`, `${ODOO_BASE_URL}/odoo/op.student/80`],
  [`reg_form`, `${ODOO_BASE_URL}/odoo/student.registration/10`],
];

for (const [name, url] of urls) {
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  for (let t = 0; t < 24; t += 1) {
    await page.waitForTimeout(5000);
    await dismissModals(page);
    const len = await page.evaluate(() => document.body.innerText.length);
    console.log(name, 't', (t + 1) * 5, 'chars', len, 'url', page.url());
    if (len > 200) break;
  }
  await page.screenshot({ path: screenshotPath(`debug/final_${name}.png`), fullPage: true });
}

await browser.close();

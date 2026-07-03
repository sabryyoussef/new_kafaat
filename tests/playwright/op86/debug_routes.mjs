import { chromium } from '@playwright/test';
import { odooLogin, dismissModals, screenshotPath } from './helpers.mjs';
import fs from 'fs';

fs.mkdirSync(screenshotPath('debug'), { recursive: true });

const routes = [
  '/web#action=1311&model=op.student&view_type=list',
  '/odoo/students',
  '/odoo/op-student/80',
  '/web#id=80&model=op.student&view_type=form',
  '/web#id=10&model=student.registration&view_type=form',
];

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.setDefaultTimeout(30000);

await odooLogin(page);

const report = [];
for (const route of routes) {
  await page.goto(`http://127.0.0.1:8069${route}`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(5000);
  await dismissModals(page);
  const name = route.replace(/[^a-zA-Z0-9]+/g, '_').slice(0, 40);
  await page.screenshot({ path: screenshotPath(`debug/${name}.png`), fullPage: true });
  report.push({
    route,
    url: page.url(),
    title: await page.title(),
    hasList: await page.locator('.o_list_view').count(),
    hasForm: await page.locator('.o_form_view').count(),
    hasDataRow: await page.locator('.o_data_row').count(),
    bodySnippet: (await page.locator('body').innerText()).slice(0, 300),
  });
}

console.log(JSON.stringify(report, null, 2));
await browser.close();

import { chromium } from '@playwright/test';
import { odooLogin, dismissModals, ODOO_BASE_URL } from './helpers.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await odooLogin(page);
await page.goto(`${ODOO_BASE_URL}/odoo`);
await page.waitForTimeout(2000);
await dismissModals(page);
const apps = await page.evaluate(() =>
  [...document.querySelectorAll('.o_app')].map((el) => ({
    text: el.innerText.trim(),
    xmlid: el.getAttribute('data-menu-xmlid'),
    href: el.getAttribute('href'),
    className: el.className,
  })),
);
console.log(JSON.stringify(apps.filter((a) => /SIS|Student|openeducat/i.test(a.text + (a.xmlid || ''))), null, 2));
await browser.close();

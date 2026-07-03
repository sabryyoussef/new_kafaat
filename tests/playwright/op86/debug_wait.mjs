import { chromium } from '@playwright/test';
import { odooLogin, dismissModals, screenshotPath } from './helpers.mjs';
import fs from 'fs';

fs.mkdirSync(screenshotPath('debug'), { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await odooLogin(page);
await page.goto('http://127.0.0.1:8069/web#action=1311&model=op.student&view_type=list');
for (const wait of [5000, 10000, 15000, 20000]) {
  await page.waitForTimeout(5000);
  await page.keyboard.press('Escape');
  await dismissModals(page);
  const info = await page.evaluate(() => ({
    url: location.href,
    classes: [...document.querySelectorAll('[class*="list"], [class*="List"], .o_action_manager, .o_view_controller')].slice(0, 20).map((el) => el.className),
    textLen: document.body.innerText.length,
    sample: document.body.innerText.slice(0, 500),
  }));
  console.log('wait', wait, JSON.stringify(info, null, 2));
  await page.screenshot({ path: screenshotPath(`debug/wait_${wait}.png`), fullPage: true });
}

await browser.close();

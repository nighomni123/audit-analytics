const { chromium } = require('/Users/Mitesh Gada/Documents/Projects/Do not delete folder/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  // Step 5 — Serve / Web UI review page (main)
  await page.goto('http://127.0.0.1:8788/', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'docs/screenshots/05-serve-ui.png', fullPage: true });
  console.log('captured 05-serve-ui.png');

  // Mobile width
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('http://127.0.0.1:8788/', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'docs/screenshots/06-serve-ui-mobile.png', fullPage: true });
  console.log('captured 06-serve-ui-mobile.png');

  // Click through to an exception detail (if nav available) — try /exception/1 or similar
  try {
    await page.goto('http://127.0.0.1:8788/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'docs/screenshots/07-serve-exception-detail.png', fullPage: false });
    console.log('captured 07-serve-exception-detail.png');
  } catch (e) { console.log('detail capture skipped:', e.message); }

  await browser.close();
})();

const { chromium } = require("playwright");
const path = require("node:path");

const outputDirectory = path.resolve(__dirname, "../../docs/screenshots");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto("http://127.0.0.1:8788/", { waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(outputDirectory, "05-serve-ui.png"), fullPage: true });
  console.log("captured 05-serve-ui.png");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("http://127.0.0.1:8788/", { waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(outputDirectory, "06-serve-ui-mobile.png"), fullPage: true });
  console.log("captured 06-serve-ui-mobile.png");
  await browser.close();
})();

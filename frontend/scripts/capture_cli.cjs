const { chromium } = require("playwright");
const fs = require("node:fs");
const path = require("node:path");

const outputDirectory = path.resolve(__dirname, "../../docs/screenshots");
const steps = [
  { file: "/tmp/step01_init.txt", title: "Step 1 — Init synthetic engagement", out: "01-init.png", cmd: "python3 run.py init --db demo-engagement.db ..." },
  { file: "/tmp/step02_import.txt", title: "Step 2 — Import 400-row synthetic GL", out: "02-import-gl.png", cmd: "python3 run.py import-gl --db demo-engagement.db ..." },
  { file: "/tmp/step03_ack.txt", title: "Step 3 — Acknowledge population", out: "03-ack.png", cmd: "python3 run.py acknowledge-population ..." },
  { file: "/tmp/step04_analyze.txt", title: "Step 4 — Analyze", out: "04-analyze.png", cmd: "python3 run.py analyze --db demo-engagement.db --actor reviewer" },
];

(async () => {
  fs.mkdirSync(outputDirectory, { recursive: true });
  const browser = await chromium.launch();
  for (const step of steps) {
    const text = fs.readFileSync(step.file, "utf8");
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>body{background:#0b0c10;color:#00ff88;font-family:monospace;padding:40px;font-size:15px;line-height:1.5}h1{font-size:22px;color:#fff;border-left:4px solid #00ff88;padding-left:12px;margin-bottom:6px}.subtitle{color:#888;font-size:13px;margin-bottom:24px}pre{background:#15161b;padding:18px;border-radius:10px;border:1px solid #222;overflow:auto;white-space:pre-wrap;word-break:break-word}</style></head><body><h1>${step.title}</h1><div class="subtitle">${step.cmd}</div><pre>${text.replace(/</g, "&lt;")}</pre></body></html>`;
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
    await page.setContent(html, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(outputDirectory, step.out), fullPage: true });
    await page.close();
    console.log(`captured ${step.out}`);
  }
  await browser.close();
})();

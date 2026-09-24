import path from "node:path";
import { expect, test } from "@playwright/test";

const demoLedger = path.resolve(process.cwd(), "../examples/demo-journal-entries.csv");

test("complete persisted workbench workflow at desktop and mobile", async ({ page }) => {
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Engagement" })).toBeVisible();

  await page.getByLabel("Client name").fill("Synthetic Browser Client");
  await page.getByLabel("Audit period").fill("2025-04-01:2026-03-31");
  await page.getByLabel("Local owner").fill("manager");
  await page.getByRole("button", { name: "Create engagement" }).click();
  await expect(page.getByRole("heading", { name: "Population & Configuration" })).toBeVisible();

  await page.getByLabel("CSV or bounded XLSX source").setInputFiles(demoLedger);
  await page.getByRole("button", { name: "Preview source" }).click();
  await expect(page.getByText(/All required concepts detected/)).toBeVisible();
  await page.getByLabel("Expected rows").fill("400");
  await page.getByLabel("Expected debits").fill("3496407.62");
  await page.getByLabel("Expected credits").fill("0");
  await page.getByRole("button", { name: "Import ledger" }).click();
  await expect(page.getByText(/stored 400 accepted/)).toBeVisible();

  await page.getByLabel("Acknowledgement note").fill("Synthetic browser verification; control totals match.");
  await page.getByRole("button", { name: "Acknowledge population" }).click();
  await expect(page.getByText(/analysis is unlocked/)).toBeVisible();

  await page.getByLabel("Overall materiality").fill("500000");
  await page.getByLabel("Performance materiality").fill("350000");
  await page.getByRole("button", { name: "Save parameters" }).click();
  await expect(page.getByText("Engagement parameters were saved.")).toBeVisible();

  await page.getByRole("button", { name: "Run analysis" }).click();
  await expect(page.getByRole("heading", { name: "Risk Dashboard" })).toBeVisible();
  await expect(page.locator("tbody tr").first()).toBeVisible();

  const firstInvestigate = page.getByRole("button", { name: /^Investigate / }).first();
  const entryButtonText = await firstInvestigate.textContent();
  await firstInvestigate.click();
  await expect(page.getByRole("heading", { name: "Investigation & Review" })).toBeVisible();
  await expect(page.getByText(entryButtonText?.replace("Investigate ", "") ?? "", { exact: true }).first()).toBeVisible();

  await page.getByLabel("Disposition").selectOption("follow_up");
  await page.getByLabel("Audit rationale / evidence requested").fill("Browser workflow persisted this follow-up note.");
  await page.getByRole("button", { name: "Save disposition" }).click();
  await expect(page.getByText(/Disposition appended/)).toBeVisible();
  await expect(page.getByText("Browser workflow persisted this follow-up note.")).toBeVisible();
  await page.reload();
  await expect(page.getByText("follow up", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Browser workflow persisted this follow-up note.")).toBeVisible();

  await page.getByLabel("Reason").fill("Synthetic browser review set complete.");
  await page.getByRole("button", { name: "Lock review set" }).click();
  await expect(page.getByText("Review set locked.")).toBeVisible();
  await expect(page.getByText(/The review set is locked/)).toBeVisible();
  await page.screenshot({ path: "test-results/workbench-desktop.png", fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/#/dashboard");
  await expect(page.getByRole("heading", { name: "Risk Dashboard" })).toBeVisible();
  const fitsViewport = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
  expect(fitsViewport).toBe(true);
  await page.screenshot({ path: "test-results/workbench-mobile.png", fullPage: true });

  expect(pageErrors).toEqual([]);
});

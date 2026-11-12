import { expect, test } from "@playwright/test";

const ADMIN = "admin";
const PASSWORD = "e2e-admin-password";

async function login(page: import("@playwright/test").Page): Promise<void> {
  await page.goto("/");
  await page.getByLabel("Gebruikersnaam").fill(ADMIN);
  await page.getByLabel("Wachtwoord").fill(PASSWORD);
  await page.getByRole("button", { name: "Inloggen" }).click();
  await expect(page.getByRole("heading", { name: "Devices" })).toBeVisible();
}

test("login toont het dashboard met een live device", async ({ page }) => {
  await login(page);
  await expect(page.getByText("MFC-E2E")).toBeVisible();
  await expect(page.getByText("online").first()).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("live")).toBeVisible();
});

test("setpoint schrijven met bevestiging en auditregel", async ({ page }) => {
  await login(page);
  await page.getByRole("link", { name: "Openen" }).click();
  await expect(page.getByRole("heading", { name: "MFC-E2E" })).toBeVisible();

  await page.getByLabel("Waarde").fill("50");
  await page.getByRole("button", { name: "Setpoint wijzigen" }).click();
  await page.getByRole("button", { name: "Bevestigen" }).click();

  await expect(page.getByText("Setpoint geschreven")).toBeVisible({ timeout: 15_000 });

  await page.getByRole("link", { name: "Audit" }).click();
  await expect(page.getByText("device.setpoint").first()).toBeVisible();
});
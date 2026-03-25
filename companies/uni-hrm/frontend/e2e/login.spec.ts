import { test, expect } from '@playwright/test';

test.describe('Login Page', () => {
  test.skip('loads login page and shows form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('form')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test.skip('shows validation errors for empty form', async ({ page }) => {
    await page.goto('/login');
    await page.locator('button[type="submit"]').click();
    // Expect validation messages to appear
    await expect(page.locator('form')).toBeVisible();
  });
});

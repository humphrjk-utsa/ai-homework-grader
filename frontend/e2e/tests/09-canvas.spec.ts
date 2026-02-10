import { test, expect } from '@playwright/test';

test.describe('Canvas Settings', () => {
  test('settings page renders with form fields', async ({ page }) => {
    await page.goto('/canvas/settings');

    await expect(page.getByRole('heading', { name: 'Canvas LMS Integration' })).toBeVisible();
    await expect(page.getByText('Connection Settings')).toBeVisible();
    await expect(page.getByPlaceholder('https://canvas.university.edu')).toBeVisible();
  });

  test('save canvas settings shows confirmation', async ({ page }) => {
    // Mock the settings save
    await page.route('**/api/canvas/settings', async (route) => {
      if (route.request().method() === 'PUT') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'Canvas settings saved' }),
        });
      } else {
        // GET returns current settings
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ canvas_url: '', has_token: false }),
        });
      }
    });

    await page.goto('/canvas/settings');

    await page.getByPlaceholder('https://canvas.university.edu').fill('https://canvas.test.edu');
    await page
      .getByPlaceholder(/paste your canvas api token/i)
      .fill('fake-token-12345');

    await page.getByRole('button', { name: 'Save Settings' }).click();

    await expect(page.getByText('Settings saved')).toBeVisible({ timeout: 5_000 });
  });

  test('test connection shows success with mocked API', async ({ page }) => {
    // Mock settings GET to show token is saved
    await page.route('**/api/canvas/settings', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ canvas_url: 'https://canvas.test.edu', has_token: true }),
      });
    });

    // Mock test connection
    await page.route('**/api/canvas/test', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          connected: true,
          user: { id: 1, name: 'Canvas Test User' },
        }),
      });
    });

    await page.goto('/canvas/settings');

    await page.getByRole('button', { name: 'Test Connection' }).click();

    await expect(page.getByText('Connected as: Canvas Test User')).toBeVisible({
      timeout: 5_000,
    });
  });
});

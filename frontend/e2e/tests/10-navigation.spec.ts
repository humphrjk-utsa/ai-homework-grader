import { test, expect } from '@playwright/test';

test.describe('Navigation and Auth Guards', () => {
  test('unauthenticated user redirected to /login', async ({ browser }) => {
    // Fresh context with explicitly empty storage state (no auth tokens)
    const context = await browser.newContext({
      storageState: { cookies: [], origins: [] },
    });
    const page = await context.newPage();

    await page.goto('http://localhost:5173/courses');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });

    await context.close();
  });

  test('nav bar shows correct links', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('link', { name: 'DeepSight' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Courses' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Canvas' })).toBeVisible();
  });

  test('nav shows user name', async ({ page }) => {
    await page.goto('/');

    // User registered as "E2E Tester"
    await expect(page.getByText('E2E Tester')).toBeVisible();
  });

  test('logout button works', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('button', { name: 'Logout' }).click();

    await expect(page).toHaveURL(/\/login/, { timeout: 5_000 });
  });

  test('dashboard link works from courses page', async ({ page }) => {
    await page.goto('/courses');

    await page.getByRole('link', { name: 'DeepSight' }).click();

    await expect(page).toHaveURL('/');
  });

  test('courses link works from dashboard', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: 'Courses' }).click();

    await expect(page).toHaveURL('/courses');
  });

  test('back to course link from assignment detail', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    await page.getByText('Back to course').click();

    await expect(page).toHaveURL(/\/courses\/\d+/);
  });
});

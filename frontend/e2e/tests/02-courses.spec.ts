import { test, expect } from '@playwright/test';

test.describe('Courses', () => {
  test('create course with all fields', async ({ page }) => {
    await page.goto('/courses/new');

    await expect(page.getByRole('heading', { name: 'New Course' })).toBeVisible();

    await page.getByPlaceholder('e.g. Business Analytics').fill('E2E Analytics');
    await page.getByPlaceholder('e.g. BA 501').fill('BA-E2E');
    await page.locator('select').first().selectOption('Spring');
    await page.locator('input[type="number"]').fill('2026');

    await page.getByRole('button', { name: 'Create Course' }).click();

    // Should redirect to course detail
    await expect(page).toHaveURL(/\/courses\/\d+/, { timeout: 10_000 });
    await expect(page.getByRole('heading', { name: 'E2E Analytics' })).toBeVisible();
  });

  test('course appears in course list', async ({ page }) => {
    await page.goto('/courses');

    await expect(page.getByText('E2E Analytics')).toBeVisible();
    await expect(page.getByText('BA-E2E')).toBeVisible();
  });

  test('course detail shows Assignments and Students tabs', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();

    await expect(page.getByRole('button', { name: /Assignments/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Students/i })).toBeVisible();
  });

  test('assignments tab shows empty state', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();

    await expect(page.getByText(/no assignments/i)).toBeVisible();
    await expect(page.getByRole('link', { name: /new assignment/i })).toBeVisible();
  });

  test('students tab shows empty state', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();

    await page.getByRole('button', { name: /Students/i }).click();

    await expect(page.getByText(/no students/i)).toBeVisible();
  });

  test('create course requires name', async ({ page }) => {
    await page.goto('/courses/new');

    // Leave name empty, try to submit
    await page.locator('input[type="number"]').fill('2026');

    const button = page.getByRole('button', { name: 'Create Course' });
    await button.click();

    // Should still be on the new course page (HTML5 validation prevents submit)
    await expect(page).toHaveURL(/\/courses\/new/);
  });
});

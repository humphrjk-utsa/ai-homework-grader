import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEST_DATA = path.resolve(__dirname, '..', 'test-data');

test.describe('Students', () => {
  test('add single student via form', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByRole('button', { name: /Students/i }).click();
    await page.getByRole('link', { name: /add student/i }).click();

    await expect(page.getByRole('heading', { name: /add student/i })).toBeVisible();

    await page.locator('label:has-text("First Name") + input').fill('Manual');
    await page.locator('label:has-text("Last Name") + input').fill('Student');
    await page.locator('label:has-text("Email") + input').fill('manual@test.edu');

    await page.getByRole('button', { name: /add student/i }).click();

    // Should redirect back to course detail
    await expect(page).toHaveURL(/\/courses\/\d+/, { timeout: 10_000 });
  });

  test('student appears in students tab', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByRole('button', { name: /Students/i }).click();

    await expect(page.getByRole('cell', { name: 'Manual Student' })).toBeVisible();
  });

  test('import students from CSV', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByRole('button', { name: /Students/i }).click();
    await page.getByRole('link', { name: /import csv/i }).click();

    await expect(page.getByRole('heading', { name: /import students/i })).toBeVisible();

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(TEST_DATA, 'students.csv'));

    await page.getByRole('button', { name: /import/i }).click();

    // Should show success message
    await expect(page.getByText(/imported.*3/i)).toBeVisible({ timeout: 10_000 });
  });

  test('imported students appear in list', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByRole('button', { name: /Students/i }).click();

    // Check for CSV-imported students using cell role for specificity
    await expect(page.getByRole('cell', { name: 'Jane Smith' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'Bob Jones' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'Alice Chen' })).toBeVisible();
  });
});

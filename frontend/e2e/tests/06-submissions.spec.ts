import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEST_DATA = path.resolve(__dirname, '..', 'test-data');

test.describe('Submissions', () => {
  test('upload single submission file', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    // Upload with Canvas-format filename so backend can identify the student.
    // Student "Jane Smith" has canvas_id=12345 (imported via CSV in test 05).
    const fileInput = page.locator('input[type="file"][accept]');
    const buffer = fs.readFileSync(path.join(TEST_DATA, 'sample-notebook.ipynb'));
    await fileInput.setInputFiles({
      name: 'smithjane_12345_submission.ipynb',
      mimeType: 'application/octet-stream',
      buffer,
    });

    // Wait for submission to appear in table
    await expect(page.getByText('Submissions (1)')).toBeVisible({ timeout: 10_000 });
  });

  test('submission appears in table with uploaded status', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    // Check for the uploaded status badge
    await expect(page.getByText('uploaded').first()).toBeVisible();
  });

  test('export buttons appear when submissions exist', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    await expect(page.getByText('Export CSV')).toBeVisible();
    await expect(page.getByText('Download Reports')).toBeVisible();
  });

  test('grade all button is visible', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    await expect(page.getByRole('button', { name: 'Grade All' })).toBeVisible();
  });
});

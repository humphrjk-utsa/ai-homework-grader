import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEST_DATA = path.resolve(__dirname, '..', 'test-data');

test.describe('Assignments', () => {
  test('create coding assignment', async ({ page }) => {
    // Navigate to course first
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await expect(page).toHaveURL(/\/courses\/\d+/);

    await page.getByRole('link', { name: /new assignment/i }).click();
    await expect(page).toHaveURL(/\/assignments\/new/);

    await page.getByPlaceholder('e.g. Homework 3').fill('E2E Homework');
    await page.locator('select').first().selectOption('coding');
    await page.locator('input[type="number"]').fill('100');

    // Language selector should appear for coding type
    const languageSelect = page.locator('select').nth(1);
    await expect(languageSelect).toBeVisible();
    await languageSelect.selectOption('R');

    await page.getByRole('button', { name: 'Create Assignment' }).click();

    // Should redirect to assignment detail
    await expect(page).toHaveURL(/\/assignments\/\d+/, { timeout: 10_000 });
    await expect(page.getByRole('heading', { name: 'E2E Homework' })).toBeVisible();
    await expect(page.getByText('100 points')).toBeVisible();
  });

  test('assignment detail shows file upload sections', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    await expect(page.getByText('Assignment Files')).toBeVisible();
    await expect(page.getByText('Rubric').first()).toBeVisible();
    await expect(page.getByText('Solution').first()).toBeVisible();
    await expect(page.getByText('Template').first()).toBeVisible();
  });

  test('build rubric link is visible', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    await expect(page.getByRole('link', { name: 'Build' })).toBeVisible();
  });

  test('upload rubric JSON file', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    // Find the rubric upload input (first file input in the rubric card)
    const rubricCard = page.locator('div:has(> p:text("Rubric"))').first();
    const fileInput = rubricCard.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(TEST_DATA, 'rubric.json'));

    // Wait for "Uploaded" text to appear
    await expect(rubricCard.getByText('Uploaded')).toBeVisible({ timeout: 10_000 });
  });

  test('upload solution notebook', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    const solutionCard = page.locator('div:has(> p:text("Solution"))').first();
    const fileInput = solutionCard.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(TEST_DATA, 'sample-notebook.ipynb'));

    await expect(solutionCard.getByText('Uploaded')).toBeVisible({ timeout: 10_000 });
  });

  test('AI prompts section opens and closes', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    // Click to expand AI Prompts
    await page.getByText('AI Prompts').click();

    // Should show prompt textareas
    await expect(page.getByText('Code Analysis Prompt')).toBeVisible();
    await expect(page.getByText('Feedback Prompt')).toBeVisible();

    // Click again to collapse
    await page.getByText('AI Prompts').click();

    await expect(page.getByText('Code Analysis Prompt')).not.toBeVisible();
  });
});

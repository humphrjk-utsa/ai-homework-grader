import { test, expect } from '@playwright/test';

test.describe('Rubric Builder', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the rubric builder for the E2E Homework assignment
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();
    await page.getByRole('link', { name: 'Build' }).click();
    await expect(page.getByRole('heading', { name: 'Rubric Builder' })).toBeVisible();
  });

  test('page loads with rubric data', async ({ page }) => {
    // Should show the assignment name and points
    await expect(page.getByText('E2E Homework')).toBeVisible();
    await expect(page.getByText('100 points')).toBeVisible();
  });

  test('can fill category name and points', async ({ page }) => {
    const nameInput = page.getByPlaceholder('e.g. Technical Execution').first();
    await nameInput.fill('Code Quality');

    // Points input
    const pointsInputs = page.locator('input[type="number"]');
    await pointsInputs.first().fill('50');

    await expect(nameInput).toHaveValue('Code Quality');
  });

  test('add second category', async ({ page }) => {
    const nameInputs = page.getByPlaceholder('e.g. Technical Execution');
    const initialCount = await nameInputs.count();

    await page.getByText('+ Add Category').click();

    // Should have one more category input than before
    await expect(nameInputs).toHaveCount(initialCount + 1);
  });

  test('points validation shows mismatch', async ({ page }) => {
    const nameInput = page.getByPlaceholder('e.g. Technical Execution').first();
    await nameInput.fill('Partial');

    // Set points that don't match total (100)
    const pointsInput = page.locator('input[type="number"][min="0"]').first();
    await pointsInput.fill('30');

    await expect(page.getByText(/do not match/i)).toBeVisible();
  });

  test('points validation shows match when totals equal', async ({ page }) => {
    // The uploaded rubric already has categories summing to 100 points (40+35+25)
    // So "Points match" should already be visible
    await expect(page.getByText(/points match/i)).toBeVisible();
  });

  test('scoring levels expand and collapse', async ({ page }) => {
    await page.getByText('Scoring Levels').first().click();

    // Should show scoring level inputs
    await expect(page.getByPlaceholder(/excellent performance/i).first()).toBeVisible();

    // Click again to collapse
    await page.getByText('Scoring Levels').first().click();
    await expect(page.getByPlaceholder(/excellent performance/i).first()).not.toBeVisible();
  });

  test('save rubric shows confirmation', async ({ page }) => {
    // Fill a complete category
    await page.getByPlaceholder('e.g. Technical Execution').first().fill('Full Category');

    const pointsInput = page.locator('input[type="number"][min="0"]').first();
    await pointsInput.fill('100');

    await page.getByPlaceholder('What does this category assess?').first().fill('Everything about the code');

    await page.getByRole('button', { name: 'Save Rubric' }).click();

    await expect(page.getByText('Saved')).toBeVisible({ timeout: 10_000 });
  });
});

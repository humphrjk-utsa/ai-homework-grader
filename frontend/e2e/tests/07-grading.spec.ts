import { test, expect } from '@playwright/test';

test.describe('Grading (mocked)', () => {
  test('batch grading shows progress bar with mocked API', async ({ page }) => {
    // Mock the batch grading endpoint
    await page.route('**/api/grading/batch/*', async (route) => {
      await route.fulfill({
        status: 202,
        contentType: 'application/json',
        body: JSON.stringify({
          job: {
            id: 999,
            assignment_id: 1,
            status: 'running',
            total_submissions: 3,
            completed_submissions: 0,
            failed_submissions: 0,
            progress_percent: 0,
          },
          async_mode: true,
        }),
      });
    });

    // Mock job polling
    let pollCount = 0;
    await page.route('**/api/grading/jobs/999', async (route) => {
      pollCount++;
      const done = pollCount >= 3;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          job: {
            id: 999,
            status: done ? 'completed' : 'running',
            total_submissions: 3,
            completed_submissions: done ? 3 : pollCount,
            failed_submissions: 0,
            progress_percent: done ? 100 : Math.round((pollCount / 3) * 100),
          },
        }),
      });
    });

    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    await page.getByRole('button', { name: 'Grade All' }).click();

    // Progress bar should appear
    await expect(page.getByText('Grading in progress...')).toBeVisible({ timeout: 5_000 });
  });

  test('grading API acceptance - real endpoint returns valid response', async ({ page }) => {
    await page.goto('/courses');
    await page.getByText('E2E Analytics').click();
    await page.getByText('E2E Homework').click();

    // Intercept to verify the request is accepted (not 400/404)
    const responsePromise = page.waitForResponse(
      (resp) => resp.url().includes('/api/grading/batch/'),
    );

    await page.getByRole('button', { name: 'Grade All' }).click();

    const response = await responsePromise;
    // 200 (sync fallback) or 202 (async) or 409 (already running) are all valid
    expect([200, 202, 409]).toContain(response.status());
  });
});

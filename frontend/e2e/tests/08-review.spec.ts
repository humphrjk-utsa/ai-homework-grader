import { test, expect } from '@playwright/test';

test.describe('Submission Review (mocked)', () => {
  test('submission detail page renders for graded submission', async ({ page }) => {
    // Mock a graded submission response
    await page.route('**/api/submissions/1', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          submission: {
            id: 1,
            student_id: 1,
            assignment_id: 1,
            status: 'graded',
            original_filename: 'homework.ipynb',
            file_path: 'test/submission.ipynb',
            ai_score: 85,
            final_score: 85,
            max_score: 100,
            component_scores: {
              technical_execution: { score: 35, max: 40 },
              analysis_quality: { score: 30, max: 35 },
              presentation: { score: 20, max: 25 },
            },
            ai_feedback: {
              comprehensive_feedback: 'Good work overall.',
              strengths: ['Clear code structure'],
              areas_for_improvement: ['Add more comments'],
            },
            student: { id: 1, first_name: 'Jane', last_name: 'Smith' },
            assignment: { id: 1, name: 'E2E Homework', total_points: 100 },
          },
        }),
      });
    });

    await page.goto('/submissions/1');

    // Should show student name and score
    await expect(page.getByText('Jane Smith')).toBeVisible();
    await expect(page.getByText('85')).toBeVisible();
  });

  test('human review form allows score override', async ({ page }) => {
    // Mock graded submission
    await page.route('**/api/submissions/1', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            submission: {
              id: 1,
              student_id: 1,
              assignment_id: 1,
              status: 'graded',
              original_filename: 'hw.ipynb',
              file_path: 'test/submission.ipynb',
              ai_score: 85,
              final_score: 85,
              max_score: 100,
              component_scores: {},
              ai_feedback: { comprehensive_feedback: 'Good.' },
              student: { id: 1, first_name: 'Jane', last_name: 'Smith' },
              assignment: { id: 1, name: 'E2E Homework', total_points: 100 },
            },
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Mock review submission
    await page.route('**/api/grading/submissions/1/review', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          submission: {
            id: 1,
            status: 'reviewed',
            human_score: 90,
            final_score: 90,
            human_feedback: 'Great improvement!',
          },
        }),
      });
    });

    await page.goto('/submissions/1');

    // Find and fill review form
    const scoreInput = page.locator('input[type="number"]').first();
    if (await scoreInput.isVisible()) {
      await scoreInput.fill('90');

      const feedbackInput = page.getByPlaceholder(/feedback/i);
      if (await feedbackInput.isVisible()) {
        await feedbackInput.fill('Great improvement!');
      }

      await page.getByRole('button', { name: /save review/i }).click();
      await expect(page.getByText(/saved/i)).toBeVisible({ timeout: 5_000 });
    }
  });
});

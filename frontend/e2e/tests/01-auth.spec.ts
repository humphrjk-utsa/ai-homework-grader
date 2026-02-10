import { test, expect } from '@playwright/test';
import { TEST_USER, STORAGE_STATE_PATH } from '../fixtures/auth';

// This file runs in the "setup" project — no storageState pre-loaded.

test.describe('Registration', () => {
  test('register new user and land on dashboard', async ({ page }) => {
    await page.goto('/register');

    await expect(page.getByRole('heading', { name: 'Create Account' })).toBeVisible();

    // Fill registration form
    await page.locator('label:has-text("First Name") + input').fill(TEST_USER.first_name);
    await page.locator('label:has-text("Last Name") + input').fill(TEST_USER.last_name);
    await page.locator('label:has-text("Organization") + input').fill(TEST_USER.organization_name);
    await page.locator('label:has-text("Email") + input').fill(TEST_USER.email);
    await page.locator('label:has-text("Password") + input').fill(TEST_USER.password);

    await page.getByRole('button', { name: 'Create Account' }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    // Save auth state for all other test files
    await page.context().storageState({ path: STORAGE_STATE_PATH });
  });

  test('duplicate email shows error', async ({ page }) => {
    await page.goto('/register');

    await page.locator('label:has-text("First Name") + input').fill('Duplicate');
    await page.locator('label:has-text("Last Name") + input').fill('User');
    await page.locator('label:has-text("Organization") + input').fill('Some Org');
    await page.locator('label:has-text("Email") + input').fill(TEST_USER.email);
    await page.locator('label:has-text("Password") + input').fill('password123');

    await page.getByRole('button', { name: 'Create Account' }).click();

    await expect(page.getByText(/already registered/i)).toBeVisible({ timeout: 5_000 });
  });
});

test.describe('Login', () => {
  test('login with valid credentials', async ({ page }) => {
    await page.goto('/login');

    await expect(page.getByRole('heading', { name: 'AI Homework Grader' })).toBeVisible();

    await page.locator('label:has-text("Email") + input').fill(TEST_USER.email);
    await page.locator('label:has-text("Password") + input').fill(TEST_USER.password);

    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page).toHaveURL('/', { timeout: 10_000 });
  });

  test('login with wrong password shows error', async ({ page }) => {
    await page.goto('/login');

    await page.locator('label:has-text("Email") + input').fill(TEST_USER.email);
    await page.locator('label:has-text("Password") + input').fill('wrongpassword');

    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page.getByText(/invalid/i)).toBeVisible({ timeout: 5_000 });
  });

  test('login with nonexistent email shows error', async ({ page }) => {
    await page.goto('/login');

    await page.locator('label:has-text("Email") + input').fill('nobody@test.edu');
    await page.locator('label:has-text("Password") + input').fill('password');

    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page.getByText(/invalid/i)).toBeVisible({ timeout: 5_000 });
  });
});

test.describe('Navigation links on auth pages', () => {
  test('register page has sign in link', async ({ page }) => {
    await page.goto('/register');
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();
  });

  test('login page has register link', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('link', { name: 'Register' })).toBeVisible();
  });
});

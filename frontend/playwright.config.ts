import { defineConfig, devices } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const backendDir = path.resolve(__dirname, '..', 'backend');

export default defineConfig({
  testDir: './e2e/tests',
  globalSetup: './e2e/global-setup.ts',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['html', { open: 'never' }], ['list']],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'setup',
      testMatch: /01-auth\.spec\.ts/,
    },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'e2e/.auth/user.json',
      },
      dependencies: ['setup'],
      testIgnore: /01-auth\.spec\.ts/,
    },
  ],
  webServer: [
    {
      command: `DATABASE_URL=sqlite:////tmp/e2e_test.db flask run --port 5001`,
      url: 'http://localhost:5001/api/health',
      cwd: backendDir,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
      env: {
        FLASK_CONFIG: 'development',
        DATABASE_URL: 'sqlite:////tmp/e2e_test.db',
        FLASK_APP: 'app:create_app',
        STORAGE_ROOT: '/tmp/e2e_test_storage',
      },
    },
    {
      command: 'npm run dev',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 15_000,
    },
  ],
});

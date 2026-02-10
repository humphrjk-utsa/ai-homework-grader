import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEST_RUN_ID = Date.now().toString(36);

export const TEST_USER = {
  email: `e2e-${TEST_RUN_ID}@test.example.com`,
  password: 'TestPass123!',
  first_name: 'E2E',
  last_name: 'Tester',
  organization_name: `Test Org ${TEST_RUN_ID}`,
};

export const STORAGE_STATE_PATH = path.resolve(__dirname, '..', '.auth', 'user.json');

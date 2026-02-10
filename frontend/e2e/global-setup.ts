import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default function globalSetup() {
  // Clean test database
  const dbPath = '/tmp/e2e_test.db';
  if (fs.existsSync(dbPath)) {
    fs.unlinkSync(dbPath);
  }

  // Clean test storage
  const storagePath = '/tmp/e2e_test_storage';
  if (fs.existsSync(storagePath)) {
    fs.rmSync(storagePath, { recursive: true });
  }
  fs.mkdirSync(storagePath, { recursive: true });

  // Create auth state directory
  const authDir = path.resolve(__dirname, '.auth');
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  // Initialize database tables
  const backendDir = path.resolve(__dirname, '..', '..', 'backend');
  execSync(
    `python3 -c "
import os, sys
os.environ['DATABASE_URL'] = 'sqlite:////tmp/e2e_test.db'
os.environ['STORAGE_ROOT'] = '/tmp/e2e_test_storage'
sys.path.insert(0, '${backendDir}')
from app import create_app
from app.extensions import db
app = create_app('development')
with app.app_context():
    db.create_all()
    print('E2E test database initialized')
"`,
    { cwd: backendDir, stdio: 'inherit' },
  );
}

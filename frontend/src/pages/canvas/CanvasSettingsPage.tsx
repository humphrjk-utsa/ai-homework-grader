import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  getCanvasSettings,
  updateCanvasSettings,
  testCanvasConnection,
  listCanvasCourses,
  type CanvasCourse,
} from '../../api/canvas';

export default function CanvasSettingsPage() {
  const [url, setUrl] = useState('');
  const [token, setToken] = useState('');
  const [hasToken, setHasToken] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ connected: boolean; user?: { name: string }; error?: string } | null>(null);
  const [courses, setCourses] = useState<CanvasCourse[]>([]);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    getCanvasSettings().then((s) => {
      setUrl(s.canvas_url);
      setHasToken(s.has_token);
    }).catch(console.error);
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    try {
      const payload: Record<string, string> = { canvas_url: url };
      if (token) payload.canvas_api_token = token;
      await updateCanvasSettings(payload);
      setMessage('Settings saved');
      setHasToken(true);
      if (token) setToken('');
    } catch (err: any) {
      setMessage(err.response?.data?.error || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testCanvasConnection();
      setTestResult(result);
    } catch (err: any) {
      setTestResult({ connected: false, error: err.response?.data?.error || 'Connection failed' });
    } finally {
      setTesting(false);
    }
  };

  const handleLoadCourses = async () => {
    setLoadingCourses(true);
    try {
      const c = await listCanvasCourses();
      setCourses(c);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to load courses');
    } finally {
      setLoadingCourses(false);
    }
  };

  return (
    <div>
      <Link to="/" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
        Back to dashboard
      </Link>

      <h1 className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">Canvas LMS Integration</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Connect to Canvas to sync students, submissions, and push grades back.
      </p>

      {/* Connection Settings */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 max-w-xl">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Connection Settings</h2>

        <div className="mt-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Canvas URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://canvas.university.edu"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              API Token
              {hasToken && <span className="ml-2 text-green-600 dark:text-green-400 text-xs">(saved)</span>}
            </label>
            <input
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder={hasToken ? 'Leave blank to keep current token' : 'Paste your Canvas API token'}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
              Generate under Canvas → Account → Settings → New Access Token
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleSave}
              disabled={saving || !url}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
            <button
              onClick={handleTest}
              disabled={testing || !hasToken}
              className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
            >
              {testing ? 'Testing...' : 'Test Connection'}
            </button>
            {message && <span className="text-sm text-green-600 dark:text-green-400">{message}</span>}
          </div>
        </div>

        {testResult && (
          <div className={`mt-4 p-3 rounded-md text-sm ${
            testResult.connected
              ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
              : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'
          }`}>
            {testResult.connected
              ? `Connected as: ${testResult.user?.name}`
              : `Connection failed: ${testResult.error}`}
          </div>
        )}
      </div>

      {/* Canvas Courses Preview */}
      {hasToken && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Canvas Courses</h2>
            <button
              onClick={handleLoadCourses}
              disabled={loadingCourses}
              className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
            >
              {loadingCourses ? 'Loading...' : 'Load Courses'}
            </button>
          </div>

          {courses.length > 0 && (
            <div className="mt-4 space-y-2">
              {courses.map((c) => (
                <div key={c.canvas_id} className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-600 rounded-md">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{c.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {c.code} - Canvas ID: {c.canvas_id}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
          {courses.length === 0 && !loadingCourses && (
            <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
              Click "Load Courses" to see your Canvas courses.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

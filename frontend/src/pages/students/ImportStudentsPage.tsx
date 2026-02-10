import { useState, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { importStudentsCsv } from '../../api/students';

export default function ImportStudentsPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [result, setResult] = useState<{ imported: number; errors: string[] } | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const res = await importStudentsCsv(Number(courseId), file);
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Import Students</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Upload a CSV file with columns: first_name, last_name, email, canvas_id (optional)
      </p>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        {error && <div className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-3 rounded text-sm">{error}</div>}
        {result && (
          <div className="bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 p-3 rounded text-sm">
            Successfully imported {result.imported} students.
            {result.errors.length > 0 && (
              <ul className="mt-2 list-disc list-inside text-red-600 dark:text-red-400">
                {result.errors.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            )}
          </div>
        )}
        <div>
          <input ref={fileRef} type="file" accept=".csv" required
            className="block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-indigo-50 dark:file:bg-indigo-900/30 file:text-indigo-700 dark:file:text-indigo-400 hover:file:bg-indigo-100 dark:hover:file:bg-indigo-900/50" />
        </div>
        <div className="flex space-x-3">
          <button type="submit" disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:opacity-50">
            {loading ? 'Importing...' : 'Import'}
          </button>
          <button type="button" onClick={() => navigate(`/courses/${courseId}`)}
            className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600">
            Back
          </button>
        </div>
      </form>
    </div>
  );
}
